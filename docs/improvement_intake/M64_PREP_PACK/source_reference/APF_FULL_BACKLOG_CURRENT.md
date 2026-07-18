# APF Full Backlog — Current Ordered Backlog

Generated: 2026-07-09T16:25:00+02:00
Scope: Ordo Applied Project Factory base package and companion utilities.
Status: transfer snapshot for next chat.

## Ordering principle

```text
already implemented → rc.4 SVG utility → post-SVG compile/start-prompt layer → later tooling
```

---

# A. Implemented / closed

## DONE-RC2-01 — PACKAGE_COMPOSITION_GATE

Status: implemented in `v0.1.0-rc.2`.

Final package assembly is blocked unless executable model, templates, derived artifacts, manifest and validation reports are complete and synchronized.

## DONE-RC3-P1 — Explicit execution mode declaration

Status: implemented in `v0.1.0-rc.3-p1`.

APF must record `source-authoring`, `compiled-runtime`, or `hybrid` at process start.

## DONE-RC3-P2 — COMPILED_RUNTIME_USAGE_GATE

Status: implemented in `v0.1.0-rc.3-p2`.

APF verifies compiled runtime existence/usage/bypass reason and prevents false runtime-ready status.

## DONE-RC3-P3 — RUNTIME_COMPILATION_GATE

Status: implemented in `v0.1.0-rc.3-p3`.

APF verifies compiled artifacts, runtime config, manifest, trace/status and hashes before runtime-ready status.

## DONE-RC3-P4 — Hybrid mode as preferred operating model

Status: implemented in `v0.1.0-rc.3-p4`.

Hybrid mode is preferred but non-intrusive: runtime controls traversal/state/gates; authoring mode only for APF process changes; normal analyst answers do not trigger recompilation; runtime checks only at lifecycle control points.

## DONE-RC3-P5 — DERIVED_ARTIFACT_SYNC_GATE

Status: implemented in `v0.1.0-rc.3-p5`.

After authoritative model changes, derived artifacts must be regenerated, confirmed current, or explicitly marked stale/omitted/not applicable before final package composition.

## DONE-RC3-P6 — Delta backlog convention

Status: implemented in `v0.1.0-rc.3-p6`.

Purpose: standardize how improvement delta files are accepted, classified, ordered, and transferred across chats.

Implemented artifacts:

```text
docs/DELTA_BACKLOG_CONVENTION_POLICY.md
backlog/APF_DELTA_BACKLOG_REGISTER.md
G_DELTA_BACKLOG_ITEM_CLASSIFIED
G_DEFERRED_DELTA_ITEMS_PRESERVED_FOR_TRANSFER
G_DELTA_BACKLOG_ORDER_PRESERVED
G_DELTA_SOURCE_FILES_INCLUDED_IN_TRANSFER_PACKAGE
A_DELTA_FILES_MUST_NOT_BE_LOST_BETWEEN_CHATS
```

---

# B. Next immediate item — rc.4 SVG graph generator utility package line

## RC4-SVG-01 — Packaged SVG graph generator utility

Priority: high.  
Status: next recommended implementation step.

Important clarification: this is **not Excel/CSV export**.

APF packages should include or bundle the visual graph generator utility needed to produce SVG drawings of the current decision tree. The purpose is to let APF:

```text
- show the analyst the current tree structure during execution;
- generate SVG drawings from the current tree/model;
- include SVG tree drawings in the resulting playbook/factory package.
```

Expected package behavior:

```text
- dev package includes graph generator utility;
- full workspace includes graph generator utility;
- runtime package includes it if runtime needs to show/generate SVG during analyst execution;
- generated SVG artifacts are listed in MANIFEST and validation reports.
```

## RC4-SVG-02 — SVG graph generation policy

Priority: high.

Define when SVG is generated:

```text
- on request during analyst process;
- at lifecycle checkpoints;
- before final package assembly;
- after tree/process model changes.
```

