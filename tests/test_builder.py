"""Tests for syslab_pandapower_builder — data loading, naming, and model assembly."""

import json
from pathlib import Path

import pandapower as pp
import pytest

from syslab_pandapower_builder.builder import (
    BreakerGroupDef,
    CableDef,
    ConverterDef,
    InlinePortDef,
    InlinePortMode,
    InterlockDef,
    SwitchDefault,
    busbar_suffix,
    build_pp_network,
    build_switch_name_map,
    create_syslab_model,
    load_breaker_groups,
    load_cable_types,
    load_cables,
    load_converter_connections,
    load_non_breaker_connections,
    _bb_bus_name,
    _bay_bus_name,
    _derive_brk_name,
    _is_cross_bay,
    _parse_cross_breaker,
)
from syslab_pandapower_builder.hardware_parser import (
    BayDef,
    BreakerDef,
    SwitchboardDef,
    parse_hardware_xml,
    load_grid_switchboards,
)


# ========================================================================
# Naming helpers
# ========================================================================

class TestBusbarSuffix:
    def test_busbar_a(self):
        assert busbar_suffix("Busbar_A") == "A"

    def test_busbar_b(self):
        assert busbar_suffix("Busbar_B") == "B"

    def test_grid(self):
        assert busbar_suffix("Grid") == "Grid"

    def test_busbar_supply(self):
        assert busbar_suffix("Busbar_Supply") == "Supply"

    def test_busbar_transformer(self):
        assert busbar_suffix("Busbar_Transformer") == "Transformer"


class TestBbBusName:
    def test_standard(self):
        assert _bb_bus_name("319-2", "Busbar_A") == "319-2_Busbar-A"

    def test_grid_busbar(self):
        assert _bb_bus_name("715-2", "Grid") == "715-2_Busbar-Grid"

    def test_supply_busbar(self):
        assert _bb_bus_name("319-3", "Busbar_Supply") == "319-3_Busbar-Supply"


class TestBayBusName:
    def test_standard(self):
        assert _bay_bus_name("319-2", "Diesel") == "319-2_Diesel"

    def test_cross_bay(self):
        assert _bay_bus_name("319-4", "Cross_A") == "319-4_Cross_A"


class TestParseCrossBreaker:
    def test_valid_cross_breaker(self):
        result = _parse_cross_breaker("319-3A-4A")
        assert result == ("319-3", "A", "319-4", "A")

    def test_different_busbars(self):
        result = _parse_cross_breaker("319-3B-4C")
        assert result == ("319-3", "B", "319-4", "C")

    def test_not_a_cross_breaker(self):
        assert _parse_cross_breaker("Battery") is None

    def test_bay_name(self):
        assert _parse_cross_breaker("Grid_2") is None


class TestIsCrossBay:
    def test_cross_bay(self):
        assert _is_cross_bay("Cross_A") is True

    def test_not_cross(self):
        assert _is_cross_bay("Diesel") is False
        assert _is_cross_bay("Grid") is False


# ========================================================================
# BRK name derivation
# ========================================================================

class TestDeriveBrkName:
    def test_busbar_to_bay(self):
        # bus_name=busbar, element_name=bay → standard BRK name
        result = _derive_brk_name("319-2_Busbar-A", "319-2_Diesel")
        assert result == "319_2_BRK_Diesel_Busbar_A"

    def test_bay_to_busbar(self):
        # Reversed: bus_name=bay, element_name=busbar
        result = _derive_brk_name("319-2_Diesel", "319-2_Busbar-A")
        assert result == "319_2_BRK_Diesel_Busbar_A"

    def test_grid_busbar(self):
        # Grid busbar uses suffix "Grid"
        result = _derive_brk_name("715-2_Busbar-Grid", "715-2_Grid")
        assert result == "715_2_BRK_Grid_Busbar_Grid"

    def test_crossbar_breaker(self):
        # Both busbars, different switchboards → crossbar naming
        result = _derive_brk_name("319-3_Busbar-A", "319-4_Busbar-B")
        assert result == "319_4_BRK_Cross_A_Busbar_B"

    def test_crossbar_reversed(self):
        result = _derive_brk_name("319-4_Busbar-C", "319-3_Busbar-A")
        assert result == "319_4_BRK_Cross_A_Busbar_C"

    def test_same_switchboard_busbars_returns_none(self):
        result = _derive_brk_name("319-2_Busbar-A", "319-2_Busbar-B")
        assert result is None

    def test_neither_busbar_returns_none(self):
        result = _derive_brk_name("319-2_Diesel", "319-2_PV")
        assert result is None

    def test_cable_bay(self):
        result = _derive_brk_name("319-3_Cable_B2A", "319-3_Busbar-A")
        assert result == "319_3_BRK_Cable_B2A_Busbar_A"


