# Spec 21 — Package Startup Model

**Milestone:** M66.0  
**Status:** specification chapter / schema convention  
**Runtime impact:** none

## 1. Overview

The Package Startup Model defines the standard contract for package entry points and start-readiness.

A package may contain many helpful files, but the startup model explains which ones are authoritative for starting a session, which are role-specific, and which validation evidence must exist before a package claims it is ready to start.

## 2. Core object

The core object is `startup_package_profile`.

It declares:

- package identity;
- default startup mode;
- supported startup modes;
- startup entry files;
- readiness gates;
- authority boundaries.

## 3. Relationship to earlier specs

The startup model builds on:

- Spec 16 — Program-level Contract Model;
- Spec 17 — Interaction / Process Rail / Conversation Model;
- Spec 18 — Program-level Approval Gate Model;
- Spec 19 — Prompt Registry Model;
- Spec 20 — Prompt Registry Validation Model.

The startup model does not replace these specs. It adds a package-entry layer above them.

## 4. Startup mode semantics

Startup mode describes how a package is entered, not how it executes internally.

Examples:

- `analyst_quick_start` starts with a short copy-paste prompt;
- `analyst_runtime_mode` starts with the full runtime-mode prompt;
- `developer_maintenance` starts with developer bundle instructions;
- `cli_operator` starts with CLI/helper instructions;
- `review_only` starts a non-mutating review session;
- `repair_resume` resumes startup after a failed readiness check.

## 5. Readiness gates

Readiness gates are lint/profile checks that confirm startup files and references are coherent.

Required standard checks include:

- required startup files exist;
- default startup mode exists;
- prompt IDs resolve when startup mode references prompts;
- quick-start prompt is discoverable for analyst-facing packages;
- authority boundary is explicit;
- manifest/lockfile coverage is declared when applicable.

## 6. Authority boundary

Startup files may guide entry. They must not override process authority.

They cannot:

- bypass gates;
- mutate state silently;
- claim validation success without evidence;
- override `program_contract`;
- override prompt registry state-change policies;
- replace approval-gate decisions.

## 7. Validation profile behavior

Recommended behavior:

- `light`: check required entry files and default mode only;
- `standard`: also check prompt references, quick-start discoverability, and authority boundary;
- `strict`: also check manifest/lockfile coverage, unused start files, role drift, and startup prompt length warnings.

## 8. Non-runtime status

M66.0 introduces no runtime opcode or compiler behavior. Existing packages can adopt the startup model gradually.
