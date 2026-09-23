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
  `converter_connections.yaml`, `breaker_groups.yaml`).

## See also

- Output consumed by `syslab_pandapower` (published model package) and
  directly by `syslab_data/topology/graph.py`.
- Domain docs (`CONTEXT.md`, `docs/adr/`) for this repo don't exist yet —
  see the outer workspace `AGENTS.md` → "Requirements" for the plan to add
  them here.
