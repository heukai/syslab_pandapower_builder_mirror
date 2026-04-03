"""Internal tool for building the syslab_pandapower model from ground-truth sources.

This package reads hardware.xml files (breaker topology) and curated
engineering data files (cables, non-breaker connections, cable parameters,
converter connections) to produce:

- A pandapower model (both Python source and serialized JSON)
- A BRK-name-to-switch-index mapping table (switch_name_map.json)
- A converter connections manifest (converter_connections.json)
- A model version manifest with validity time range (model_version.json)

The outputs are committed to the ``syslab_pandapower`` repository.

Data files
----------
The ``data/`` directory contains four curated YAML input files:

- **cable_types.yaml** — Electrical parameters for cable types used in
  the SYSLAB grid (impedance, capacitance, ampacity).
- **cables.yaml** — Inter-substation cable definitions linking bus
  endpoints in different switchboards.
- **non_breaker_connections.yaml** — Physical wiring that hardware.xml
  does not describe (connections without breakers).  Currently empty;
  back-to-back converters were moved to their own file.
- **converter_connections.yaml** — Back-to-back (B2B) converter
  definitions.  These devices electrically *isolate* primary and
  secondary sides and are NOT modeled as pandapower lines.  See below.

Converter modeling
------------------
B2B converters (ABB B2B, Grid Emulator) differ fundamentally from cables
and passive connections:

1. They **isolate** primary and secondary sides — no direct power flow
   through impedance.  In the pandapower model, primary and secondary
   buses exist but have **no line** between them.

2. The secondary side is an **externally controllable** four-quadrant
   converter that can operate in one of two modes:

   - **grid_forming** — The converter acts as a voltage source
     (``ext_grid`` / slack bus in pandapower).  Typically active when
     no other grid connection exists in the secondary side's electrical
     island.
   - **pq** — The converter acts as a controllable PQ device
     (``sgen`` in pandapower), emulating a load, generator, or storage.
     Requires another grid-forming source in the island.

3. The builder serializes converter definitions to
   ``model_data/converter_connections.json`` alongside the PP model.
   Downstream consumers (``syslab_data.topology``) load this file to
   tag converter nodes on the topology graph and to let
   ``ConnectedGrid`` suggest default operating modes.

Build workflow::

    python -m syslab_pandapower_builder.build_model \\
        --conf-dir syslab-master-conf/conf \\
        --valid-from 2023-08-15

This produces all artifacts in ``syslab_pandapower/model_data/``.
"""

__version__ = "0.1.0"
