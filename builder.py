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
from dataclasses import dataclass, field
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
    logged: bool = True


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
                SwitchDefault(
                    name=s["name"],
                    default_closed=s["default_closed"],
                    logged=s.get("logged", True),
                )
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


# -- Socket ports (CEE bays) ------------------------------------------

#: Bays whose name starts with this prefix are CEE sockets where mobile
#: equipment can be plugged in (syslab_data ADR-0004).
SOCKET_BAY_PREFIX = "CEE"


@dataclass(frozen=True)
class SocketPortDef:
    """A CEE socket bay: one-terminal plug point behind a bay breaker."""
    name: str                   # e.g. "319-2 CEEx2"
    switchboard: str            # e.g. "319-2"
    bay: str                    # e.g. "CEEx2"
    bus: str                    # PP bay bus name, e.g. "319-2_CEEx2"
    switches: list[str]         # BRK names of the bay breakers
    description: str
    #: busbar letter -> measurement name ("A": "CEEx2.A"); a bay with a single
    #: meter stores it under "*".  Each meter is a separate plug (mobile device), like
    #: the meters of cable bays are separate parallel cables.  Empty when not
    #: declared.
    meters: dict[str, str] = field(default_factory=dict)


def load_socket_meters(path: Path | None = None) -> dict[str, dict[str, str]]:
    """Load ``socket_meters.yaml``: ``{port name: {busbar letter or "*": meter}}``.

    A socket is one plug behind two busbar breakers; some have one meter per
    busbar feed (``A``/``B``), the others one meter (``*``).
    """
    if path is None:
        path = _DATA_DIR / "socket_meters.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    out: dict[str, dict[str, str]] = {}
    for e in data.get("sockets") or []:
        port = e["port"]
        if port in out:
            raise ValueError(f"Duplicate socket port: {port!r}")
        if ("meters" in e) == ("meter" in e):
            raise ValueError(f"{port}: give either 'meters' or 'meter'")
        out[port] = {"*": e["meter"]} if "meter" in e else dict(e["meters"])
    return out


def derive_socket_ports(
    switchboards: dict[str, SwitchboardDef],
    meters: dict[str, dict[str, str]] | None = None,
) -> list[SocketPortDef]:
    """Derive socket ports from ``hardware.xml`` bays named ``CEE*``.

    Only bays with at least one breaker are included (bays without a
    breaker are not modeled as buses).  Result is sorted by switchboard
    and bay name.  ``meters`` (see :func:`load_socket_meters`) is attached
    by port name; busbar letters must match the bay's breakers.
    """
    meters = meters or {}
    ports: list[SocketPortDef] = []
    for sw_name in sorted(switchboards):
        sw = switchboards[sw_name]
        for bay in sorted(sw.bays, key=lambda b: b.name):
            if not bay.name.startswith(SOCKET_BAY_PREFIX) or not bay.breakers:
                continue
            bay_bus = _bay_bus_name(sw.name, bay.name)
            switches = [
                _derive_brk_name(_bb_bus_name(sw.name, brk.busbar), bay_bus)
                for brk in bay.breakers
            ]
            name = f"{sw.name} {bay.name}"
            port_meters = meters.get(name, {})
            letters = {busbar_suffix(brk.busbar) for brk in bay.breakers}
            bad = set(port_meters) - letters - {"*"}
            if bad:
                raise ValueError(f"{name}: meters for busbar {sorted(bad)} but breakers on {sorted(letters)}")
            ports.append(SocketPortDef(
                name=name,
                switchboard=sw.name,
                bay=bay.name,
                bus=bay_bus,
                switches=[s for s in switches if s],
                description=(
                    f"CEE socket {bay.name} on {sw.name}; plug point for "
                    "mobile equipment or a cable to another port."
                ),
                meters=dict(port_meters),
            ))
    return ports


# -- Equipment catalog ------------------------------------------------

_EQUIPMENT_KINDS = {"load": 1, "impedance": 2, "converter": 2}
_PORT_KINDS = {"socket", "inline"}


