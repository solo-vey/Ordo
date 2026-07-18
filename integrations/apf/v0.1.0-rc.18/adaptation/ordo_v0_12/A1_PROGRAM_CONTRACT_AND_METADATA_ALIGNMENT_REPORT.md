# A1 — Program Contract and Metadata Alignment Report

## Result

Status: `passed-working-state`

APF now contains a canonical Ordo v0.12-aligned program-level contract and synchronized top-level metadata.

## Added

- `docs/APF_PROGRAM_LEVEL_CONTRACT.yaml`
- `docs/APF_PROGRAM_LEVEL_CONTRACT_ALIGNMENT_POLICY.md`
- this A1 report

## Updated

- `README.md`
- `CURRENT_STATE.md`
- `START_NEXT_MODEL.md`
- `VALIDATION_REPORT.json`

## Decisions

- confirmed baseline remains `v0.1.0-rc.12-confirmed-closure`;
- current working milestone is `A1-applied`;
- lifecycle is `release-candidate`;
- control level is `standard`;
- current execution mode is `chat_internal`;
- contract profile is `standard_applied_module`;
- schema enforcement is declared as `documented-convention`;
- no full-runtime claim is made;
- no APF authoring-flow change was introduced.

## Deferred to later milestones

- detailed interaction authority and process rail: A2;
- Prompt Registry: A3;
- IR/state/checkpoint alignment: A4;
- validation profile hardening: A5;
- real capability audit: A6;
- release closure: A7.
