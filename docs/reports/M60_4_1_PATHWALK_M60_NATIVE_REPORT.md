# M60.4.1 — PathWalk M60-native Adaptation

This patch adapts the companion PathWalk utility to the M60.4 runtime protocol and adds a small core safety fix for branch-aware live runtime sessions.

## Accepted changes

- PathWalk enforced mode uses `./cli_embedded/ordo`.
- Legacy `ordo_run.py` launcher is obsolete.
- Runtime views are explicit: `json`, `ordo-code`, `json,ordo-code`.
- Scoring checks `verify-targets`, `verify-session`, `session.ordo.trace`, runtime hashes, and direct `compiled/*` access violations.
- `restore-session` is the native M60.4 command, not a PathWalk fork.
- Branch-aware live runtime sessions prefer persisted `current_node` over unrelated earlier sibling nodes.

## Validation

- PathWalk pytest: 17/17 passed.
- Targeted core tests passed for branch-aware current node, checkpoint discipline, and incremental intake evidence.
- Manual M60 runtime smoke passed with `runtime_view=json,ordo-code`.