# ========================================================================
# YAML data loading
# ========================================================================

class TestLoadCableTypes:
    def test_loads_cable_types(self):
        types = load_cable_types()
        assert isinstance(types, dict)
        assert len(types) > 0
        # Each type should have electrical parameters
        for name, params in types.items():
            assert isinstance(name, str)
            assert isinstance(params, dict)

    def test_custom_path(self, tmp_path):
        p = tmp_path / "test_types.yaml"
        p.write_text('cable_types:\n  test_cable:\n    r_ohm_per_km: 0.1\n')
        types = load_cable_types(p)
        assert "test_cable" in types


class TestLoadCables:
    def test_loads_cables(self):
        cables = load_cables()
        assert isinstance(cables, list)
        assert len(cables) > 0
        for c in cables:
            assert isinstance(c, CableDef)
            assert c.length_km > 0


class TestLoadConverterConnections:
    def test_loads_converters(self):
        converters = load_converter_connections()
        assert isinstance(converters, list)
        for c in converters:
            assert isinstance(c, ConverterDef)
            assert c.primary_bus
            assert c.secondary_bus


# ========================================================================
# Breaker groups — YAML loading with `logged` field
# ========================================================================

class TestLoadBreakerGroups:
    @pytest.fixture(autouse=True)
    def _load(self):
        self.groups, self.ports = load_breaker_groups()

    def test_returns_groups_and_ports(self):
        assert isinstance(self.groups, list)
        assert isinstance(self.ports, list)
        assert len(self.groups) > 0

    def test_group_structure(self):
        for g in self.groups:
            assert isinstance(g, BreakerGroupDef)
            assert g.name
            assert g.type
            assert isinstance(g.switches, list)
            assert isinstance(g.interlocks, list)

    def test_switch_has_logged_field(self):
        """All SwitchDefault instances should have a logged attribute."""
        for g in self.groups:
            for s in g.switches:
                assert isinstance(s, SwitchDefault)
                assert hasattr(s, "logged")
                assert isinstance(s.logged, bool)

    def test_unlogged_switch_count(self):
        """Exactly 19 switches should be marked logged=False."""
        unlogged = [
            s for g in self.groups for s in g.switches if not s.logged
        ]
        assert len(unlogged) == 19

    def test_known_unlogged_switches(self):
        """Specific switches should be marked unlogged."""
        all_switches = {s.name: s for g in self.groups for s in g.switches}
        assert not all_switches["117_2_BRK_Grid_2_Busbar_Grid"].logged
        assert not all_switches["117_4_BRK_Cable_D1_Manual_Busbar_A"].logged
        assert not all_switches["715_2_BRK_Grid_Busbar_Grid"].logged

    def test_evse_117_6_all_unlogged(self):
        """All 16 EVSE switches in 117-6 should be unlogged."""
        evse = [
            s for g in self.groups for s in g.switches
            if s.name.startswith("117_6_BRK_EVSE_")
        ]
        assert len(evse) == 16
        assert all(not s.logged for s in evse)

    def test_logged_default_true(self):
        """Switches without explicit logged=false should default to True."""
        all_switches = {s.name: s for g in self.groups for s in g.switches}
        # Pick some known logged switches
        assert all_switches["319_2_BRK_Grid_Busbar_B"].logged
        assert all_switches["715_2_BRK_Grid_Busbar_A"].logged
        assert all_switches["117_2_BRK_Battery_Busbar_A"].logged

    def test_interlock_members_exist_in_switches(self):
        """All interlock member names should reference actual switches."""
        for g in self.groups:
            switch_names = {s.name for s in g.switches}
            for il in g.interlocks:
                for m in il.members:
                    assert m in switch_names, (
                        f"Interlock {il.group!r} in {g.name!r} references "
                        f"unknown switch {m!r}"
                    )

    def test_inline_ports_loaded(self):
        assert len(self.ports) > 0
        for p in self.ports:
            assert isinstance(p, InlinePortDef)
            assert p.cable
            assert len(p.modes) > 0


