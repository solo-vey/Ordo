# Reviewer Start Here — Ordo v0.12.0-preview-rc1

You are reviewing an Ordo pre-release candidate, not a published open-source release.

## What Ordo is

Ordo is a hybrid AI process language centered on Process Rail. AI remains the active interpreter/developer/executor, while the language and CLI helper layer provide deterministic checks for gates, state, coverage, generated artifacts, consistency, and go/no-go decisions.

## What to review first

1. `README.md` — overview and current status.
2. `language/` — Ordo language, Semantic JSON IR, contracts, artifact coverage, go/no-go model.
3. `cli/docs/` — deterministic helper commands.
4. `packages/ordo_project_builder/` — canonical Developer example.
5. `packages/history_event_guided_intake/` — analytical package regression/example.
6. `docs/external_audit/` — audit checklist and prior self-audit.
7. `docs/release_candidate/` — freeze note for `v0.12.0-preview-rc1`.

## Minimal local verification

Run source hygiene before install/tests:

```bash
cd cli
python -m pip install -e .
ordo repo-check ..
python -m unittest discover -s tests
```

Then run active package checks:

```bash
for p in ../packages/ordo_project_builder ../packages/ordo_hybrid_executor ../packages/history_event_guided_intake; do
  ordo lint "$p"
  ordo compile "$p"
  ordo test "$p"
  ordo coverage "$p"
done
```

For generated artifact validation, use the History Event example:

```bash
ordo intake ../packages/history_event_guided_intake --answers ../packages/history_event_guided_intake/run_inputs/intake_success.yaml --non-interactive
ordo generate-output ../packages/history_event_guided_intake
ordo validate-output ../packages/history_event_guided_intake
ordo validate-artifacts ../packages/history_event_guided_intake
ordo consistency ../packages/history_event_guided_intake
ordo go-no-go ../packages/history_event_guided_intake
```

## Expected status

The expected final result is `go` for the active regression package and no blockers in the release-candidate handoff.

