# A6 — Real Capability Audit

## Status

`passed-with-capability-boundaries`

## Audit basis

The audit inspected the actual Ordo v0.12 pre-release workspace: CLI parser and implementation, runtime/session code, schemas and targeted automated tests. Documentation-only claims were not treated as runtime support.

## Capability matrix

| Capability | Documented | Schema | CLI | Runtime enforced | Tested | APF decision |
|---|---:|---:|---:|---:|---:|---|
| `checkpoint_state_and_forward_blocking` | yes | yes | yes | yes | yes | `adopt-now` |
| `state_snapshots_hash_chain` | yes | yes | yes | yes | yes | `adopt-now` |
| `state_diff` | yes | no | yes | no | yes | `adopt-as-helper` |
| `append_only_restore_session` | yes | yes | yes | yes | yes | `adopt-with-boundary` |
| `backtracking_stale_dependency_invalidation` | yes | yes | no | no | no | `policy-only-pending-implementation` |
| `prompt_registry_stable_ids` | yes | yes | yes | no | yes | `adopt-now` |
| `prompt_application_trace_writer` | yes | yes | no | no | yes | `package-local-evidence-only` |
| `session_trace_and_verify_session` | yes | yes | yes | yes | yes | `adopt-now` |
| `transcript_replay_protocol` | yes | no | no | no | yes | `pilot-only-not-production` |
| `multi_runtime_transcript_replay_acceptance` | yes | no | no | no | no | `blocked` |

## Executed evidence

```text
6 passed, 91 deselected
```

Targeted tests covered checkpoint selection/skip blocking, snapshots, append-only restore, Prompt Registry schema and prompt-trace validation artifacts.

## Accepted for APF now

- earliest-incomplete checkpoint selection and forward blocking;
- runtime state snapshots with tamper-evident hash chain;
- `verify-session`;
- `diff-state` as a deterministic helper/report;
- append-only `restore-session`, with prior history preserved;
- stable semantic Prompt Registry identities and clean-check validation.

## Accepted only with explicit limitations

### Backtracking and stale invalidation

`restore-session` is real and tested, but it is an append-only restore to a prior snapshot. A generalized semantic engine that automatically discovers every dependent APF decision/artifact and marks it stale was not found. APF therefore keeps dependency invalidation as a package/AI-guided contract until a concrete implementation exists.

### Prompt application trace

The language package contains a validated evidence shape (`prompt_id`, `use`, `sha256`, `ordinal`) and tests/examples. No generalized runtime writer was found that automatically writes this evidence for arbitrary applied modules. APF must produce/validate it at package level and must not describe it as core session-trace enforcement.

### Transcript replay

M60.6.4 is an offline synthetic transcript-replay pilot, not a production capability or live-model validation. M60.6.5 multi-runtime expansion is explicitly blocked by a process-boundary hang. Therefore replay does not yet unlock APF real-case validation.

## Backlog effect

- `BL-APF-001`: remains deferred. A6 found a useful pilot protocol, but not a production-ready multi-runtime replay capability.
- `BL-APF-002`: remains deferred. Stable Prompt Registry support is real, but node-bound mini-prompt applicability review was not started.

## Release consequence

A7 may package APF with honest capability labels: `runtime-supported`, `helper-supported`, `package-local`, `policy-only`, `pilot-only`, or `blocked`. It must not collapse these into a generic “supported” status.
