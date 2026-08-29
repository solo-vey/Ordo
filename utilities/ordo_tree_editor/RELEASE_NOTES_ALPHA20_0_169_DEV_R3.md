# Ordo Tree Editor 0.2.0-alpha.20.0.169-dev

## Server-managed Execute Playbook REST API

No canonical Ordo language semantics changed in this release.

Added a high-level local REST layer for agents that need to drive the same live runtime used by **Execute Playbook** without reproducing browser-owned execution state.

### New Execute Playbook API

- `POST /api/execute-run-start` — create a server-managed run from a loaded playbook package; optionally attach registered Auto Answers and immediately advance;
- `POST /api/execute-run-step` — execute exactly one persisted runtime phase;
- `POST /api/execute-run-advance` — advance until missing analyst input, terminal, halt/error, or bounded max-steps;
- `POST /api/execute-run-input` — submit analyst input and optionally continue;
- `POST /api/execute-run-stop` — stop the run (or request stop after an already-running synchronous phase);
- `GET /api/execute-run-status` — current element, canonical state/revision, execution path, transcript, usage, artifacts and outcome;
- `GET /api/execute-run-debug` — full state/history/transcript/debug trace/error traceback/Auto Answer cursors for automated failure analysis.

The high-level layer calls the same live runtime boundary as `/api/live-step`; it does not implement a second execution semantics.

### Auto Answers

`POST /api/replay-package` remains backward compatible and now additionally registers the parsed replay server-side and returns `replay_id`. That id can be supplied to `execute-run-start` as `auto_answers_replay_id`.

### API documentation

Added `/api-docs/execute-playbook.html`, a task-oriented guide describing the complete agent workflow with direct links to the relevant OpenAPI operations. Help → REST API links to this guide.

The OpenAPI 3.1 contract now documents 45 HTTP operations and contains a dedicated **Execute Playbook** group.

### Safety / consistency

- managed runs retain canonical state, revision, path, transcript and debug evidence server-side;
- concurrent execution of the same managed run fails closed as busy;
- runtime exceptions retain the pre-failure state and capture node/phase/type/message/traceback in the debug snapshot;
- runtime artifacts returned in run status include ready-to-use download URLs;
- the server remains local-by-default (`127.0.0.1`).
