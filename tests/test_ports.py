"""Tests for socket ports (CEE bays) and the equipment catalog (ADR-0004)."""

import json
from pathlib import Path

import pytest
import yaml

from syslab_pandapower_builder.builder import (
    SocketPortDef,
    create_syslab_model,
    derive_bay_meters,
    derive_socket_ports,
    load_equipment_catalog,
    portable_source_path,
)
from syslab_pandapower_builder.hardware_parser import BayDef, BreakerDef, InstrumentDef, InterlockDef, SwitchboardDef

_CONF_DIR = Path(__file__).resolve().parents[2] / "syslab-master-conf" / "conf"


def _sb(name: str, bays: list[BayDef]) -> SwitchboardDef:
    return SwitchboardDef(name=name, busbars=["Busbar_A", "Busbar_B"], bays=bays)


def _bay(name: str, with_breakers: bool = True, interlock: bool = True) -> BayDef:
    brks = (
        [BreakerDef(f"{name}-A", "Busbar_A", name), BreakerDef(f"{name}-B", "Busbar_B", name)]
        if with_breakers else []
    )
    ils = [InterlockDef(f"{name}-IL", f"{name}-A", f"{name}-B")] if brks and interlock else []
    return BayDef(name=name, breakers=brks, interlocks=ils)


class TestDeriveBayMeters:
    """Auto-update ticket 09: every metered bay carries its hardware.xml instrument names."""

    @staticmethod
    def _metered(name: str, *meters: str, with_breakers: bool = True) -> BayDef:
        bay = _bay(name, with_breakers=with_breakers)
        bay.instruments = [InstrumentDef(m, "") for m in meters]
        return bay

    def test_meter_name_differs_from_bay(self):
        (m,) = derive_bay_meters({"117-4": _sb("117-4", [self._metered("Grid", "Grid_4")])})
        assert m == {"switchboard": "117-4", "bay": "Grid", "bus": "117-4_Grid", "meters": ["Grid_4"]}

    def test_only_bays_with_breakers_and_instruments_no_cee(self):
        sbs = {"319-2": _sb("319-2", [
            self._metered("PV", "PV"), _bay("Aircon"), self._metered("Spare", "Spare", with_breakers=False),
            self._metered("CEEx2", "CEEx2.A", "CEEx2.B"),
        ])}
        assert [(m["bay"], m["meters"]) for m in derive_bay_meters(sbs)] == [("PV", ["PV"])]

    def test_several_instruments_kept_in_order_and_sorted(self):
        sbs = {
            "716-2": _sb("716-2", [self._metered("Grid", "Grid")]),
            "117-2": _sb("117-2", [self._metered("Cable_C1", "Cable_C1B", "Cable_C1A")]),
        }
        assert [(m["switchboard"], m["meters"]) for m in derive_bay_meters(sbs)] == [
            ("117-2", ["Cable_C1B", "Cable_C1A"]), ("716-2", ["Grid"])]


class TestDeriveSocketPorts:
    def test_only_cee_bays_with_breakers(self):
        sbs = {"319-2": _sb("319-2", [_bay("CEE"), _bay("CEEx1"), _bay("PV"), _bay("CEE_3", False)])}
        ports = derive_socket_ports(sbs)
        assert [p.name for p in ports] == ["319-2 CEE", "319-2 CEEx1"]

    def test_fields_and_brk_names(self):
        (p,) = derive_socket_ports({"319-2": _sb("319-2", [_bay("CEE")])})
        assert isinstance(p, SocketPortDef)
        assert p.switchboard == "319-2"
        assert p.bay == "CEE"
        assert p.bus == "319-2_CEE"
        assert p.busbar == ""
        assert p.switches == ["319_2_BRK_CEE_Busbar_A", "319_2_BRK_CEE_Busbar_B"]

    def test_bay_without_interlock_has_one_socket_per_busbar(self):
        a, b = derive_socket_ports({"319-2": _sb("319-2", [_bay("CEEx2", interlock=False)])})
        assert (a.name, a.busbar, a.bus) == ("319-2 CEEx2.A", "A", "319-2_CEEx2.A")
        assert (b.name, b.busbar, b.bus) == ("319-2 CEEx2.B", "B", "319-2_CEEx2.B")
        assert a.switches == ["319_2_BRK_CEEx2_Busbar_A"]
        assert b.switches == ["319_2_BRK_CEEx2_Busbar_B"]

    def test_sorted_by_switchboard_then_bay(self):
        sbs = {
            "716-2": _sb("716-2", [_bay("CEE")]),
            "117-5": _sb("117-5", [_bay("CEEx1_2"), _bay("CEEx1_1")]),
        }
        assert [p.name for p in derive_socket_ports(sbs)] == [
            "117-5 CEEx1_1", "117-5 CEEx1_2", "716-2 CEE",
        ]


