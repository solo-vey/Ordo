# BL-BENCH-044 — Benchmark Evidence and Run Acceptance Governance

**Status:** DONE  
**Implemented in:** 1.0.0-alpha.7

Implemented as an enforceable governance layer, not only documentation.

## Canonical rule

A run or Playbook is promoted to canonical evidence only after factual audit, integrity resolution and explicit user confirmation. Generation, file presence, validator PASS or execution summary alone cannot promote evidence.

## Implemented controls

- canonical evidence-base directory initializer;
- immutable run revisions and lifecycle states;
- actual artifact SHA-256 and audit binding;
- three-score contract: Process / Documents / Final;
- confirm, reject, quarantine, supersede and invalidate operations;
- confirmed-only score ledger and comparative scoreboard;
- neutral launch-prompt gate;
- post-RUN_05 Playbook approval-resolution gate;
- versioned sync report, manifest and checksum generation;
- fail-closed command-line validator and acceptance tests.

## Runtime

`tools/manage_benchmark_evidence.py`

Main operations: `init`, `receive`, `audit`, `confirm`, `reject`, `invalidate`, `scoreboard`, `validate`.

## Source traceability

The owner-provided normative document remains unchanged at:

`backlog_attachments/BL-BENCH-044/BENCHMARK_EVIDENCE_AND_RUN_ACCEPTANCE_PROCESS_UA.md`
