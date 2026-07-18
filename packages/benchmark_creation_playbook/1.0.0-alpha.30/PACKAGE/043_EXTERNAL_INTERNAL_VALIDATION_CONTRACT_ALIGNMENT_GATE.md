# BL-BENCH-043 — External/Internal Validation Contract Alignment Gate

## Status

**DONE**

## Contract

Every document-generation node and template MUST bind an authoritative external validation contract by immutable contract ID, version and SHA-256. Node-local rules are accepted only after rule-level structural and semantic equivalence is proven.

The gate is fail-closed for missing, weaker, contradictory, stale, wrongly bound or silently overridden rules. Extra internal rules are permitted only when explicitly classified as non-conflicting strengthening rules; extra blocking rules require approval because they may change externally valid outputs into internal failures.

## Required flow

1. Freeze external contract identity and checksum.
2. Extract internal node/template rules.
3. Normalize both rule sets.
4. Map rules by canonical `rule_id`.
5. Compare requirement, condition, severity, blocking behavior, exceptions, lineage and terminal semantics.
6. Block the node when any required rule is absent or semantically weaker/conflicting/stale.
7. Regenerate internal rules from the frozen external contract.
8. Re-run the gate and accept only on zero unresolved blocking differences.
9. Seal an alignment report and bind it to the release gate.

## Implementation

- Policy: `VALIDATION_ALIGNMENT_POLICY.yaml`
- Validator/regenerator: `tools/validate_contract_alignment.py`
- Declaration template: `templates/VALIDATION_ALIGNMENT_BINDING.template.yaml`
- Report schema: `schemas/validation_alignment_report.schema.json`
- Positive, negative, boundary and regeneration fixtures: `fixtures/validation_alignment/`
- Acceptance report: `reports/VALIDATION_ALIGNMENT_ACCEPTANCE_TESTS.json`

## Release gate

Release is blocked when any document-generation node lacks a current PASS report whose external contract checksum, internal rules checksum and node/template identity match the release contents.

## Acceptance evidence

The implementation rejects missing, weakened, contradictory and stale rules; proves equivalent positive/negative/boundary verdicts; regenerates internal rules from the authoritative contract; and passes all acceptance tests.
