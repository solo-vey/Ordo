# Spec 22 — Startup Profile Validation Model

**Milestone:** M66.2

## 1. Model

The startup profile validation model defines a reusable lint/profile layer for packages that declare `startup_package_profile`.

It validates four questions:

1. Can the user or AI agent discover the correct entry point?
2. Do required startup entry files exist?
3. Do referenced startup prompts resolve through `prompt_registry` and manifest coverage?
4. Does the startup surface respect Ordo authority boundaries?

## 2. Scope

In scope:

- profile selection: `light`, `standard`, `strict`;
- severity mapping: `error`, `warning`, `info`;
- readiness decisions: `start_ready`, `start_ready_with_warnings`, `blocked`, `not_applicable`;
- checks for entry files, prompt refs, manifests, checksums, and authority boundaries.

Out of scope:

- runtime execution;
- compiler enforcement;
- CLI implementation;
- new opcodes;
- compiled IR regeneration.

## 3. Profile semantics

`light` is acceptable for drafts and examples.

`standard` is the default for reusable analyst-facing packages.

`strict` is intended for stable or externally shared packages where startup artifacts must be fully covered by manifest/checksum evidence.

## 4. Check families

The model contains these check families:

- shape checks;
- entry-file resolution checks;
- prompt-registry linkage checks;
- manifest/checksum coverage checks;
- authority-safety checks;
- readiness-gate checks.

## 5. Decision function

```text
if any error:
  readiness_decision = blocked
elif any warning:
  readiness_decision = start_ready_with_warnings
elif profile not applicable:
  readiness_decision = not_applicable
else:
  readiness_decision = start_ready
```

## 6. Authority boundary

Startup files and prompts may explain how to begin. They may not:

- bypass gates;
- approve outputs;
- claim validation has passed;
- change state without declared runtime mechanism;
- override `program_contract` or `program_level_approval_gate`.

## 7. M66.2 non-change statement

M66.2 is a documentation/schema/lint-profile milestone only.

It does not change runtime core, compiler, CLI, package execution, or IR semantics.