@pytest.mark.skipif(not _CONF_DIR.exists(), reason="syslab-master-conf not available")
class TestSocketPortsAgainstModel:
    @pytest.fixture(scope="class")
    def model(self):
        net, switch_map, _ = create_syslab_model(_CONF_DIR)
        from syslab_pandapower_builder.hardware_parser import load_grid_switchboards
        ports = derive_socket_ports(load_grid_switchboards(_CONF_DIR))
        return net, switch_map, ports

    def test_all_cee_bays_found(self, model):
        _, _, ports = model
        assert {p.name for p in ports} >= {"319-2 CEE", "319-2 CEEx2.A", "319-2 CEEx2.B"}
        assert len(ports) == 10

    def test_bus_exists_in_network(self, model):
        net, _, ports = model
        names = set(net.bus["name"])
        for p in ports:
            assert p.bus in names, p.name

    def test_switches_in_switch_map(self, model):
        _, switch_map, ports = model
        for p in ports:
            assert len(p.switches) == (1 if p.busbar else 2), p.name
            for s in p.switches:
                assert s in switch_map, f"{s} ({p.name})"


class TestPortableSourcePath:
    def test_relative_below_base(self, tmp_path):
        (tmp_path / "syslab-master-conf" / "conf").mkdir(parents=True)
        got = portable_source_path(tmp_path / "syslab-master-conf" / "conf", tmp_path)
        assert got == "syslab-master-conf/conf"

    def test_outside_base_keeps_last_two_parts(self, tmp_path):
        got = portable_source_path(Path("C:/Users/someone/git/ws/syslab-master-conf/conf"), tmp_path)
        assert got == "syslab-master-conf/conf"
        assert "someone" not in got


class TestEquipmentCatalog:
    def test_loads_expected_equipment(self):
        cat = load_equipment_catalog()
        ids = {e["id"] for e in cat["equipment"]}
        assert {"mobile_load_1", "mobile_load_2", "mobile_load_3",
                "inline_impedance", "mobile_converter"} <= ids

    def test_includes_cable_types(self):
        cat = load_equipment_catalog()
        assert "NOIK-AL-M 4x95 0.6/1kV" in cat["cable_types"]

    def test_json_serializable(self):
        json.dumps(load_equipment_catalog())

    @pytest.mark.parametrize("entry,msg", [
        ({"id": "x", "kind": "toaster", "terminals": 1, "ports": ["socket"]}, "unknown kind"),
        ({"id": "x", "kind": "load", "terminals": 2, "ports": ["socket"]}, "terminal"),
        ({"id": "x", "kind": "load", "terminals": 1, "ports": ["wall"]}, "invalid ports"),
        ({"id": "x", "kind": "load", "terminals": 1, "ports": []}, "invalid ports"),
    ])
    def test_validation_errors(self, tmp_path, entry, msg):
        p = tmp_path / "cat.yaml"
        p.write_text(yaml.safe_dump({"equipment": [entry]}), encoding="utf-8")
        with pytest.raises(ValueError, match=msg):
            load_equipment_catalog(p)

    def test_duplicate_id(self, tmp_path):
        e = {"id": "x", "kind": "load", "terminals": 1, "ports": ["socket"]}
        p = tmp_path / "cat.yaml"
        p.write_text(yaml.safe_dump({"equipment": [e, e]}), encoding="utf-8")
        with pytest.raises(ValueError, match="Duplicate"):
            load_equipment_catalog(p)


class TestSocketMeters:
    """Each meter of a CEE bay belongs to a separate socket (data/socket_meters.yaml)."""

    @pytest.fixture(scope="class")
    def ports(self):
        from syslab_pandapower_builder.builder import load_socket_meters
        from syslab_pandapower_builder.hardware_parser import load_grid_switchboards
        return {
            p.name: p
            for p in derive_socket_ports(load_grid_switchboards(_CONF_DIR), load_socket_meters())
        }

    def test_every_port_has_a_meter(self, ports):
        assert len(ports) == 10
        assert all(p.meter for p in ports.values())

    def test_ceex2_has_two_sockets_each_tied_to_a_busbar(self, ports):
        assert (ports["319-2 CEEx2.A"].busbar, ports["319-2 CEEx2.A"].meter) == ("A", "CEEx2.A")
        assert (ports["319-2 CEEx2.B"].busbar, ports["319-2 CEEx2.B"].meter) == ("B", "CEEx2.B")
        assert ports["117-2 CEEx2.A"].meter == "CEEx2_2"
        assert ports["117-2 CEEx2.B"].meter == "CEEx2_1"

    def test_interlocked_bays_have_one_socket_on_either_busbar(self, ports):
        for name, p in ports.items():
            if "CEEx2" not in name:
                assert p.busbar == "" and len(p.switches) == 2, name

    def test_sockets_per_busbar_are_separate_buses_with_one_switch(self):
        net, switch_map, _ = create_syslab_model(_CONF_DIR)
        names = set(net.bus["name"])
        assert {"319-2_CEEx2.A", "319-2_CEEx2.B"} <= names
        assert "319-2_CEEx2" not in names
        assert "319_2_BRK_CEEx2_Busbar_A" in switch_map

    def test_meter_for_unknown_port_is_rejected(self):
        from syslab_pandapower_builder.hardware_parser import load_grid_switchboards
        with pytest.raises(ValueError, match="unknown ports"):
            derive_socket_ports(load_grid_switchboards(_CONF_DIR), {"319-2 CEEx2": "x"})
