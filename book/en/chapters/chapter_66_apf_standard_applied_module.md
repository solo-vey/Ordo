# Chapter 66. APF as a Standard Applied Module

APF, or `ordo.applied_project_factory`, is not a utility and not runtime core. It is a standard applied module distributed with the Ordo language package that helps create or correct other Ordo processes and playbooks.

Its place in the package is:

```text
packages/ordo_applied_project_factory/
```

## Why APF is needed

An ordinary user or PM should not have to write `source/program.ordo.yaml` by hand. APF guides them through human review of the process:

```text
process goal
→ process type
→ roles
→ input policy
→ output catalog
→ decision tree
→ node/branch review
→ terminal output binding
→ source YAML generation
→ validation / handoff
```

The main idea is that the user confirms a human understanding of the process, and the model converts that understanding into Ordo source / IR.

## How APF differs from utilities

Visual Graph Generator and PathWalk help inspect a process from the outside. APF is the process for creating processes.

```text
APF = standard applied module
Visual Graph = read-only renderer
PathWalk = testcase/review artifact generator
Ordo CLI = deterministic validation/runtime tooling
```

## How to review APF

After import, APF can be analyzed through the same companion route already present in the package:

```text
packages/ordo_applied_project_factory/source/program.ordo.yaml
  → Visual Graph Generator
  → PathWalk real-module-graph
  → PathWalk real-module-paths
  → PathWalk clean/noise cases
  → PathWalk review cards
```

This does not replace source YAML or JSON IR. These are review aids that help expose structure, terminal paths, and scenarios.

## M62.2 boundary

M62.2 only documents APF as a standard module. It does not rewrite APF branches, introduce new opcodes, or execute/score generated testcases.

The next logical step is to classify APF language-pattern candidates: what remains a documentation pattern, what becomes an APF subflow, what needs a schema convention, and what may eventually become an IR/runtime construct.

## Important PathWalk clarification

The full `graph → paths → clean/noise cases → review cards` route is stable for processes whose terminal paths can be enumerated without unresolved cycles. APF itself is a self-hosted authoring process with review loops, so for imported `v0.1.0-alpha.14`, the PathWalk graph summary works but terminal-path/testcase generation for APF itself may be blocked by cycle edges. This is not an M62.2 error: adapting APF to cycle-aware testcase generation must be a separate future step.
