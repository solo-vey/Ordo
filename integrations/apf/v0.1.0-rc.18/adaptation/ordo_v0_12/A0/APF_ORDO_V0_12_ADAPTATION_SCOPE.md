# APF ↔ Ordo v0.12 Adaptation Scope

Status: `A0 proposed-for-confirmation`

## 1. Baselines

### APF baseline

```text
ordo_applied_project_factory
version: v0.1.0-rc.12-confirmed-closure
scope: creation and governance of Ordo playbook/process packages
```

### Ordo baseline

```text
Ordo language package: v0.12 PRE-RELEASE
handoff date: 2026-07-10
workspace artifact: ordo_github_workspace_v0_12_pre_release_after_full_self_check.zip
```

## 2. Adaptation objective

Bring APF's package contracts and validation model into honest compatibility with the confirmed Ordo v0.12 package/runtime conventions while preserving the accepted APF rc.12 authoring methodology and responsibility boundary.

## 3. In scope

1. Program-level contract metadata and compatibility declarations.
2. Interaction model: human, AI and CLI responsibilities and decision authority.
3. Process rail policy: deviations, resume, backtracking, skip-ahead and dependent-state invalidation.
4. Conversation semantics as declared package policy.
5. Runtime source-of-truth chain: source YAML, compiled JSON IR, run state and generated outputs.
6. Checkpoint and earliest-incomplete-node discipline.
7. Prompt Registry adoption, stable prompt identity and node/artifact prompt references.
8. Controlled prompt application order and package-level prompt evidence.
9. APF validation profile alignment with available parent CLI commands and APF-local helpers.
10. Clean-source, dev/runtime and evidence-package separation.
11. Release hygiene and generated-artifact freshness checks using capabilities that actually exist.
12. Capability audit for replay, snapshots, diffs, trace and restore before deferred APF backlog is reconsidered.
13. Regression protection for all confirmed APF rc.7–rc.12 decisions.

## 4. Out of scope

1. Any change to Ordo language, compiler, IR core, runtime core or parent CLI.
2. New Ordo opcodes or formal language constructs.
3. Deterministic natural-language classification.
4. Promotion of APF-local helpers to required parent CLI commands.
5. Fabrication of runtime/session evidence that current tooling does not produce.
6. Implementation of `BL-APF-001` or `BL-APF-002` during A0.
7. Creation of a real domain playbook.
8. Real analyst intake or execution of a concrete playbook-authoring case.
9. Redesign of accepted APF package-creation methodology without a separately confirmed APF change.
10. Adoption of Ordo backlog items unrelated to APF creation and governance.

## 5. Normative source hierarchy

1. Confirmed Ordo v0.12 source contracts, schemas, CLI documentation and passing tests.
2. Accepted Ordo v0.12 design/schema-convention documents where enforcement is not claimed.
3. APF rc.12 confirmed closure documents and policies.
4. APF source-reference improvement proposals, used only as candidate input and not as accepted APF behavior.
5. Historical reports and examples.

## 6. Capability status vocabulary

| Status | Meaning |
|---|---|
| `runtime-enforced` | Implemented and mechanically enforced by current runtime/CLI. |
| `schema-supported` | Representable and validated by an existing schema/compiler contract. |
| `accepted-convention` | Accepted documentation/source convention, but not fully mechanically enforced. |
| `package-local` | Implemented or evidenced inside APF/package tooling rather than parent runtime/CLI. |
| `documented-only` | Described, but current implementation/evidence is insufficient. |
| `deferred` | Explicitly postponed and must not be claimed as current capability. |
| `unsupported` | No current support found. |
| `audit-required` | Evidence must be checked before assigning a stronger status. |

## 7. Adaptation rules

- Do not convert an accepted convention into a false claim of runtime enforcement.
- Do not make an APF-local command a parent CLI blocker.
- JSON IR and run state control deterministic routing; prompts provide local guidance only.
- Human approval remains mandatory for content and final release decisions.
- Any change to the APF process rail requires explicit human confirmation under existing rc.8 policy.
- Existing APF deferred backlog remains closed until the adaptation and capability audit are complete.

## 8. A0 deliverable boundary

A0 produces only scope, status classification, compatibility gaps and next-patch boundaries. It does not edit APF source packages.
