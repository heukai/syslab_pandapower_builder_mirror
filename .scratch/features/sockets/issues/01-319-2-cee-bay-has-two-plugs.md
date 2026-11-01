# The 319-2 CEE bay has two sockets behind one breaker pair and one meter

Status: needs-triage
Filed: 2026-11-01, from the maintainer (seen at the lab)
Consumer side: `syslab_data/.scratch/features/sockets/issues/01-several-plugs-on-one-socket-port.md`

## Problem

The model has one socket port per interlocked CEE bay: "319-2 CEE" is one port with one meter (`socket_meters.yaml`,
`SocketPortDef` in `builder.py`). At the lab, the 319-2 CEE bay turns out to have **two plugs (sockets)**: two devices
can be plugged in on the same bay at the same time. Both hang behind the same interlocked breaker pair (Busbar A or B)
and the same meter, so the meter measures their sum.

Electrically the grid model is unchanged (both sockets are on the bay's bus, below the meter). The limitation is in what
the model publishes about the port: nothing says the port takes two plugs, and `syslab_data` allows one device per port
("port ... is occupied twice").

Not the same as CEEx2 (319-2, 117-2): there each socket is tied to its own busbar and has its own meter, so each is a
port of its own.

## Proposal

- A socket port gets a socket count (`sockets: 2` for "319-2 CEE"; default 1), declared in `socket_meters.yaml` (or a
  sibling file) with the source "seen at the lab by the maintainer, 2026-11-01", and written to the model's port data.
- No second port: the two sockets share bus, breakers and meter, so the data cannot tell them apart.
- In the versioning: a declared fact, not a lab change (it has always been so) -> a third-level model improvement
  (e.g. the next 6.x.N), change entry with origin `declared`.

## Open

- Which other CEE bays have more than one socket (310-2 CEE_1/CEE_2, 117-5 CEEx1, 716-2 CEE, 330-12)? Staff question.
- Is "CEE 1" the bay `CEE` of 319-2 (hardware.xml has `CEE` and `CEEx2` on 319-2)?

## Comments
