# 031. Cross-Variant Comparison

**Version:** `1.0`  
**Backlog:** `BL-BENCH-031`  
**Status:** canonical contract

## 1. Purpose

Cross-variant comparison determines how `PV-YAML`, `PV-STRUCTURED`, `PV-HISTORICAL` and `PV-DIRECT` differ under equivalent benchmark conditions without hiding lineage, Driver or contamination differences.

## 2. Comparable cohort gate

Two records may be compared directly only when all mandatory cohort dimensions match or have an approved normalization:

- same test case and version;
- same RUN and RUN contract version;
- equivalent executor model/configuration and tool permissions;
- same evaluation contract versions;
- clean blind-isolation status;
- equivalent source evidence cutoff;
- compatible terminal path;
- no unresolved contamination;
- package variant identity and lineage verified.

Otherwise comparison is `conditional` or `excluded`, with reasons.

## 3. Standard comparison dimensions

### 3.1 Process determinism

Measured from route correctness, required obligations, corrections, terminal disposition and repeated-attempt variance.

### 3.2 Document quality depth

Uses artifact-specific final scores and coverage; does not substitute generic document length.

### 3.3 Executability

Assesses whether generated instructions/QA/automation are actionable under their artifact contracts.

### 3.4 Correction resilience

Measures invalidation, regeneration and version-bound approval handling, especially in `RUN_04`.

### 3.5 Failure honesty

Measures correct blocked/exhausted/no-go behavior without fabricated completion.

### 3.6 Portability

Assesses dependency on special runtime/tooling, package readability and transferability.

### 3.7 Resource footprint

Records package bytes, file count, YAML node count where applicable, instruction length and execution token/time metrics when reliably available. Resource metrics are descriptive unless an approved scoring contract assigns weight.

### 3.8 Stability

Uses repeated attempts to calculate score variance, terminal consistency and artifact-set consistency.

## 4. Fairness rules

- compare the same intended capability, not merely same filenames;
- do not penalize a variant for intentionally absent internal Ordo structure when its contract forbids it;
- do not reward hidden leakage or evaluator hints;
- do not merge scores across different Driver families without showing Driver as a dimension;
- report sample sizes and uncertainty;
- retain process and document dimensions separately;
- do not infer causality from one attempt.

## 5. Comparison output

A cross-variant report contains:

- cohort definition and exclusions;
- per-attempt matrix;
- per-variant aggregates and dispersion;
- dimension-by-dimension findings;
- evidence references;
- limitations and uncertainty;
- no unsupported “winner” conclusion.

## 6. Winner declaration gate

A winner may be declared only if:

- the comparison objective and primary metric were fixed before examining results;
- cohorts are comparable;
- minimum sample size policy is satisfied;
- no critical contamination exists;
- uncertainty does not reverse the conclusion;
- all ties and trade-offs are disclosed.

Without those conditions, output must say `insufficient evidence for a single winner`.
