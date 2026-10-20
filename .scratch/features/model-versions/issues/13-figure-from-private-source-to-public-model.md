# How does a figure travel safely from its private source to the public model?

Type: grilling
Status: open
Blocked by: 01, 12

## Question

Decide the pipe from the figure's private repository to `syslab_pandapower` (public): what is stripped and how (sanitizing in
the builder, the only side with access), who may publish the figure (permission of its owner), which artifacts are published per
model version (sanitized SVG, PNG render, label map) and in what format, how a figure version is tied to its configuration era,
and which checks block publishing if anything private remains. Designed so the future CI/CD pipeline can run it.
