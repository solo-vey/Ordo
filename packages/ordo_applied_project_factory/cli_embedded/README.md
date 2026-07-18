# Embedded Ordo Runtime CLI

This runtime package carries a minimal CLI entrypoint so guided execution does not depend on model memory or direct IR reading.

Use:

```bash
./cli_embedded/ordo runtime-entry .
./cli_embedded/ordo next-step . --state run_state.json
./cli_embedded/ordo intake . --submit <NODE_ID> --answer "<answer>"
./cli_embedded/ordo intake . --submit <NODE_ID> --answer-file tmp_answer.yaml
./cli_embedded/ordo check-gate . <GATE_ID> --state run_state.json
./cli_embedded/ordo validate-state . --state run_state.json
./cli_embedded/ordo render-runtime-view . --format ordo-code --node <NODE_ID>
./cli_embedded/ordo verify-targets .
./cli_embedded/ordo restore-session . --to-seq <N>
./cli_embedded/ordo verify-session .
```

Only runtime commands are exposed. Authoring/package/release commands are intentionally blocked in the embedded runtime profile.

M60.4 adds append-only `restore-session` for correction/backtrack without deleting prior proof material. M60.3 keeps JSON IR as the canonical target, supports explicit runtime view modes (`json`, `ordo-code`, `json,ordo-code`), and writes `runtime/session.ordo.trace` as an append-only proof program. M59.4+M60.3 require every incremental node submit to write `runtime/evidence/*_evidence.json`, `runtime/state_snapshots/SESSION-*.json`, `runtime/session.ordo.trace`, and an auto-resume cache at `runtime/live_session_state.json`; the AI must show evidence and trace digests before asking the next question. `restore-session` must write restore evidence, a restore snapshot, and a restore trace step. Final approval requires `verify-session`.
