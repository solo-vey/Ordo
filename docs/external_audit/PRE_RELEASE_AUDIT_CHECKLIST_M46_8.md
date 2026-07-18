# Ordo v0.12 M46.8 Pre-release Audit Checklist

This checklist is for manual or AI-assisted external review of the Ordo pre-release candidate.

## 1. Archive structure

- [ ] Root contains `.github/`, `book/`, `cli/`, `docs/`, `language/`, `packages/`, and expected metadata files.
- [ ] Root does not contain legacy `dashboards/`, `site/`, `site_publish/`, `catalogs/`, `playbooks/`, `publication/`, or `template_registry/`.
- [ ] Root does not contain generated packaging metadata such as `cli/ordo_cli.egg-info/`.
- [ ] Package source directories do not carry stale generated files in `compiled/`, `reports/`, `runtime/`, or `generated_outputs/` except `.gitkeep`.

## 2. CLI baseline

From `cli/`:

```bash
PYTHONDONTWRITEBYTECODE=1 ordo repo-check ..
python -m pip install -e .
ordo --version
python -m unittest discover -s tests
```

Expected:

- [ ] CLI installs.
- [ ] `PYTHONDONTWRITEBYTECODE=1 ordo repo-check ..` passes on a clean source archive before install/tests.
- [ ] If `repo-check` is run after install/tests, generated metadata is cleaned first or the source-hygiene failure is treated as expected.
- [ ] Unit tests pass.
- [ ] `ordo test` output says `[static mode]`.

## 3. Active reference packages

Run for each active package:

```bash
ordo lint ../packages/ordo_project_builder
ordo compile ../packages/ordo_project_builder
ordo test ../packages/ordo_project_builder
ordo coverage ../packages/ordo_project_builder

ordo lint ../packages/ordo_hybrid_executor
ordo compile ../packages/ordo_hybrid_executor
ordo test ../packages/ordo_hybrid_executor
ordo coverage ../packages/ordo_hybrid_executor

ordo lint ../packages/history_event_guided_intake
ordo compile ../packages/history_event_guided_intake
ordo test ../packages/history_event_guided_intake
ordo coverage ../packages/history_event_guided_intake
```

Expected:

- [ ] All active packages pass lint/compile/test/coverage.
- [ ] `ordo_hybrid_executor` uses `self_consistency + repeated_model_judgment`.
- [ ] Compile does not generate op-codes missing from `language/registry/OPCODE_CATALOG.md`.

## 4. Generated artifact validation flow

For `history_event_guided_intake`:

```bash
ordo intake ../packages/history_event_guided_intake \
  --answers ../packages/history_event_guided_intake/run_inputs/intake_success.yaml \
  --non-interactive
ordo generate-output ../packages/history_event_guided_intake
ordo validate-artifacts ../packages/history_event_guided_intake
ordo consistency ../packages/history_event_guided_intake
ordo go-no-go ../packages/history_event_guided_intake
```

Expected:

- [ ] Generated Passport contains event identity, source/trigger rules, HistoryEvent output contract, normalization, and test strategy.
- [ ] Generated Jira contains test deliverables and acceptance criteria.
- [ ] Generated Implementation Prompt mentions unit tests and paired markdown test documentation when required.
- [ ] Generated QA Package includes positive/negative trigger cases and empty/null/missing transitions.
- [ ] `validate-artifacts` writes `reports/artifact_validation_report.json`.
- [ ] `consistency` writes `reports/CONSISTENCY_CHECK_REPORT.json`.
- [ ] `go-no-go` writes `reports/GO_NO_GO_REPORT.json` and returns `go` for the valid fixture.

## 5. Negative coverage expectations

Verify tests or fixtures cover these failure classes:

- [ ] Missing confirmed field in required artifact -> `ORDO-COV-002`.
- [ ] Candidate/proposed value rendered as confirmed -> `ORDO-COV-003`.
- [ ] Cross-artifact mismatch -> `ORDO-COV-004`.
- [ ] Missing confirmed contract artifact mapping -> `ORDO-COV-001`.
- [ ] Test strategy confirmed but absent from Passport/Jira -> `ORDO-COV-009`.

## 6. Documentation and book source

- [ ] `language/CONTRACTS.md` exists.
- [ ] `language/ARTIFACT_COVERAGE.md` exists.
- [ ] `language/GENERATED_ARTIFACT_VALIDATION.md` exists.
- [ ] `language/CONSISTENCY_CHECK_REPORT.md` exists.
- [ ] `language/GO_NO_GO.md` exists.
- [ ] `cli/docs/VALIDATE_ARTIFACTS_M46_3.md` exists.
- [ ] `cli/docs/CONSISTENCY_M46_4.md` exists.
- [ ] `cli/docs/GO_NO_GO.md` exists.
- [ ] `cli/docs/GO_NO_GO_M46_5.md` compatibility pointer exists.
- [ ] `book/source/chapters/chapter_41_contract_artifact_coverage_go_no_go.md` exists.
- [ ] PDF book regeneration is not required for this check.

## 7. Final verdict

Use:

```text
go                 no blocking issues
no_go              at least one blocker
go_with_warnings   usable pre-release, but non-blocking issues remain
```

