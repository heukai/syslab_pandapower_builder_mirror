# How is a forward change found and built?

Type: grilling
Status: open
Blocked by: 07

## Question

The regular build: diff each new release of a source (`hardware.xml`, curated YAML, SVG) against the record, decide
whether it opens a new era or corrects the current one, and build the model versions. Designed so that a CI/CD pipeline can
trigger it later (fog: its own epic).
