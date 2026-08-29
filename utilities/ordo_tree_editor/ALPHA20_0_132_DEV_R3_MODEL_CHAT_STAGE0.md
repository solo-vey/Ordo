# alpha.20.0.132-dev — Model Chat architecture review Stage 0

Implements Stage 0 from the independent architecture review.

Changes:
- removes full `_workspace_index(root)` from the model context;
- adds compact `_workspace_head(root)`:
  - file count;
  - total bytes;
  - top directories;
  - up to six high-confidence entrypoint/start/prompt/readme/instruction/manifest candidates;
- no file bodies are embedded in workspace_head;
- model must use workspace.list/search/read for further discovery;
- browser response now returns workspace head rather than a 300-entry index.

Acceptance fixture:
- 5,002-file workspace => workspace_head estimated below 400 tokens;
- startup prompt is discoverable as a candidate;
- file contents are not included.
