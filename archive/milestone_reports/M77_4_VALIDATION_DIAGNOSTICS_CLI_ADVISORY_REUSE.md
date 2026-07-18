# M77.4 — Validation Diagnostics, CLI Integration and Advisory Reuse Detection

Status: PASS

## Implemented

- `validate_flow_reuse()` validates authored `FLOW.JOIN` and `SHARED.TAIL.REFERENCE` declarations.
- Invalid authored reuse fails closed with `FLOW_REUSE_INVALID`.
- `ordo lint` includes a `flow_reuse_validation` subreport.
- Structurally similar linear tails may emit `FLOW_REUSE_CANDIDATE` as `info` only.
- Candidate detection never rewrites source and never changes compile status by itself.
- Diagnostics include candidate node IDs and an explicit author-review recommendation.

## Policy

Ordinary duplicated branches remain valid. Reuse is optional. Only invalid use of the authored reuse constructs is blocking.

## Verification

- M77.0–M77.4 targeted suite: 35/35 PASS.
