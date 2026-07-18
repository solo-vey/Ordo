# M87.0 — Ordo vs Plain Prompt A/B Benchmark Design Audit

Status: **completed**

Relevant files scanned: **827**

## Existing strengths

- Canonical evidence schema.
- Provider-neutral driver.
- Replay and artifact-integrity checks.
- Prompt/input/output hashes, model identity, retries and timestamps.
- Adversarial mismatch taxonomy.

## Critical design gaps

1. No canonical `pair_id` linking A and B runs.
2. Plain Prompt and Ordo arms are not frozen.
3. No shared paired task dataset.
4. No scoring rubric across correctness, completion, fabrication, state protection, recovery and overhead.
5. No blind-scoring protocol.
6. No randomization or counterbalancing policy.
7. No predefined statistical analysis plan or closure thresholds.
8. No contamination controls.
9. No cost-normalized latency/token reporting.

## Decision

BL-ORDO-018 is ready to proceed, but paired execution must not start before protocol, rubric, contamination controls and analysis plan are frozen.

Next step: **M87.1 — paired A/B protocol and scoring rubric**.
