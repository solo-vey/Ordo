# M48 Final Handoff — Ordo v0.12.0-preview-rc1

## Handoff status

Status: `final handoff package`

Release candidate: `v0.12.0-preview-rc1`

Publication mode: source-available preview candidate; not an open-source release.

M48 does not change runtime behavior. It packages the M47 release candidate into a reviewer-ready handoff with a clear route, review questions, and final validation evidence.

## What changed in M48

- Added reviewer-facing final handoff documents.
- Added a final handoff report.
- Added a design decision for the final handoff package.
- Updated README and CHANGELOG to point reviewers to the handoff route.
- Updated book source Markdown only; PDF was not regenerated.

## What did not change

- No new CLI commands.
- No new language semantics.
- No package business logic changes.
- No generated PDF book update.
- No publication push or Git tag.

## Main review objects

- `language/` — language and IR model.
- `cli/` — deterministic helper layer.
- `packages/ordo_project_builder/` — AI Ordo Developer example.
- `packages/ordo_hybrid_executor/` — AI Ordo Executor example.
- `packages/history_event_guided_intake/` — analytical regression/example package.
- `docs/external_audit/` — audit prompts and checklist.
- `docs/release_candidate/` — M47 freeze evidence.
- `docs/final_handoff/` — M48 handoff route.

## Validation expectation

The final handoff is valid when:

- active packages pass lint/compile/test/coverage;
- source archive hygiene passes before install/test artifacts are generated;
- History Event generated artifacts pass validate-output, validate-artifacts, consistency, and go-no-go;
- no generated package artifacts are carried in the source archive except `.gitkeep` placeholders;
- reviewer-facing docs point to real files.

## Known limitations

- `ordo test` is a static structural runner, not live AI behavior execution.
- Assertions still distinguish behavioral evaluation from structural-only checks.
- The preview license remains source-available, not open-source.
- External review feedback may still create follow-up M49+ work.

