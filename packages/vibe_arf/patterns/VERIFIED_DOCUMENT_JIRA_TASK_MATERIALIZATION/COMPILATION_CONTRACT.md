# Compilation contract — VERIFIED_DOCUMENT_JIRA_TASK_MATERIALIZATION v1.1

This pattern separates **canonical process semantics** from **editor-executable routing syntax**.

`outcome_edges` in `EXECUTION.template.yaml` are the semantic source of truth. They describe which outcomes exist and where each outcome must go. They are **not permission to emit an `outcomes:` structure directly into a compiled Vibe/Ordo playbook** unless the target compiler explicitly supports that route shape.

## Required lowering

- One unconditional successor → `next`.
- Question / human interaction that resumes → `on_answer.next`.
- Binary deterministic branch → `on_pass` / `on_fail`.
- Enum or other multi-outcome branch → write/evaluate the canonical discriminator and lower to explicit deterministic cascade gates. Each exact canonical token keeps its original destination. Unknown, empty, contradictory, or unsupported values fail closed.
- Model-produced classifications must not route implicitly. Persist a canonical discriminator value, then use deterministic routing.

## Mandatory compiler preflight

Before a generated playbook is delivered, mechanically verify: YAML parse; unique executable IDs; all targets resolve; every non-terminal has a compiler-valid outgoing route; full reachability from the declared entry node; canonical outcome coverage is preserved; exact enum semantics are preserved; and the target editor/runtime-plan validator accepts the package.

This contract was added after a dogfood finding where semantically correct abstract `outcomes` were not recognized as executable routes by the target editor, producing dead non-terminals and a truncated reachable graph.
