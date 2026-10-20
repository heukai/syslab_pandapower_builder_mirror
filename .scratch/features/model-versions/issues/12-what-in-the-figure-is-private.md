# What in the switchboard overview figure is private or operator-only?

Type: research
Status: open
Blocked by: -

## Question

From the two samples (`sample_data_SYSLAB-NAS/switchboard_overview_6(1).svg`, `_7.svg`): list everything that must not reach
the public `syslab_pandapower` package or is meaningful only to the operator UI (layers such as `LayerLoginButton`,
`LayerAccessDenied`, user-name and logout texts, Inkscape metadata and export paths, hidden or out-of-service layers, anything
naming people, hosts or internal paths), and what the figure must keep for a label map (which texts name switchboards, bays,
breakers and cables, and how a label is tied to its switchboard: grouping, position). Second pass after the access ticket:
what the Java code reads from the figure.
