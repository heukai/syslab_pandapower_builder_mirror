"""Core builder: reads YAML data + XML hardware → produces pandapower model.

This module loads the curated YAML data files (cable types, cables,
non-breaker connections) and the hardware.xml switchboard definitions,
then assembles a pandapower network.

It also derives the BRK-name-to-switch-index mapping table so that
downstream consumers (syslab_data) can map FTP CSV breaker columns to
pandapower switch indices without reverse-engineering bus names at runtime.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import pandapower as pp
import yaml

from .hardware_parser import SwitchboardDef, load_grid_switchboards


# ── Data loading ─────────────────────────────────────────────────────

_DATA_DIR = Path(__file__).resolve().parent / "data"


@dataclass(frozen=True)
class CableDef:
    """A cable or internal connection between two bus endpoints."""
    name: str
    bus1: str
    bus2: str
    length_km: float
    cable_type: str


@dataclass(frozen=True)
class ConverterDef:
    """A back-to-back converter that isolates primary and secondary sides.

    Unlike cables, converters do not create a direct electrical connection.
    The secondary side can operate as grid-forming (ext_grid) or PQ
    (sgen), depending on the island configuration.
    """
    name: str
    primary_bus: str
    secondary_bus: str


def load_cable_types(path: Path | None = None) -> dict[str, dict]:
    """Load cable type electrical parameters from YAML."""
    if path is None:
        path = _DATA_DIR / "cable_types.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["cable_types"]


def load_cables(path: Path | None = None) -> list[CableDef]:
    """Load inter-substation cable definitions from YAML."""
    if path is None:
        path = _DATA_DIR / "cables.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [
        CableDef(
            name=c["name"], bus1=c["bus1"], bus2=c["bus2"],
            length_km=c["length_km"], cable_type=c["cable_type"],
        )
        for c in data["cables"]
    ]


def load_non_breaker_connections(path: Path | None = None) -> list[CableDef]:
    """Load non-breaker internal connections from YAML."""
    if path is None:
        path = _DATA_DIR / "non_breaker_connections.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [
        CableDef(
            name=c["name"], bus1=c["bus1"], bus2=c["bus2"],
            length_km=c["length_km"], cable_type=c["cable_type"],
        )
        for c in (data["connections"] or [])
    ]


def load_converter_connections(path: Path | None = None) -> list[ConverterDef]:
    """Load back-to-back converter definitions from YAML.

    These converters electrically isolate their two sides and are NOT
    added as lines in the pandapower model.  They are used by the
    topology layer to determine grid-forming / PQ mode at simulation time.
    """
    if path is None:
        path = _DATA_DIR / "converter_connections.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [
        ConverterDef(
            name=c["name"],
            primary_bus=c["primary_bus"],
            secondary_bus=c["secondary_bus"],
        )
        for c in (data["converters"] or [])
    ]


# ── Breaker groups & inline ports ────────────────────────────────────


@dataclass(frozen=True)
class SwitchDefault:
    """A switch within a breaker group with its default state."""
    name: str
    default_closed: bool


@dataclass(frozen=True)
class InterlockDef:
    """A mutual-exclusion constraint on a set of switches."""
    group: str
    max_closed: int
    members: list[str]


@dataclass(frozen=True)
class BreakerGroupDef:
    """A named group of related breakers with documentation and constraints."""
    name: str
    type: str
    description: str
    switches: list[SwitchDefault]
    interlocks: list[InterlockDef]


@dataclass(frozen=True)
class InlinePortMode:
    """One available mode for an inline port."""
    name: str
    description: str
    default: bool


@dataclass(frozen=True)
class InlinePortDef:
    """A cable plug point where mobile equipment can be inserted."""
    name: str
    cable: str
    location: str
    description: str
    modes: list[InlinePortMode]


def load_breaker_groups(
    path: Path | None = None,
) -> tuple[list[BreakerGroupDef], list[InlinePortDef]]:
    """Load breaker group and inline port definitions from YAML.

    Returns
    -------
    (breaker_groups, inline_ports)
    """
    if path is None:
        path = _DATA_DIR / "breaker_groups.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    groups = [
        BreakerGroupDef(
            name=g["name"],
            type=g["type"],
            description=g["description"],
            switches=[
                SwitchDefault(name=s["name"], default_closed=s["default_closed"])
                for s in g.get("switches", [])
            ],
            interlocks=[
                InterlockDef(
                    group=i["group"],
                    max_closed=i["max_closed"],
                    members=list(i["members"]),
                )
                for i in g.get("interlocks", [])
            ],
        )
        for g in (data.get("breaker_groups") or [])
    ]

    ports = [
        InlinePortDef(
            name=p["name"],
            cable=p["cable"],
            location=p["location"],
            description=p["description"],
            modes=[
                InlinePortMode(
                    name=m["name"],
                    description=m.get("description", ""),
                    default=m.get("default", False),
                )
                for m in p.get("modes", [])
            ],
        )
        for p in (data.get("inline_ports") or [])
    ]

    return groups, ports


# ── PP naming helpers ────────────────────────────────────────────────


def busbar_suffix(xml_busbar: str) -> str:
    """``"Busbar_A"`` → ``"A"``, ``"Grid"`` → ``"Grid"``."""
    if xml_busbar.startswith("Busbar_"):
        return xml_busbar[7:]
    return xml_busbar


def _bb_bus_name(sw_name: str, xml_busbar: str) -> str:
    return f"{sw_name}_Busbar-{busbar_suffix(xml_busbar)}"


def _bay_bus_name(sw_name: str, bay_name: str) -> str:
    return f"{sw_name}_{bay_name}"


# Cross-switch breaker: "319-3A-4A" → (src_sw, src_bus, dst_sw, dst_bus)
_CROSS_BRK_RE = re.compile(r"^(\d+)-(\d+)([A-Z])-(\d+)([A-Z])$")


def _parse_cross_breaker(brk_name: str) -> tuple[str, str, str, str] | None:
    m = _CROSS_BRK_RE.match(brk_name)
    if not m:
        return None
    building, sec1, bus1, sec2, bus2 = m.groups()
    return f"{building}-{sec1}", bus1, f"{building}-{sec2}", bus2


def _is_cross_bay(bay_name: str) -> bool:
    return bay_name.startswith("Cross_")


def _get_bus_idx(net: pp.pandapowerNet, name: str) -> int:
    matches = net.bus.index[net.bus["name"] == name].tolist()
    if len(matches) != 1:
        raise ValueError(
            f"Bus '{name}': found {len(matches)} matches (expected 1)"
        )
    return matches[0]


# ── BRK name derivation ─────────────────────────────────────────────
_BUSBAR_RE = re.compile(r"^(.+)_Busbar-(.+)$")


def _derive_brk_name(bus_name: str, element_name: str) -> str | None:
    """Derive BRK name from two PP bus names connected by a switch.

    Convention: ``{sb_underscore}_BRK_{bay}_Busbar_{busbar_suffix}``
    Crossbar:   ``319_4_BRK_Cross_{src_letter}_Busbar_{dst_letter}``

    Names use the full ``_Busbar_`` form to match FTP CSV column names
    (e.g. ``BRK_Battery_Busbar_A``), avoiding the need for a translation layer.
    """
    # Check which of the two bus names are busbars (match "XXX_Busbar-Y")
    bb1 = _BUSBAR_RE.match(bus_name)
    bb2 = _BUSBAR_RE.match(element_name)

    is_bb1, is_bb2 = bool(bb1), bool(bb2)

    # Case 1: Both sides are busbars → crossbar breaker (busbar-to-busbar)
    # Only the 319-3 ↔ 319-4 crossbar exists in the SYSLAB grid
    if is_bb1 and is_bb2:
        sb1 = bb1.group(1).replace("-", "_")  # e.g. "319-3" → "319_3"
        sb2 = bb2.group(1).replace("-", "_")
        suffix1, suffix2 = bb1.group(2), bb2.group(2)  # busbar letters, e.g. "A", "B"
        if sb1 != sb2 and "319_3" in (sb1, sb2) and "319_4" in (sb1, sb2):
            # src = 319-3 side, dst = 319-4 side
            src_letter = suffix1 if sb1 == "319_3" else suffix2
            dst_letter = suffix2 if sb2 == "319_4" else suffix1
            return f"319_4_BRK_Cross_{src_letter}_Busbar_{dst_letter}"
        # Two busbars on the same switchboard → not a named breaker
        return None

    # Case 2: bus_name is a busbar, element_name is a bay node
    # e.g. bus="319-2_Busbar-A", element="319-2_Diesel" → "319_2_BRK_Diesel_Busbar_A"
    if is_bb1 and not is_bb2:
        sb = bb1.group(1).replace("-", "_")   # switchboard: "319-2" → "319_2"
        suffix = bb1.group(2)                  # busbar letter: "A"
        bay = element_name.split("_", 1)[1] if "_" in element_name else ""  # bay name after "319-2_"
        return f"{sb}_BRK_{bay}_Busbar_{suffix}"

    # Case 3: bus_name is a bay node, element_name is a busbar (reversed order)
    # Same logic, just swapped sides
    if not is_bb1 and is_bb2:
        sb = bb2.group(1).replace("-", "_")
        suffix = bb2.group(2)
        bay = bus_name.split("_", 1)[1] if "_" in bus_name else ""
        return f"{sb}_BRK_{bay}_Busbar_{suffix}"

    # Case 4: Neither side is a busbar → cannot derive a BRK name
    return None




# ── Network builder ──────────────────────────────────────────────────


def build_pp_network(
    switchboards: dict[str, SwitchboardDef],
    cables: list[CableDef],
    cable_types: dict[str, dict],
    internal_connections: list[CableDef],
) -> pp.pandapowerNet:
    """Build a pandapower network from parsed switchboard definitions
    and curated cable/connection data."""

    net = pp.create_empty_network()

    # Register cable types
    for type_name, params in cable_types.items():
        pp.create_std_type(net, params, name=type_name, element="line")

    # Phase 1: Create all busbar buses
    busbar_buses: dict[str, int] = {}
    for sw in switchboards.values():
        for bb in sw.busbars:
            bus_name = _bb_bus_name(sw.name, bb)
            idx = pp.create_bus(
                net, name=bus_name, vn_kv=sw.rated_voltage_kv, type="b",
            )
            busbar_buses[bus_name] = idx

    # Phase 2: Create bay nodes and switches
    for sw in switchboards.values():
        for bay in sw.bays:
            if _is_cross_bay(bay.name):
                for brk in bay.breakers:
                    cross = _parse_cross_breaker(brk.name)
                    if cross is None:
                        continue
                    src_sw, src_bus, _dst_sw, _dst_bus = cross
                    src_bb_name = f"{src_sw}_Busbar-{src_bus}"
                    dst_bb_name = _bb_bus_name(sw.name, brk.busbar)
                    brk_name = _derive_brk_name(src_bb_name, dst_bb_name)
                    pp.create_switch(
                        net,
                        busbar_buses[src_bb_name],
                        busbar_buses[dst_bb_name],
                        et="b", type="CB", closed=False,
                        name=brk_name,
                    )
            elif not bay.breakers:
                continue
            else:
                bay_name = _bay_bus_name(sw.name, bay.name)
                bay_idx = pp.create_bus(
                    net, name=bay_name, vn_kv=sw.rated_voltage_kv, type="n",
                )
                for brk in bay.breakers:
                    bb_name = _bb_bus_name(sw.name, brk.busbar)
                    brk_name = _derive_brk_name(bb_name, bay_name)
                    pp.create_switch(
                        net,
                        busbar_buses[bb_name],
                        bay_idx,
                        et="b", type="CB", closed=False,
                        name=brk_name,
                    )

    # Phase 3: Create inter-substation cable lines
    for cable in cables:
        bus1_idx = _get_bus_idx(net, cable.bus1)
        bus2_idx = _get_bus_idx(net, cable.bus2)
        pp.create_line(
            net, bus1_idx, bus2_idx,
            length_km=cable.length_km,
            std_type=cable.cable_type,
            name=cable.name,
        )

    # Phase 4: Create internal non-breaker connections
    for link in internal_connections:
        bus1_idx = _get_bus_idx(net, link.bus1)
        bus2_idx = _get_bus_idx(net, link.bus2)
        pp.create_line(
            net, bus1_idx, bus2_idx,
            length_km=link.length_km,
            std_type=link.cable_type,
            name=link.name,
        )

    return net


# ── Switch name map generation ───────────────────────────────────────


def build_switch_name_map(net: pp.pandapowerNet) -> dict[str, int]:
    """Build BRK-name → switch-index mapping from the switch table.

    Reads the ``name`` column set at switch creation time.
    The result is serialized to ``switch_name_map.json``.
    """
    mapping: dict[str, int] = {}
    for idx in net.switch.index:
        name = net.switch.at[idx, "name"]
        if name is not None and name != "":
            mapping[name] = int(idx)
    return mapping


# ── Convenience entry-point ──────────────────────────────────────────


def create_syslab_model(
    conf_dir: Path | str | None = None,
) -> tuple[pp.pandapowerNet, dict[str, int], list[ConverterDef]]:
    """Build the complete SYSLAB pandapower model and switch name map.

    Returns
    -------
    net : pandapowerNet
        The assembled network.
    switch_map : dict[str, int]
        BRK name → pandapower switch index mapping.
    converters : list[ConverterDef]
        Back-to-back converter definitions (not modeled as lines).
    """
    if conf_dir is None:
        conf_dir = (
            Path(__file__).resolve().parents[1] / "syslab-master-conf" / "conf"
        )

    switchboards = load_grid_switchboards(conf_dir)
    cable_types = load_cable_types()
    cables = load_cables()
    internal_connections = load_non_breaker_connections()
    converters = load_converter_connections()

    net = build_pp_network(switchboards, cables, cable_types, internal_connections)
    switch_map = build_switch_name_map(net)

    return net, switch_map, converters


# ── Serialization helpers ────────────────────────────────────────────


def save_switch_name_map(switch_map: dict[str, int], path: Path | str) -> None:
    """Write switch name map to JSON."""
    path = Path(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(switch_map, f, indent=2, sort_keys=True)


def save_model_version(
    output_dir: Path | str,
    *,
    valid_from: str,
    valid_to: str | None = None,
    hardware_xml_source: str = "",
    notes: str = "",
) -> None:
    """Write model_version.json with validity and provenance metadata."""
    import datetime

    from . import __version__ as builder_version

    version_info = {
        "model_build_date": datetime.date.today().isoformat(),
        "builder_version": builder_version,
        "valid_from": valid_from,
        "valid_to": valid_to,
        "hardware_xml_source": hardware_xml_source,
        "notes": notes,
    }
    path = Path(output_dir) / "model_version.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(version_info, f, indent=2)
