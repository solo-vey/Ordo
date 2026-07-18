# Package Startup Standard

**Milestone:** M66.0 — Package Startup Standard / Startup Package Profile  
**Status:** accepted documentation/schema convention  
**Scope:** Ordo language package conventions and standard applied modules  
**Runtime impact:** none

## Purpose

The Package Startup Standard defines how an Ordo package declares the files, prompts, profile, and validation expectations needed to start using it safely.

It answers a simple operational question:

> When a human, AI assistant, developer, or CLI helper receives a package, which file should be opened first, which startup mode is intended, and which evidence confirms that the package is ready to start?

This standard complements the M64 and M65 layers:

```text
program_contract
→ interaction_model
→ process_rail
→ conversation_semantics
→ program_level_approval_gate
→ prompt_registry
→ startup_package_profile
```

## Problem

Existing packages may contain several start-related files:

- `README.md`
- `START_HERE_RUNTIME_MODE.md`
- `START_PROMPT_RUNTIME_MODE.md`
- `prompts/QUICK_START_PROMPT.md`
- package-specific runtime prompts
- validation profiles
- manifests
- lock files
- compiled runtime artifacts

Without a standard startup declaration, package authors and analysts may not know which entry point is authoritative for a given role or startup mode.

Typical risks:

- the quick-start prompt exists but is not referenced from README/START_HERE;
- a developer uses a human-facing quick prompt as if it were a full runtime prompt;
- runtime package files exist but their readiness gates are unclear;
- package profiles are described informally and drift across packages;
- generated bundles include helpful start files but not a startup contract.

## Standard rule

Every package that is intended for guided use SHOULD declare a `startup_package_profile`.

A startup profile is not an opcode and not runtime execution logic. It is a package-level contract that explains:

1. which startup modes exist;
2. which entry files belong to each mode;
3. which audience each entry file serves;
4. which prompts are intended for copy-paste startup;
5. which validation evidence must exist before the package is considered start-ready;
6. which files are required, recommended, or optional;
7. which files are visible to analysts and which are developer/operator materials.

## Required startup surfaces

A package may support several startup surfaces.

| Surface | Purpose |
|---|---|
| `readme` | Human-readable package overview and navigation |
| `start_here` | Minimal role-aware entry instructions |
| `hp.package.quick_start.v1` | Tiny copy-paste prompt for a new chat/session |
| `hp.runtime.start.v1` | Full runtime-mode prompt or execution handoff |
| `developer_start_prompt` | Developer/maintainer entry prompt |
| `cli_start` | CLI/operator startup instructions |
| `validation_profile` | Declares start-readiness checks |
| `manifest` | Lists files included in the package |
| `lockfile` | Pins generated/runtime package expectations where applicable |

## Startup modes

Recommended startup modes:

| Mode | Meaning |
|---|---|
| `analyst_quick_start` | Small human-facing entry path for normal analyst use |
| `analyst_runtime_mode` | Guided runtime mode with full process behavior |
| `developer_maintenance` | Developer bundle / package maintainer mode |
| `cli_operator` | CLI/helper validation or local package execution mode |
| `review_only` | Read-only package review without state mutation |
| `repair_resume` | Resume an interrupted or failed startup after repair |

## Authority boundary

Startup files may guide package entry, but they do not override:

- `program_contract`;
- nodes and gates;
- state requirements;
- prompt registry authority restrictions;
- manifest/checksum evidence;
- approval/lint gate decisions;
- runtime truthfulness boundaries.

A startup profile may say which startup path is recommended. It must not claim that validation has passed unless supporting evidence exists.

## Relationship to prompt registry

`startup_package_profile` may reference prompt IDs from `prompt_registry`, especially:

- `package_bootstrap` prompts;
- `runtime_start` prompts;
- `repair_helper` prompts;
- `validation_helper` prompts.

The startup profile should not duplicate the full prompt text. It should reference the prompt registry and entry files.

## Relationship to package profiles

`startup_package_profile` is narrower than a package profile.

A package profile describes the package class and composition expectations. A startup package profile describes the entry sequence, startup modes, required files, and start-readiness gates.

## Minimal recommendation

For a standard applied module, the minimum startup package profile should define:

1. package ID and version;
2. default startup mode;
3. `README.md` entry;
4. `START_HERE_RUNTIME_MODE.md` or equivalent;
5. `START_PROMPT_RUNTIME_MODE.md` or equivalent;
6. quick-start prompt if analyst-facing;
7. manifest or lockfile evidence;
8. start-readiness validation checks;
9. statement that startup files do not override process contracts or gates.

## Non-goals in M66.0

M66.0 does not:

- add runtime-core behavior;
- add compiler behavior;
- add CLI commands;
- add opcodes;
- regenerate compiled IR;
- rewrite APF or History Event Factory runtime logic;
- claim deterministic classification of startup intent.
