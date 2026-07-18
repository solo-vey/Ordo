# Chapter 78. APF Replay, Prompt Registry, and Internal Mini-prompts

M78 evaluates APF not only with static tests but through a real process-creation scenario. The goal is to observe the analyst experience: where the process is clear, where unnecessary friction appears, and where the runtime or prompt layer encourages undesirable model behavior.

## Real-case replay

APF replay takes a real case through the existing process rails and records:

```text
active step
analyst input
classification
state mutation
transition
friction finding
```

This is not a replacement for a benchmark. Replay is a product/process review of a specific applied module.

## Prompt Registry reconciliation

As APF evolved, different prompts appeared: startup prompts, runtime prompts, handoff prompts, and internal task-specific prompts.

The Prompt Registry makes the following visible for every prompt:

```text
prompt id
purpose
owner layer
version
entry condition
expected output
replacement/deprecation relation
```

Duplicate or obsolete prompts must not remain silently active.

## Internal mini-prompts

M78 also reviews where an internal mini-prompt is genuinely useful. A mini-prompt is appropriate for a bounded model-assisted task with a clear input/output contract.

It must not replace:

```text
runtime transition rules
gates
state contracts
compiler validation
deterministic CLI checks
```

The main principle is:

```text
use mini-prompts for bounded model work;
use APF/runtime contracts for process control.
```