def load_equipment_catalog(path: Path | None = None) -> dict:
    """Load and validate the flexibly deployed equipment catalog.

    Returns ``{"equipment": [...], "cable_types": {...}}`` where
    ``cable_types`` is the content of ``cable_types.yaml`` (standard cables
    that can be used for port-to-port connections).
    """
    if path is None:
        path = _DATA_DIR / "equipment_catalog.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    equipment = data.get("equipment") or []
    seen: set[str] = set()
    for e in equipment:
        eid = e["id"]
        if eid in seen:
            raise ValueError(f"Duplicate equipment id: {eid!r}")
        seen.add(eid)
        kind = e["kind"]
        if kind not in _EQUIPMENT_KINDS:
            raise ValueError(f"{eid}: unknown kind {kind!r}")
        if e["terminals"] != _EQUIPMENT_KINDS[kind]:
            raise ValueError(
                f"{eid}: kind {kind!r} needs {_EQUIPMENT_KINDS[kind]} terminal(s)"
            )
        bad = set(e["ports"]) - _PORT_KINDS
        if bad or not e["ports"]:
            raise ValueError(f"{eid}: invalid ports {e['ports']!r}")

    return {"equipment": equipment, "cable_types": load_cable_types()}


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

    # Phase 5: Assign bus geodata for pandapower plotting
    _assign_bus_geodata(net)

    return net


# ── Bus geodata for PP-native plotting ───────────────────────────────
#
# PP simple_plot draws switches as small rectangles on edges, so buses
# need generous spacing.  Bays are arranged in a grid pattern (multiple
# columns) below their busbar rather than a single vertical stack.
#
# Grid positions mirror syslab_data.visualization.topology._SB_GRID_POS
# but use PP-style hyphen names (e.g. "319-2").

_SB_GRID_POS_PP: dict[str, tuple[int, int]] = {
    # Centre
    "319-3": (-1, -1),    "319-4": (1, -1),
    # Bottom row
    "715-2": (-5, -2),    "117-2": (-2, -3),   "117-5": (0, -3),
    "117-4": (1, -3),     "117-6": (2, -3),    "319-2": (5, -2),
    # Top row
    "716-2": (-5, 3),     "330-13": (-2, 3),   "330-12": (1, 4),
    "310-2": (5, 2),
}

_GEO_X_SCALE  = 40.0   # world-units per grid column
_GEO_Y_SCALE  = 55.0   # world-units per grid row
_GEO_BB_DX    =  8.0   # horizontal spacing between busbars
_GEO_BAY_DX   =  6.0   # horizontal spacing between bay columns
_GEO_BAY_DY   =  6.0   # vertical spacing between bay rows
_GEO_BAY_TOP  = 10.0   # gap between busbar row and first bay row
_GEO_BAY_COLS =  4      # max columns in bay grid


def _sb_of_pp_bus(name: str) -> str | None:
    """Extract switchboard prefix from a PP bus name.

    ``"319-2_Busbar-A"`` → ``"319-2"``
    ``"330-13_Cable_K1A"`` → ``"330-13"``
    """
    m = re.match(r"^(\d+-\d+)_", name)
    return m.group(1) if m else None


