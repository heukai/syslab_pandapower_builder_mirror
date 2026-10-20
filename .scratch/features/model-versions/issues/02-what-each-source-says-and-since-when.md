# What does each source say, and since when?

Type: research
Status: open
Blocked by: -

## Question

For every source of configuration knowledge, what does it state (switchboards, bays, breakers, cables, asset connections,
names), how are its versions dated, and how far back does it reach? First pass with what is available now: the column archive
(header eras, `syslab_data/metadata/column_archive/`), the device registry (`syslab_data/metadata/devices.py`), the builder's
git history and curated YAML, `hardware.xml` as of now, and the SVG versions 6 and 7
(`sample_data_SYSLAB-NAS/switchboard_overview_6(1).svg`, `_7.svg`; labels are visible text, ids carry no meaning). Second pass
after the access ticket: the SVG/Java repository history and the `syslab-master-conf` history.

Output: one table per source (what, dating, reach, naming), and the known changes each source shows (AirCon 715_2 -> 319_2,
the Gaia move, CEEx2 sockets, SVG 6 -> 7: 316-2, 119-10, Cable Q1, ...).
