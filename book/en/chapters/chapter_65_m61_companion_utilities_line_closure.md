# Chapter 65. Closing M61: A Stable Companion Utilities Layer

M61 completes the layer of utilities that accompany Ordo without becoming runtime core.

This layer supports practical work with the language: inspect the tree, understand paths, generate clean/noise test cases, and prepare human-readable review cards.

## What belongs to the stable layer

At the M61 boundary, two companion utilities are considered stable.

**PathWalk** is responsible for the artifact-only testing/review flow:

```text
source/program.ordo.yaml
  → graph summary
  → terminal paths
  → clean cases
  → bounded noise cases
  → review cards
```

**Visual Graph Generator** is responsible for the read-only visualization flow:

```text
source/program.ordo.yaml
  → Mermaid / SVG / PNG graph
  → subtree / context / path views
  → optional annotation overlays
```

## What this layer does not do

Companion utilities do not execute a runtime session and do not prove that a model traversed a process correctly. They help authors and reviewers see structure, prepare scenarios, and inspect logic manually.

The important boundary is:

```text
visual/review artifacts ≠ runtime execution evidence
```

## Why M61 should close

After M61.3, a complete practical route exists:

```text
YAML → visual graph → paths → cases → review cards
```

Adding more small noise variants or partial integrations without a strong new milestone would reopen an endless improvement block. M61 therefore closes as a stable utility layer.

## What remains for the future

The backlog retains:

- runtime execution of generated testcases;
- scoring and calibration for executed cases;
- process-boundary/watchdog hardening;
- `backtrack` and `correction_backtrack` patterns;
- possible future utility unification only when it has a separate justification.

These are not blockers for M61. They should become separate future milestones.