class TestLoadBreakerGroupsFromCustomYaml:
    def test_logged_defaults_true_when_omitted(self, tmp_path):
        p = tmp_path / "bg.yaml"
        p.write_text(
            'breaker_groups:\n'
            '  - name: test\n'
            '    type: test\n'
            '    description: test group\n'
            '    switches:\n'
            '      - {name: "s1", default_closed: true}\n'
            '    interlocks: []\n'
        )
        groups, _ = load_breaker_groups(p)
        assert groups[0].switches[0].logged is True

    def test_logged_false_parsed(self, tmp_path):
        p = tmp_path / "bg.yaml"
        p.write_text(
            'breaker_groups:\n'
            '  - name: test\n'
            '    type: test\n'
            '    description: test group\n'
            '    switches:\n'
            '      - {name: "s1", default_closed: true, logged: false}\n'
            '    interlocks: []\n'
        )
        groups, _ = load_breaker_groups(p)
        assert groups[0].switches[0].logged is False


# ========================================================================
# Hardware parser
# ========================================================================

class TestHardwareParser:
    @pytest.fixture(autouse=True)
    def _conf_dir(self):
        self.conf_dir = (
            Path(__file__).resolve().parent.parent.parent
            / "syslab-master-conf" / "conf"
        )
        if not self.conf_dir.exists():
            pytest.skip("syslab-master-conf not available")

    def test_parse_syslab_09(self):
        cfg = parse_hardware_xml(
            self.conf_dir / "syslab-09" / "hardware.xml",
            node_id="syslab-09",
        )
        assert cfg.device_name
        assert len(cfg.switchboards) >= 1
        sw = cfg.switchboards[0]
        assert sw.name == "715-2"
        assert len(sw.busbars) >= 2
        assert len(sw.bays) > 0

    def test_parse_syslab_11(self):
        cfg = parse_hardware_xml(
            self.conf_dir / "syslab-11" / "hardware.xml",
            node_id="syslab-11",
        )
        names = [sw.name for sw in cfg.switchboards]
        assert "117-2" in names
        assert "117-4" in names
        assert "117-5" in names

    def test_grid_switchboards(self):
        sbs = load_grid_switchboards(self.conf_dir)
        assert isinstance(sbs, dict)
        # Should have at least the major switchboards
        for expected in ["319-2", "319-3", "319-4", "715-2", "117-2"]:
            assert expected in sbs, f"Missing switchboard {expected}"

    def test_switchboard_breakers(self):
        cfg = parse_hardware_xml(
            self.conf_dir / "syslab-09" / "hardware.xml",
            node_id="syslab-09",
        )
        sw = cfg.switchboards[0]
        all_brk = sw.all_breakers()
        assert len(all_brk) > 0
        for brk in all_brk:
            assert isinstance(brk, BreakerDef)
            assert brk.name
            assert brk.busbar

    def test_bay_lookup(self):
        cfg = parse_hardware_xml(
            self.conf_dir / "syslab-09" / "hardware.xml",
            node_id="syslab-09",
        )
        sw = cfg.switchboards[0]
        grid_bay = sw.bay_by_name("Grid")
        assert grid_bay is not None
        assert grid_bay.name == "Grid"