Avoid generating SVG after every analyst answer unless explicitly requested.

## RC4-SVG-03 — Graph profiles

Priority: medium-high.

Potential profiles:

```text
full
current-tree
focused-branch
terminal-paths
gates-view
artifacts-view
```

## RC4-SVG-04 — Visual artifact provenance

Priority: medium-high.

Each SVG artifact should record:

```text
source model path/hash
projection path/hash
utility name/version
render mode/profile
command/options
output path
timestamp
```

## RC4-SVG-05 — SVG inclusion gate

Priority: high if SVG is part of package output.

Gate should verify requested SVG artifacts exist, match current model/projection, are included in MANIFEST, or are explicitly omitted/not-applicable.

---

# C. Post-SVG backlog from compile/start-prompt delta

Source delta: `APF_BASE_PACKAGE_DELTA_INSTRUCTIONS_COMPILE_AND_START_PROMPT.md`.

These items are intentionally placed after the SVG graph-generator utility unless a compile/startup blocker is discovered earlier.

## FUTURE-COMPILE-01 — Compile capability must be included in base APF package
Priority: high. Decision status: implemented in `0.1.0-rc.4-post-svg`.

## FUTURE-COMPILE-02 — COMPILE_UTILITY_DISCOVERY_GATE
Priority: high. Decision status: implemented in `0.1.0-rc.4-post-svg`.

## FUTURE-COMPILE-03 — Runtime compilation verification hardening
Priority: high. Decision status: implemented in `0.1.0-rc.4-post-svg` by binding runtime-ready claims to runtime compilation/package profile evidence.

## FUTURE-PROFILE-01 — PACKAGE_PROFILE_GATE
Priority: high. Decision status: implemented in `0.1.0-rc.4-post-svg`.

## FUTURE-START-01 — Start prompt required for every generated full playbook/factory package
Priority: high. Decision status: implemented in `0.1.0-rc.4-post-svg`.

## FUTURE-START-02 — Human start guide required
Priority: high. Decision status: implemented in `0.1.0-rc.4-post-svg`.

## FUTURE-START-03 — README startup section required
Priority: high. Decision status: implemented in `0.1.0-rc.4-post-svg`.

## FUTURE-START-04 — START_PROMPT_PACKAGING_GATE
Priority: high. Decision status: implemented in `0.1.0-rc.4-post-svg`.

## FUTURE-START-05 — README_STARTUP_SECTION_GATE
Priority: high. Decision status: implemented in `0.1.0-rc.4-post-svg`.

---

# D. Later tooling / hardening backlog

## FUTURE-HASH-01 — Checksum-based derived artifact stale detection
Priority: medium-high. Decision status: implement-later.

## FUTURE-MANIFEST-01 — Executable manifest-vs-archive checker
Priority: medium-high. Decision status: implement-later.

## FUTURE-LIVE-01 — Real APF module test-case generation utility
Priority: medium. Decision status: defer.

## FUTURE-DOCS-01 — Book/chapter integration
Priority: medium. Decision status: implement-later.


---

# E. Future base-process program-level metadata backlog

Source delta: `APF_BASE_PROCESS_PROGRAM_LEVEL_METADATA_IMPROVEMENT_PROMPT.md`.

## FUTURE-PROGRAM-CONTRACT-01 — Program-level metadata, interaction semantics and approval gates

Priority: high. Decision status: implement-later.

Scope:

```text
PROGRAM.DEF / top-level metadata
INTERACTION.MODEL
PROCESS_RAIL.DEF / process_rail
CONVERSATION.SEMANTICS
HYBRID_EXECUTION.MODEL
Deterministic validation requirements
Human review and approval points
PROGRAM_LEVEL_CONTRACT_REVIEW / PROGRAM_LEVEL_CONTRACT_APPROVAL_GATE
```

This item is intentionally preserved for a future APF base-process patch and was not implemented as part of RC4-Post-SVG.
