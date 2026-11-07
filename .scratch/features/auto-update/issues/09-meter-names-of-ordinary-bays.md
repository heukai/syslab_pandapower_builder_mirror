# Which meter name does the model give an ordinary bay?

Type: grilling
Status: open
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

## Comments
