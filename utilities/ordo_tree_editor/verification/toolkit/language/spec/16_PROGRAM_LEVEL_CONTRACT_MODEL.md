# 16. Program-level Contract Model

Status: `M64.1 schema convention`

The Program-level Contract Model defines a package-level contract above nodes, gates, outputs, and templates.
It records how a complete Ordo program should be interpreted, reviewed, validated, and handed off.

## 1. Purpose

The contract answers questions that cannot be safely inferred from graph structure alone:

```text
What package is this?
Which language/runtime line does it target?
How strict is process control?
Who owns decisions: human, AI, or CLI/helper tools?
Which validation commands are expected?
Which review points are mandatory?
```

## 2. Source-level convention

The canonical source-level container is `program_contract`.

```yaml
program_contract:
  program_id: example_process
  module_id: ordo.example_process
  version: 0.1.0
  ordo_version: "0.12"
  lifecycle: draft
  control_level: standard
  execution_mode: full_runtime
```

## 3. Semantic level

In M64.1, the program-level contract is a **schema/documentation convention**, not a new IR opcode.
Compilers and linters may preserve it as metadata, but runtime behavior must not depend on unsupported fields unless the package declares local semantics.

## 4. Recommended validation posture

- Missing `program_contract` in an old package: no blocker.
- Missing `program_contract` in a new `standard_applied_module`: warning.
- Invalid enum value in a declared contract: warning in `light`/`standard`, possible error in future `strict` profile.
- Claiming `full_runtime` without validation/startup evidence: candidate for M64.3 lint/profile rule.

## 5. Relation to future work

M64.2 will document interaction/process-rail/conversation-semantics submodels.
M64.3 will design approval-gate lint/profile behavior.
`FLOW.JOIN` and `SHARED.TAIL.REFERENCE` remain future IR design candidates and are not part of this model.