def _assign_bus_geodata(net: pp.pandapowerNet) -> None:
    """Set ``bus.geo`` for every bus using a switchboard-clustered layout.

    Busbars are placed in a horizontal row at the top of each
    switchboard cluster.  Bays fan out in a grid (up to
    ``_GEO_BAY_COLS`` columns) below their assigned busbar.

    After this, ``pandapower.plotting.simple_plot(net)`` renders the
    SYSLAB grid with the recognisable physical layout.
    """
    from collections import defaultdict
    import math

    # ---- Classify buses ------------------------------------------------
    busbars: dict[str, list[tuple[int, str]]] = defaultdict(list)
    bays:    dict[str, list[tuple[int, str]]] = defaultdict(list)

    for idx in net.bus.index:
        name = net.bus.at[idx, "name"]
        sb = _sb_of_pp_bus(name)
        if sb is None:
            continue
        if "_Busbar-" in name:
            busbars[sb].append((idx, name))
        else:
            bays[sb].append((idx, name))

    # ---- SB anchor positions -------------------------------------------
    all_sbs = set(busbars) | set(bays)
    fallback_col = max((c for c, _ in _SB_GRID_POS_PP.values()), default=0) + 2
    sb_anchor: dict[str, tuple[float, float]] = {}
    for sb in sorted(all_sbs):
        if sb in _SB_GRID_POS_PP:
            col, row = _SB_GRID_POS_PP[sb]
        else:
            col, row = fallback_col, 0
            fallback_col += 2
        sb_anchor[sb] = (col * _GEO_X_SCALE, row * _GEO_Y_SCALE)

    # ---- Place busbars in a horizontal row -----------------------------
    def _is_special(name: str) -> bool:
        suffix = name.split("_Busbar-")[-1] if "_Busbar-" in name else ""
        return suffix not in {"A", "B", "C"}

    busbar_xy: dict[int, tuple[float, float]] = {}

    for sb, bb_list in busbars.items():
        ax_x, ax_y = sb_anchor[sb]
        # Sort: special busbars (Grid, Supply, …) first, then regular A/B/C
        special = sorted(
            [(i, n) for i, n in bb_list if _is_special(n)], key=lambda t: t[1],
        )
        regular = sorted(
            [(i, n) for i, n in bb_list if not _is_special(n)], key=lambda t: t[1],
        )
        all_ordered = special + regular
        n = len(all_ordered)
        # Centre the row horizontally on the anchor
        x_start = ax_x - (n - 1) / 2.0 * _GEO_BB_DX
        for i, (idx, _name) in enumerate(all_ordered):
            busbar_xy[idx] = (x_start + i * _GEO_BB_DX, ax_y)

    # ---- Bay → busbar assignment via switch table ----------------------
    bay_to_bb: dict[int, int] = {}
    for sw_idx in net.switch.index:
        if net.switch.at[sw_idx, "et"] == "b":
            bus = int(net.switch.at[sw_idx, "bus"])
            elem = int(net.switch.at[sw_idx, "element"])
            if bus in busbar_xy and elem not in busbar_xy:
                bay_to_bb.setdefault(elem, bus)
            elif elem in busbar_xy and bus not in busbar_xy:
                bay_to_bb.setdefault(bus, elem)

    # ---- Place bays in a grid below their busbar -----------------------
    bay_counts: dict[int, int] = defaultdict(int)  # per-busbar counter
    bay_xy: dict[int, tuple[float, float]] = {}

    for sb, bay_list in bays.items():
        for idx, _name in sorted(bay_list, key=lambda t: t[1]):
            bb_idx = bay_to_bb.get(idx)
            if bb_idx is not None and bb_idx in busbar_xy:
                bx, by = busbar_xy[bb_idx]
                j = bay_counts[bb_idx]
                col = j % _GEO_BAY_COLS
                row = j // _GEO_BAY_COLS
                # Centre the grid columns under the busbar
                x = bx + (col - (_GEO_BAY_COLS - 1) / 2.0) * _GEO_BAY_DX
                y = by - _GEO_BAY_TOP - row * _GEO_BAY_DY
                bay_xy[idx] = (x, y)
                bay_counts[bb_idx] += 1
            else:
                # No switch connection — centre below all SB busbars
                sb_bbs = [
                    busbar_xy[i] for i, _ in busbars.get(sb, [])
                    if i in busbar_xy
                ]
                if sb_bbs:
                    mx = sum(p[0] for p in sb_bbs) / len(sb_bbs)
                    my = min(p[1] for p in sb_bbs) - _GEO_BAY_TOP
                else:
                    mx, my = sb_anchor.get(sb, (0.0, 0.0))
                    my -= _GEO_BAY_TOP
                bay_xy[idx] = (mx, my)

    # ---- Write GeoJSON to net.bus.geo ----------------------------------
    for idx, (x, y) in {**busbar_xy, **bay_xy}.items():
        net.bus.at[idx, "geo"] = json.dumps(
            {"coordinates": [x, y], "type": "Point"}
        )


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


def portable_source_path(path: Path | str, base: Path | str | None = None) -> str:
    """Return *path* relative to *base* (default: cwd) in POSIX form.

    Used for provenance fields in published files so that local absolute
    paths (user names, drive letters) do not leak into the public
    ``syslab_pandapower`` repo.  If *path* is not below *base*, only its
    last two components are kept (e.g. ``"syslab-master-conf/conf"``).
    """
    path = Path(path).resolve()
    base = Path(base).resolve() if base is not None else Path.cwd().resolve()
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return "/".join(path.parts[-2:])


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
