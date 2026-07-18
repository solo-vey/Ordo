# Chapter 67. APF Language Pattern Extraction

M62.3 does not add a new runtime or rewrite APF. Its task is different: take the ideas discovered during review of `ordo.applied_project_factory` and classify them by maturity level.

The main rule is that APF needing a pattern does not mean the pattern should immediately become an opcode or IR object.

The correct ladder is:

```text
APF need
→ documented APF pattern
→ reusable APF subflow or state convention
→ use in multiple packages
→ lint/check candidate
→ formal language construct
→ IR/runtime object only if truly necessary
```

## Why this matters

When creating applied processes, it is easy to want to formalize everything immediately:

```text
INPUT.POLICY
TERMINAL.OUTPUT.BIND
TREE.AUTHOR.PROGRESSIVE
NODE.REVIEW
FLOW.JOIN
```

But some of these are user-facing authoring workflow. Some are schema conventions. Some are future lint rules. Only a very small subset may eventually become IR-level constructs.

## Current classification

M62.3 classifies APF candidates as:

```text
Documentation pattern
APF reusable subflow
Schema convention
Artifact standard
Rendering standard
Package authoring policy
Lint candidate
Future IR candidate
```

The nearest practical candidates for an APF patch are input policy, output candidate catalog, progressive tree authoring, node/branch review, terminal output binding, and terminal readiness check.

The strongest future IR candidates are `FLOW.JOIN` and `SHARED.TAIL.REFERENCE`, but they require a separate design milestone.

## M62.3 boundary

M62.3 does not perform:

```text
APF YAML rewrite
new opcodes
runtime-core changes
execution/scoring/calibration
watchdog/process-boundary hardening
```

It is only a plan for extracting language patterns from APF experience.

## Next healthy boundary

After M62.3, M62 should close and record:

```text
M62.1 — APF imported
M62.2 — APF documented
M62.3 — APF patterns classified
```

Only then should a separate M63 line open for continued branch review and a scoped YAML patch.
