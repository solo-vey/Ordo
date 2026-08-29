# Language/tooling -> Editor verification integration contract

## Goal

When a new Ordo language/tooling package adds, removes, or changes verification capabilities, an Editor build should update the verification page **without adding check names to Editor UI code**.

## Required build procedure

A model or build process assembling the Editor from a language/tooling package MUST:

1. Inspect the language/tooling verification catalog, CLI help, runner scripts, and verification modules.
2. Copy the executable dependencies required by those checks into `utilities/ordo_tree_editor/verification/toolkit/` (or replace that snapshot atomically).
3. Reconcile `utilities/ordo_tree_editor/verification/checks/*.json` with the capabilities actually present in the copied toolkit.
4. Create one descriptor per user-visible verification capability.
5. Never silently delete a previously known descriptor. If a check no longer exists, remove it only when the source tooling confirms removal; record that change in release notes.
6. Mark checks requiring context that cannot be inferred from a loaded playbook using `requires` instead of hard-coding UI exclusions.
7. Prefer safe, deterministic, read-only commands. Commands that create release archives or require destructive/mutating context must be conditional (`requires: ["release_context"]`) rather than run automatically.
8. Validate every descriptor against `check_descriptor.schema.json`.
9. Run a discovery test proving the catalog visible through `/api/verification-catalog` exactly matches the descriptor directory.
10. Run a smoke verification against at least one fixture playbook and prove progress/status transitions are emitted sequentially.
11. Update `VERIFICATION_SOURCE.json` with the language/tooling source version, toolkit manifest hash, and integration timestamp/build identifier.

## Model instructions for future automatic integration

When you are updating the Editor from a newer Ordo language/tooling package:

- Do not infer checks only from filenames. Read the tooling catalog/CLI/specification and executable entry points.
- Treat the language/tooling package as source of truth for verification semantics.
- Do not reimplement a language verification in JavaScript or Editor-specific Python when the tooling already provides it.
- Add/modify descriptors rather than branching the verification UI.
- Preserve check IDs when semantics remain compatible so historical verification evidence stays comparable.
- If a command gains required arguments, reflect them with `requires` and mark it `SKIPPED` when the loaded playbook does not supply them.
- If a new safe check can run solely from `{package_root}`, enable it for the one-click suite automatically.
- If applicability can be detected from package files, use declarative file requirements rather than playbook/domain names.
- Never add domain-specific values to Editor core.
- After integration, produce a catalog diff: added / removed / changed checks.

## Status semantics

- `PASS`: command completed successfully (exit code 0 / internal validation passed).
- `FAIL`: verification executed and found a verification failure.
- `ERROR`: the verification mechanism itself could not run (timeout, missing executable, malformed descriptor, internal exception).
- `SKIPPED`: capability is known but not applicable or requires missing external context.

A skipped check must not be presented as passed.

## Portable executable contract

Verification descriptors MUST remain platform-neutral. For Python checks, the first command token SHOULD be `python` or `{python}`; the Editor verification runner resolves it to `sys.executable` at runtime. Do not hard-code an absolute interpreter path, virtualenv path, or assume `python`/`python3` exists on PATH. Future descriptor generators must preserve this rule.


## Evidence applicability

A check that depends on runtime/session evidence MUST declare `evidence_requirement` in its descriptor. The one-click source verification runner skips such a check when the required evidence is absent instead of reporting a playbook FAIL.

## Generated verification reports

Checks SHOULD emit machine-readable reports under the subject package `reports/` or runtime report locations. The Editor embeds generated/updated reports into the verification result as evidence so UI, JSON export, and model explanations can use the actual report rather than only stdout/stderr.


## SKIPPED reason classification

Descriptors that can be conditionally skipped SHOULD declare `skip_kind`. Supported Editor-facing kinds include `not_applicable`, `needs_runtime_evidence`, `needs_selected_gate`, `needs_bindings_context`, `needs_template_context`, `needs_tree_module_context`, `release_only`, `toolkit_only`, `unsafe_one_click`, `missing_optional_dependency`, and `missing_required_context`. The Editor keeps the machine status as `SKIPPED` but presents the reason label to the user.
