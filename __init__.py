"""Internal tool for building the syslab_pandapower model from ground-truth sources.

This package reads hardware.xml files (breaker topology) and curated
engineering data files (cables, non-breaker connections, cable parameters)
to produce:

- A pandapower model (both Python source and serialized JSON)
- A BRK-name-to-switch-index mapping table (switch_name_map.json)
- A model version manifest with validity time range (model_version.json)

The outputs are committed to the ``syslab_pandapower`` repository.
"""

__version__ = "0.1.0"
