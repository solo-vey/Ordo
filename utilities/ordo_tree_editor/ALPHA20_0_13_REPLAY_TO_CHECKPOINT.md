# Alpha 20.0.13 — Replay to Checkpoint

Adds deterministic guided replay for debugging and regression reproduction.

- Load a previous debug-run summary or reproduction ZIP.
- Replays recorded analyst answers and accepted model structured outputs.
- Recorded model output is revalidated by the current runtime semantic contract; it is not copied directly into state.
- Replay stops automatically at the configured checkpoint and switches to live execution.
- Designed to avoid repeated LLM calls while reproducing a late-stage problem.
- Existing Auto answers mode remains available and unchanged in purpose.
