"""Build script: generates pandapower model artifacts for syslab_pandapower.

Usage::

    python -m syslab_pandapower_builder.build_model \
        --conf-dir syslab-master-conf/conf \
        --output-dir syslab_pandapower \
        --valid-from 2023-08-15 [--valid-to DATE] [--notes TEXT]

Outputs written to ``<output-dir>/``:
    model_data/syslab_grid.json       — serialized pandapower network
    model_data/switch_name_map.json   — BRK name → switch index mapping
    model_data/converter_connections.json — B2B converter definitions
    model_data/breaker_groups.json    — breaker groups + inline/socket ports
    model_data/equipment_catalog.json — equipment + cable types for ports
    model_data/model_version.json     — version/validity metadata
    create_model.py                   — thin loader (auto-generated)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandapower as pp

from .hardware_parser import load_grid_switchboards
from .builder import (
    create_syslab_model,
    derive_socket_ports,
    load_breaker_groups,
    load_equipment_catalog,
    portable_source_path,
    save_model_version,
    save_switch_name_map,
)


_LOADER_TEMPLATE = '''\
"""Load SYSLAB pandapower model artifacts.

Supports both legacy single-model layout (files directly under
``model_data``) and multi-model layout via ``model_data/models/<model_id>``.
If multi-model layout is present, active model selection is read from
``model_data/default_model.txt`` unless ``model_id`` is explicitly passed.
"""

from __future__ import annotations

from pathlib import Path

import pandapower as pp

from .runtime.model_loader import load_artifact_json, load_model_json, resolve_model_dir


_MODEL_DIR = Path(__file__).resolve().parent / "model_data"


def create_syslab_model(
    model_id: str | None = None,
    *,
    model_data_dir: Path | str | None = None,
) -> pp.pandapowerNet:
    """Load the SYSLAB pandapower network for the selected model."""
    return load_model_json(model_id=model_id, model_data_dir=model_data_dir or _MODEL_DIR)


def load_switch_name_map(
    model_id: str | None = None,
    *,
    model_data_dir: Path | str | None = None,
) -> dict[str, int]:
    """Load the BRK-name -> switch-index mapping table."""
    return load_artifact_json(
        "switch_name_map.json",
        model_id=model_id,
        model_data_dir=model_data_dir or _MODEL_DIR,
    )


def load_model_version(
    model_id: str | None = None,
    *,
    model_data_dir: Path | str | None = None,
) -> dict:
    """Load model version and validity metadata."""
    return load_artifact_json(
        "model_version.json",
        model_id=model_id,
        model_data_dir=model_data_dir or _MODEL_DIR,
    )


def load_converter_connections(
    model_id: str | None = None,
    *,
    model_data_dir: Path | str | None = None,
) -> list[dict]:
    """Load back-to-back converter definitions.

    Returns an empty list if the artifact is absent.
    """
    try:
        return load_artifact_json(
            "converter_connections.json",
            model_id=model_id,
            model_data_dir=model_data_dir or _MODEL_DIR,
        )
    except FileNotFoundError:
        return []


def load_breaker_groups(
    model_id: str | None = None,
    *,
    model_data_dir: Path | str | None = None,
) -> dict:
    """Load breaker group, inline-port and socket-port definitions.

    Returns ``{"breaker_groups": [], "inline_ports": [], "socket_ports": []}``
    if absent.
    """
    try:
        return load_artifact_json(
            "breaker_groups.json",
            model_id=model_id,
            model_data_dir=model_data_dir or _MODEL_DIR,
        )
    except FileNotFoundError:
        return {"breaker_groups": [], "inline_ports": [], "socket_ports": []}


def load_equipment_catalog(
    model_id: str | None = None,
    *,
    model_data_dir: Path | str | None = None,
) -> dict:
    """Load the equipment catalog assignable to ports.

    Returns ``{"equipment": [...], "cable_types": {...}}``; empty containers
    if absent.
    """
    try:
        return load_artifact_json(
            "equipment_catalog.json",
            model_id=model_id,
            model_data_dir=model_data_dir or _MODEL_DIR,
        )
    except FileNotFoundError:
        return {"equipment": [], "cable_types": {}}


def get_active_model_id(*, model_data_dir: Path | str | None = None) -> str | None:
    """Return active model id when multi-model layout is used, else None."""
    base = Path(model_data_dir) if model_data_dir is not None else _MODEL_DIR
    models_root = base / "models"
    if not models_root.exists():
        return None
    model_dir = resolve_model_dir(model_data_dir=base)
    return model_dir.name
'''


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Build SYSLAB pandapower model from XML + YAML sources",
    )
    parser.add_argument(
        "--conf-dir",
        type=Path,
        default=Path("syslab-master-conf/conf"),
        help="Path to conf/ folder (from syslab-master) (default: %(default)s)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("syslab_pandapower"),
        help="Output directory for generated artifacts (default: %(default)s)",
    )
    parser.add_argument(
        "--valid-from",
        required=True,
        help="ISO date when this model configuration became valid (e.g. 2023-08-15)",
    )
    parser.add_argument(
        "--valid-to",
        default=None,
        help="ISO date when this model configuration stopped being valid (default: None = current)",
    )
    parser.add_argument(
        "--notes",
        default="",
        help="Free-text notes for model_version.json",
    )
    args = parser.parse_args(argv)

    conf_dir = args.conf_dir.resolve()
    output_dir = args.output_dir.resolve()
    model_data_dir = output_dir / "model_data"
    model_data_dir.mkdir(parents=True, exist_ok=True)

    print(f"Building model from: {conf_dir}")
    print(f"Output directory:    {output_dir}")

    # Build network + mapping + converter definitions
    net, switch_map, converters = create_syslab_model(conf_dir)

    print(f"  Buses:    {len(net.bus)}")
    print(f"  Switches: {len(net.switch)}")
    print(f"  Lines:    {len(net.line)}")
    print(f"  Mapped BRK names: {len(switch_map)}")

    # Save serialized pandapower model
    model_json_path = model_data_dir / "syslab_grid.json"
    pp.to_json(net, str(model_json_path))
    print(f"  Written: {model_json_path}")

    # Save switch name map
    map_path = model_data_dir / "switch_name_map.json"
    save_switch_name_map(switch_map, map_path)
    print(f"  Written: {map_path}")

    # Save converter connections
    conv_path = model_data_dir / "converter_connections.json"
    with open(conv_path, "w", encoding="utf-8") as f:
        json.dump(
            [{"name": c.name, "primary_bus": c.primary_bus, "secondary_bus": c.secondary_bus}
             for c in converters],
            f, indent=2,
        )
    print(f"  Written: {conv_path}")

    # Save breaker groups + inline ports
    groups, ports = load_breaker_groups()
    socket_ports = derive_socket_ports(load_grid_switchboards(conf_dir))
    bg_path = model_data_dir / "breaker_groups.json"
    with open(bg_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "breaker_groups": [
                    {
                        "name": g.name,
                        "type": g.type,
                        "description": g.description,
                        "switches": [
                            {"name": s.name, "default_closed": s.default_closed, "logged": s.logged}
                            for s in g.switches
                        ],
                        "interlocks": [
                            {"group": i.group, "max_closed": i.max_closed, "members": i.members}
                            for i in g.interlocks
                        ],
                    }
                    for g in groups
                ],
                "inline_ports": [
                    {
                        "name": p.name,
                        "cable": p.cable,
                        "location": p.location,
                        "description": p.description,
                        "modes": [
                            {"name": m.name, "description": m.description, "default": m.default}
                            for m in p.modes
                        ],
                    }
                    for p in ports
                ],
                "socket_ports": [
                    {
                        "name": p.name,
                        "switchboard": p.switchboard,
                        "bay": p.bay,
                        "bus": p.bus,
                        "switches": p.switches,
                        "description": p.description,
                    }
                    for p in socket_ports
                ],
            },
            f, indent=2,
        )
    print(f"  Written: {bg_path}")

    # Save equipment catalog (devices/cables assignable to ports)
    cat_path = model_data_dir / "equipment_catalog.json"
    with open(cat_path, "w", encoding="utf-8") as f:
        json.dump(load_equipment_catalog(), f, indent=2)
    print(f"  Written: {cat_path}")

    # Save model version
    save_model_version(
        model_data_dir,
        valid_from=args.valid_from,
        valid_to=args.valid_to,
        hardware_xml_source=portable_source_path(conf_dir),
        notes=args.notes,
    )
    print(f"  Written: {model_data_dir / 'model_version.json'}")

    # Generate thin loader
    loader_path = output_dir / "create_model.py"
    loader_path.write_text(_LOADER_TEMPLATE, encoding="utf-8")
    print(f"  Written: {loader_path}")

    print("\nBuild complete.")


if __name__ == "__main__":
    main()
