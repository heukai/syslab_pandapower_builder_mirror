"""Configuration in force on a day, from the lab repository (skipped where the workspace has no syslab/ clone)."""

import datetime as dt
from pathlib import Path

import pytest

from syslab_pandapower_builder.conf_snapshot import conf_in_force, export_conf
from syslab_pandapower_builder.hardware_parser import load_grid_switchboards

LAB = Path(__file__).resolve().parents[2] / "syslab"
pytestmark = pytest.mark.skipif(not (LAB / "conf").is_dir(), reason="no syslab/ clone in the workspace")


def test_last_commit_written_on_or_before_the_day():
    before, after = (conf_in_force(LAB, dt.date(2026, 8, d))["syslab-53"] for d in (12, 13))
    assert before.written < dt.date(2026, 8, 13) <= after.written     # 310-2 Boiler, written 2026-08-13
    assert "syslab-53" not in conf_in_force(LAB, dt.date(2023, 10, 1))  # 310-2 configured from 2023-10-19


def test_exported_configuration_carries_the_rename(tmp_path):
    export_conf(LAB, dt.date(2026, 8, 20), tmp_path)
    bays = {b.name for b in load_grid_switchboards(tmp_path)["310-2"].bays}
    assert "Boiler" in bays and "Spare_1" not in bays
