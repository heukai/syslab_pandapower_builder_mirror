# syslab_pandapower_builder

Builds the serialized pandapower model consumed by `syslab_data` and
published as `syslab_pandapower`. Separate git repo
(`git.elektro.dtu.dk/kheu/syslab_pandapower_builder`, private).

## Role

Combines two sources into one pandapower network (see `syslab_data`'s
ADR-0002 for the rationale):

- `hardware.xml` per substation (read from the sibling `syslab-master-conf`
  repo) — authoritative for breaker/bay/busbar definitions.
- Curated YAML in `data/` — cable routes, cable electrical types,
  non-breaker internal connections, and breaker-group/inline-port
  definitions that `hardware.xml` cannot express.

## Contents

- `hardware_parser.py` — parses `hardware.xml` into dataclasses.
- `builder.py` — core builder: YAML + parsed XML → pandapower network, plus
  the BRK-name ↔ switch-index mapping table `syslab_data` relies on.
- `build_model.py` / `__main__.py` — CLI entry point that writes the
  serialized model JSON.
- `data/*.yaml` — the curated engineering data (`cables.yaml`,
  `cable_types.yaml`, `non_breaker_connections.yaml`,
  `converter_connections.yaml`, `breaker_groups.yaml`) plus
  `equipment_catalog.yaml` (flexibly deployed devices, see below).
  `non_breaker_connections.yaml` is currently empty (`connections: []`).
- `tests/test_builder.py` — pytest coverage for the builder.

## Usage

Run from the workspace root (the outer folder holding the sibling repos):

```powershell
python -m syslab_pandapower_builder.build_model `
    --conf-dir syslab-master-conf/conf `
    --output-dir syslab_pandapower `
    --valid-from 2023-08-15
```

| Flag | Default | Meaning |
|---|---|---|
| `--conf-dir` | `syslab-master-conf/conf` | Folder with the per-substation `hardware.xml` files |
| `--output-dir` | `syslab_pandapower` | Target package; artifacts go to `<output-dir>/model_data/` |
| `--valid-from` | *(required)* | ISO date from which this model configuration is valid |
| `--valid-to` | open-ended | ISO date when it stopped being valid |
| `--notes` | empty | Free text stored in `model_version.json` |

Outputs in `model_data/`: `syslab_grid.json`, `switch_name_map.json`,
`converter_connections.json`, `breaker_groups.json` (breaker groups, inline
ports and `socket_ports`), `equipment_catalog.json`, `model_version.json`;
plus an auto-generated `create_model.py` loader in the output dir.

## Ports and equipment catalog

Temporary equipment is never wired into the model (syslab_data ADR-0004).
Instead the build publishes the plug points and the devices that can be
assigned to them:

- **Inline ports** — curated in `breaker_groups.yaml` (24 on 319-3/319-4).
- **Socket ports** — derived automatically from every `CEE*` bay with
  breakers in `hardware.xml` (`derive_socket_ports`).
- **Equipment catalog** — `data/equipment_catalog.yaml` + the standard
  cable types, validated by `load_equipment_catalog`. Parameters of
  `status: placeholder` entries are still to be supplied by SYSLAB staff.

`syslab_pandapower` is a public repo — check the diff before committing
generated files.

## See also

- Output consumed by `syslab_pandapower` (published model package) and
  directly by `syslab_data/topology/graph.py`.
- Domain docs (`CONTEXT.md`, `docs/adr/`) for this repo don't exist yet —
  see the outer workspace `AGENTS.md` → "Requirements" for the plan to add
  them here.