# ========================================================================
# Full model build
# ========================================================================

class TestCreateSyslabModel:
    @pytest.fixture(autouse=True)
    def _build(self):
        conf_dir = (
            Path(__file__).resolve().parent.parent.parent
            / "syslab-master-conf" / "conf"
        )
        if not conf_dir.exists():
            pytest.skip("syslab-master-conf not available")
        self.net, self.switch_map, self.converters = create_syslab_model(conf_dir)

    def test_network_type(self):
        assert isinstance(self.net, pp.pandapowerNet)

    def test_bus_count(self):
        assert len(self.net.bus) == 185  # CEEx2 bays: one bus per socket

    def test_switch_count(self):
        assert len(self.net.switch) == 297

    def test_line_count(self):
        assert len(self.net.line) == 33

    def test_switch_map_size(self):
        assert len(self.switch_map) == 297

    def test_switch_map_contains_known_keys(self):
        assert "319_2_BRK_Grid_Busbar_B" in self.switch_map
        assert "715_2_BRK_Grid_Busbar_Grid" in self.switch_map
        assert "117_2_BRK_Grid_2_Busbar_Grid" in self.switch_map

    def test_switch_map_values_are_indices(self):
        for name, idx in self.switch_map.items():
            assert isinstance(idx, int)
            assert idx in self.net.switch.index

    def test_converters_returned(self):
        assert isinstance(self.converters, list)
        for c in self.converters:
            assert isinstance(c, ConverterDef)

    def test_bus_geodata_assigned(self):
        """All buses should have GeoJSON geodata after build."""
        geo = self.net.bus["geo"]
        assert geo.notna().all(), (
            f"{geo.isna().sum()} buses lack geodata"
        )
        # Spot-check one: should be a valid GeoJSON point string
        sample = json.loads(geo.iloc[0])
        assert sample["type"] == "Point"
        assert len(sample["coordinates"]) == 2

    def test_crossbar_switches_present(self):
        """The 6 crossbar switches should be in the switch map."""
        for src in "ABC":
            for dst in "ABC":
                key = f"319_4_BRK_Cross_{src}_Busbar_{dst}"
                if key in self.switch_map:
                    assert isinstance(self.switch_map[key], int)
        # The 6 that actually exist
        assert "319_4_BRK_Cross_A_Busbar_A" in self.switch_map
        assert "319_4_BRK_Cross_A_Busbar_B" in self.switch_map
        assert "319_4_BRK_Cross_C_Busbar_C" in self.switch_map


# ========================================================================
# JSON serialization roundtrip (breaker_groups.json)
# ========================================================================

class TestBreakerGroupsJson:
    """Test that the serialized breaker_groups.json is correct."""

    @pytest.fixture(autouse=True)
    def _load_json(self):
        json_path = (
            Path(__file__).resolve().parent.parent.parent
            / "syslab_pandapower" / "model_data" / "breaker_groups.json"
        )
        if not json_path.exists():
            pytest.skip("breaker_groups.json not built yet")
        with open(json_path, encoding="utf-8") as f:
            self.data = json.load(f)

    def test_has_breaker_groups_key(self):
        assert "breaker_groups" in self.data

    def test_has_inline_ports_key(self):
        assert "inline_ports" in self.data

    def test_switches_have_logged_field(self):
        for g in self.data["breaker_groups"]:
            for s in g["switches"]:
                assert "logged" in s, (
                    f"Switch {s['name']} in {g['name']} missing 'logged' field"
                )

    def test_unlogged_count_matches_yaml(self):
        unlogged = [
            s["name"]
            for g in self.data["breaker_groups"]
            for s in g["switches"]
            if not s["logged"]
        ]
        assert len(unlogged) == 19

    def test_logged_is_bool(self):
        for g in self.data["breaker_groups"]:
            for s in g["switches"]:
                assert isinstance(s["logged"], bool)
