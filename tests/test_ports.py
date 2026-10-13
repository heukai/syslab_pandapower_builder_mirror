"""Tests for socket ports (CEE bays) and the equipment catalog (ADR-0004)."""

import json
from pathlib import Path

import pytest
import yaml

from syslab_pandapower_builder.builder import (
    SocketPortDef,
    create_syslab_model,
    derive_socket_ports,
    load_equipment_catalog,
    portable_source_path,
)
from syslab_pandapower_builder.hardware_parser import BayDef, BreakerDef, SwitchboardDef

_CONF_DIR = Path(__file__).resolve().parents[2] / "syslab-master-conf" / "conf"


def _sb(name: str, bays: list[BayDef]) -> SwitchboardDef:
    return SwitchboardDef(name=name, busbars=["Busbar_A", "Busbar_B"], bays=bays)


def _bay(name: str, with_breakers: bool = True) -> BayDef:
    brks = (
        [BreakerDef(f"{name}-A", "Busbar_A", name), BreakerDef(f"{name}-B", "Busbar_B", name)]
        if with_breakers else []
    )
    return BayDef(name=name, breakers=brks)


class TestDeriveSocketPorts:
    def test_only_cee_bays_with_breakers(self):
        sbs = {"319-2": _sb("319-2", [_bay("CEE"), _bay("CEEx2"), _bay("PV"), _bay("CEE_3", False)])}
        ports = derive_socket_ports(sbs)
        assert [p.name for p in ports] == ["319-2 CEE", "319-2 CEEx2"]

    def test_fields_and_brk_names(self):
        (p,) = derive_socket_ports({"319-2": _sb("319-2", [_bay("CEEx2")])})
        assert isinstance(p, SocketPortDef)
        assert p.switchboard == "319-2"
        assert p.bay == "CEEx2"
        assert p.bus == "319-2_CEEx2"
        assert p.switches == ["319_2_BRK_CEEx2_Busbar_A", "319_2_BRK_CEEx2_Busbar_B"]

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
        assert {p.name for p in ports} >= {"319-2 CEE", "319-2 CEEx2"}
        assert len(ports) == 8

    def test_bus_exists_in_network(self, model):
        net, _, ports = model
        names = set(net.bus["name"])
        for p in ports:
            assert p.bus in names, p.name

    def test_switches_in_switch_map(self, model):
        _, switch_map, ports = model
        for p in ports:
            assert len(p.switches) == 2
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
