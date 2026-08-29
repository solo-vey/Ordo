# alpha.20.0.144-dev

Model Chat UX changes:

- removes the standalone `Upload YAML` action from the initial empty page;
- keeps `Upload Playbook`;
- Model Chat now starts an asynchronous agent run and polls incremental status;
- every completed/started local workspace action is visible immediately in the chat;
- final model Markdown arrives only when the agent turn is complete;
- Stop requests cancellation of the active Model Chat run;
- full agent trace/debug export behavior is preserved.

This is transport/UI orchestration only; playbook execution semantics are unchanged.
