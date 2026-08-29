# Ordo Tree Editor 0.2.0-alpha.20.0.215-dev

- Replay Real Chat now renders canonical user-visible Markdown messages and reconstructed Markdown source as formatted Markdown instead of literal markup text.
- Canonical debug artifacts with Markdown content use formatted preview in Replay.
- Observed-file Summary tables now combine read_observed/write_observed into one compact Access column (R / W / RW / —).
- File size remains explicitly labeled as metadata and is not presented as bytes read by the model. Exact Read bytes / Written bytes columns appear only when exact byte evidence is present.
- Added tooltips and explanatory note for file-access evidence semantics.
- No canonical debug evidence or runtime semantics changed.
