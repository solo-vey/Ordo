# 018. Preflight Integrity Gate

**Backlog task:** `BL-BENCH-018`  
**Status:** implemented deterministic gate contract

## 1. Purpose

Prevent invalid, contaminated or non-reproducible attempts from starting.

## 2. Mandatory checks

### Identity and availability

- benchmark suite, test case, RUN, package variant and attempt IDs are present;
- referenced RUN and package variant exist in active registries;
- selected Driver binding is `supported`;
- versions are mutually compatible.

### Integrity

- package archive/file hashes match the immutable manifest;
- scenario contract, Driver contract and isolation manifest hashes are recorded;
- no expected file is missing;
- no unapproved file is present in executor-visible context.

### Blindness and residue

- evaluator-only and Driver-private files are absent from executor-visible workspace;
- output directory is new or empty;
- no previous outputs, logs, scores, prompts or diagnostic residue are present;
- environment does not expose historical benchmark registry to the executor.

### Runtime readiness

- output path is writable;
- log sink can append and preserve order;
- terminal-disposition writer is available;
- attempt clock/time source and correlation ID are initialized.

## 3. Result states

- `passed` — execution may begin;
- `blocked_integrity` — hash/manifest/version failure;
- `blocked_isolation` — leakage or residue detected;
- `blocked_binding` — unsupported/hybrid Driver binding;
- `blocked_environment` — output/log/runtime prerequisite unavailable.

No blocked state may be converted to passed by narrative explanation. A corrected launch requires a new signed preflight record; material changes require a new `attempt_id`.

## 4. Evidence

Every check records:

```text
check_id, status, expected, observed, evidence_reference, timestamp
```

The report is machine-readable and sealed before first executor interaction.

## 5. Gate condition

```text
all mandatory checks passed
AND no blocker exists
AND executor-visible allowlist equals actual exposure
```
