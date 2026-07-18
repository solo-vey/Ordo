# M47 — Release Candidate Freeze

Status: **release-candidate frozen**  
Package mode: **source-available preview candidate**  
Tag candidate: `v0.12.0-preview-rc1`  
Publication status: **not published**

M47 freezes the M46.9 pre-release candidate after the contract/artifact/go-no-go validation layer and external audit self-run. This milestone does not add language semantics, CLI behavior, package business logic, or book content. It records the current workspace as the final pre-release candidate before any publication or external handoff decision.

## Included functional baseline

- Process Rail language model.
- AI Ordo Developer and AI Ordo Executor reference flows.
- Semantic JSON IR with contract/artifact coverage primitives.
- Deterministic CLI helper layer.
- `contract → artifact coverage → rendered artifact validation → consistency → go/no-go` pipeline.
- Active reference packages:
  - `packages/ordo_project_builder/`
  - `packages/ordo_hybrid_executor/`
  - `packages/history_event_guided_intake/`

## Freeze rules

After M47, changes should be limited to:

- critical bug fixes;
- documentation wording fixes;
- validation report corrections;
- external audit feedback fixes.

New language primitives, new CLI command families, and new reference package business logic should move to a later milestone after the release candidate is reviewed.

## Validation summary

The release candidate was checked with:

```text
repo-check
CLI unit tests
active package lint/compile/test/coverage
Process Rail helper commands
History Event lock/intake/generate-output/validate-output
validate-artifacts
consistency
go-no-go
```

Result: **passed**.

## Known limitations

- `ordo test` remains a static behavior-validation helper, not a live AI execution runner.
- Some assertions remain structural-only unless their conditions are supported by the current evaluator.
- The archive is a source-available preview candidate, not an open-source release.
- Book PDF was not regenerated after recent markdown updates.
