# Which meter name does the model give an ordinary bay?

Type: grilling
Status: resolved
Blocked by:

## Question

The model names the meter of a socket port (`socket_ports[].meter`, e.g. `CEEx2.A`) but not of an ordinary bay: the
simulation looks for `P_<bay>` (bay `Grid` -> `P_Grid`). hardware.xml names the instrument of 117-4's Grid bay `Grid_4`
since 2023-10-31; the data said `P_Grid` until 2026-06-24 (data-name period D27, meter-lag) and say `P_Grid_4` from
then on. So on 2026-06-25 the 117-4/117-5 island has an unmeasured slack and no residual (remote session, 2026-11-07),
exactly when the data caught up with the configuration. Same pattern for `Grid_2` (117-2) and the CEEx2 meters.

Draft: the model carries, for every metered bay, the instrument name from hardware.xml (`Grid_4`), as socket ports
already do; the simulation reads the meter by that name; the data of a meter-lag period are translated by its column
map (ticket 08). Builder and syslab_data change; done in the remote session.

## Answer

Settled with the maintainer, 2026-11-07: the model carries, for every metered bay, the instrument name from
hardware.xml (bay `Grid` of 117-4 -> meter `Grid_4`), as socket ports already do, and the simulation reads a bay's meter
by that name. Builder and syslab_data change; done in the remote session. Data of meter-lag periods are read through
their column map (ticket 08).

## Comments
- 2026-11-07, implemented by the remote session on local branches, not pushed (waiting for the maintainer): builder
  `bay-meters` (from `model-versions`) writes `bay_meters` [{switchboard, bay, bus, meters}] into breaker_groups.json
  with the hardware.xml instrument names (CEE bays left out: their sockets carry a meter); syslab_data `bay-meters` keeps
  them in the graph, and `apply_socket_meters` copies a single-instrument bay's meter column to the bay's column
  (`P_Grid_4` -> `P_Grid`), never overwriting an existing bay column, leaving bays with several instruments alone. So the
  simulation still reads bay columns; the data are mapped onto them (a variant of the decision, same effect). End to end,
  2026-06-25 with set-up and reader fix: the 117-4/117-5 island closes at -0.003 / 0.015 kW; every island of the day
  closes. D27 days (data `P_Grid`) need no column map for this. Blocker: no hardware.xml on the sandbox, so no real build
  with `bay_meters` there (ticket 06).
