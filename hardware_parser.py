"""Parse SYSLAB hardware.xml files into structured dataclasses.

The hardware.xml files in ``syslab-master-conf/conf/syslab-XX/`` define
the ground-truth switchboard topology: busbars, bays, breakers,
interlocks, combinations, and instruments.  This module makes that
data accessible as Python objects for building pandapower models and
validating against FTP measurement data.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path


# ── Dataclasses ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class BreakerDef:
    """A circuit breaker from hardware.xml."""

    name: str       # e.g. "Grid_2-A", "319-3A-4A"
    busbar: str     # XML busbar attribute, e.g. "Busbar_A", "Grid"
    bay_name: str   # parent bay name, e.g. "Grid_2", "Cross_A"


@dataclass(frozen=True)
class InterlockDef:
    """Safety interlock between two breakers."""

    name: str
    breaker_a: str
    breaker_b: str


@dataclass(frozen=True)
class CombinationDef:
    """Coordinated switching combination between two interlocks."""

    name: str
    interlock_a: str
    interlock_b: str


@dataclass(frozen=True)
class InstrumentDef:
    """Power measurement instrument (DEIF MIC-2 etc.)."""

    name: str
    position: str


@dataclass
class BayDef:
    """A switchboard bay with its breakers and instruments."""

    name: str
    breakers: list[BreakerDef] = field(default_factory=list)
    interlocks: list[InterlockDef] = field(default_factory=list)
    combinations: list[CombinationDef] = field(default_factory=list)
    instruments: list[InstrumentDef] = field(default_factory=list)


@dataclass
class SwitchboardDef:
    """A switchboard parsed from hardware.xml."""

    name: str                   # e.g. "319-2"
    busbars: list[str] = field(default_factory=list)
    bays: list[BayDef] = field(default_factory=list)
    rated_voltage_kv: float = 0.4
    location: str = ""
    latitude: float = 0.0
    longitude: float = 0.0

    @property
    def name_underscore(self) -> str:
        """Switchboard name with dashes replaced by underscores."""
        return self.name.replace("-", "_")

    def all_breakers(self) -> list[BreakerDef]:
        """Return all breakers across all bays."""
        return [b for bay in self.bays for b in bay.breakers]

    def bay_by_name(self, name: str) -> BayDef | None:
        for bay in self.bays:
            if bay.name == name:
                return bay
        return None


@dataclass
class SubstationConfig:
    """All switchboards from one hardware.xml file."""

    device_name: str
    node_id: str                # directory name, e.g. "syslab-11"
    switchboards: list[SwitchboardDef] = field(default_factory=list)


# ── Parsing ──────────────────────────────────────────────────────────


def _parse_bay(bay_el: ET.Element) -> BayDef:
    """Parse a <bay> element into a BayDef."""
    bay_name = bay_el.attrib["name"]
    bay = BayDef(name=bay_name)

    for child in bay_el:
        tag = child.tag
        if tag == "breaker":
            bay.breakers.append(BreakerDef(
                name=child.attrib["name"],
                busbar=child.attrib["busbar"],
                bay_name=bay_name,
            ))
        elif tag == "interlock":
            bay.interlocks.append(InterlockDef(
                name=child.attrib["name"],
                breaker_a=child.attrib["breakerA"],
                breaker_b=child.attrib["breakerB"],
            ))
        elif tag == "combination":
            bay.combinations.append(CombinationDef(
                name=child.attrib["name"],
                interlock_a=child.attrib["interlockA"],
                interlock_b=child.attrib["interlockB"],
            ))
        elif tag == "instrument":
            bay.instruments.append(InstrumentDef(
                name=child.attrib["name"],
                position=child.attrib.get("position", ""),
            ))

    return bay


def _parse_switchboard(sw_el: ET.Element) -> SwitchboardDef:
    """Parse a <switchboard> element."""
    sw = SwitchboardDef(
        name=sw_el.attrib["name"],
        rated_voltage_kv=float(sw_el.attrib.get("ratedU", "400")) / 1000.0,
        location=sw_el.attrib.get("location", ""),
        latitude=float(sw_el.attrib.get("latitude", "0")),
        longitude=float(sw_el.attrib.get("longitude", "0")),
    )

    for child in sw_el:
        if child.tag == "busbar":
            sw.busbars.append(child.attrib["name"])
        elif child.tag == "bay":
            sw.bays.append(_parse_bay(child))

    return sw


def parse_hardware_xml(path: Path | str, node_id: str = "") -> SubstationConfig:
    """Parse a hardware.xml file into a SubstationConfig.

    Parameters
    ----------
    path : Path or str
        Path to the hardware.xml file.
    node_id : str
        The syslab node ID (e.g. "syslab-11").  If empty, inferred
        from the parent directory name.
    """
    path = Path(path)
    if not node_id:
        node_id = path.parent.name

    tree = ET.parse(path)  # noqa: S314 — trusted local config files
    root = tree.getroot()

    config = SubstationConfig(
        device_name=root.attrib.get("name", ""),
        node_id=node_id,
    )

    for sw_el in root.iter("switchboard"):
        config.switchboards.append(_parse_switchboard(sw_el))

    return config


# ── Grid-level loading ───────────────────────────────────────────────

# Mapping: syslab FTP node → conf directory (only grid-relevant nodes)
GRID_NODES: dict[str, str] = {
    "syslab-01": "syslab-01",   # 319-2
    "syslab-09": "syslab-09",   # 715-2
    "syslab-11": "syslab-11",   # 117-2, 117-4, 117-5
    "syslab-26": "syslab-26",   # 117-6
    "syslab-29": "syslab-29",   # 716-2
    "syslab-50": "syslab-50",   # 330-12
    "syslab-51": "syslab-51",   # 330-13
    "syslab-52": "syslab-52",   # 319-3, 319-4
    "syslab-53": "syslab-53",   # 310-2
}


def load_grid_switchboards(
    conf_dir: Path | str,
    nodes: dict[str, str] | None = None,
) -> dict[str, SwitchboardDef]:
    """Load all switchboards that form the SYSLAB grid.

    Parameters
    ----------
    conf_dir : Path or str
        Path to the ``syslab-master-conf/conf/`` directory.
    nodes : dict or None
        Node ID → directory mapping.  Defaults to :data:`GRID_NODES`.

    Returns
    -------
    dict[str, SwitchboardDef]
        Mapping from switchboard name (e.g. ``"319-2"``) to its definition.
    """
    conf_dir = Path(conf_dir)
    if nodes is None:
        nodes = GRID_NODES

    switchboards: dict[str, SwitchboardDef] = {}

    for node_id, dir_name in nodes.items():
        hw_path = conf_dir / dir_name / "hardware.xml"
        if not hw_path.exists():
            continue
        config = parse_hardware_xml(hw_path, node_id)
        for sw in config.switchboards:
            switchboards[sw.name] = sw

    return switchboards
