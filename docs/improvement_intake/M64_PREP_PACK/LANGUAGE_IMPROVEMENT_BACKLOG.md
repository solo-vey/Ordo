# Language Improvement Backlog

Status: `ordered planning backlog`  
Scope: Ordo language package and language-adjacent package standards.  
Not a runtime patch by itself.

## Priority scale

```text
P0 — next language/design line candidate
P1 — should be integrated after evidence from APF implementation
P2 — useful hardening or tooling candidate
P3 — keep visible, defer until repeated need is proven
```

---

## LIP-01 — Program-level contract layer

Priority: `P0`  
Initial home: language schema convention + package authoring standard  
Future home: potential formal language construct after repeated use

Add explicit top-level program/process contract fields:

```text
PROGRAM.DEF / program_id / module_id / version / ordo_version
control_level
execution_mode
compatibility policy
```

This should support human review before final package assembly.

Do not hide these decisions only inside YAML. They need a human-readable review block.

---

## LIP-02 — Interaction model

Priority: `P0`  
Initial home: schema convention + validation/lint candidate

Define explicit roles and responsibilities:

```text
human responsibility
AI responsibility
CLI/helper responsibility
raw tool output policy
```

This prevents the model from silently deciding human-owned content decisions.

---

## LIP-03 — Process rail definition

Priority: `P0`  
Initial home: process model convention

Define process rail policies:

```text
state_tracking
allow_deviation
resume_after_deviation
backtracking policy
state invalidation policy
```

This is especially important for conversational execution where analysts deviate, ask clarifying questions, or go back to earlier decisions.

---

## LIP-04 — Conversation semantics

Priority: `P0`  
Initial home: schema convention + runtime/lint candidate later

Classify analyst inputs:

```text
answer_current_node
clarification
deviation
backtrack_request
new_requirement
unmatched input
```

Each class needs routing behavior, including no-state-change handling for clarifications and resume policy after deviations.

---

## LIP-05 — Hybrid execution model

Priority: `P0`  
Initial home: package standard + runtime profile convention

Define the boundary between:

```text
AI guided process driver
CLI deterministic validator
human reviewer
```

The language/package model should explicitly say which checks require real evidence and cannot be satisfied by an AI statement.

---

## LIP-06 — Program-level approval gate

Priority: `P0`  
Initial home: gate standard / lint candidate

Add:

```text
PROGRAM_LEVEL_CONTRACT_REVIEW
PROGRAM_LEVEL_CONTRACT_APPROVAL_GATE
```

The gate blocks final archive assembly if program metadata, interaction model, process rail, conversation semantics, hybrid execution commands, review points, or startup behavior are incomplete.

---

## LIP-07 — Package profile and startup gates

Priority: `P1`  
Initial home: package standard, already proven in APF rc.4-post-svg

Generalize APF gates:

```text
COMPILE_UTILITY_DISCOVERY_GATE
PACKAGE_PROFILE_GATE
START_PROMPT_PACKAGING_GATE
README_STARTUP_SECTION_GATE
```

These are strong candidates for all full generated playbook/factory packages.

---

## LIP-08 — Derived artifact synchronization

Priority: `P1`  
Initial home: package validation standard

Generalize:

```text
DERIVED_ARTIFACT_SYNC_GATE
checksum-based stale detection
manifest-vs-archive verification
```

Any authoritative model change must either regenerate derived artifacts, confirm them current, or mark them stale/omitted/not-applicable.

---

## LIP-09 — SVG graph artifact standard

Priority: `P1`  
Initial home: companion utility/package artifact standard

Generalize the packaged graph rendering convention:

```text
render from source YAML
render from compiled IR
record source hash/projection hash
record utility version and render profile
include SVG/MMD artifacts only through explicit manifest rules
```

This should remain a package/utility standard before becoming a language construct.

---

## LIP-10 — Delta backlog convention

Priority: `P1`  
Initial home: release discipline/package standard

Preserve improvement prompts and delta files with structured metadata:

```text
source_file
item_id
scope
priority
version_target
decision_status
ordering_position
transfer_status
```

This prevents cross-chat loss of improvement decisions.

---

## LIP-11 — FLOW.JOIN / SHARED.TAIL.REFERENCE

Priority: `P2`  
Initial home: future IR design candidate

Reason:

APF repeatedly needs shared validation/handoff tails. Duplicating tail nodes causes drift.

Do not implement as a quick opcode. It needs a dedicated design milestone because it may affect compiler, IR graph shape, validation, path enumeration, and graph rendering.

---

## LIP-12 — Real-module testcase generation mode

Priority: `P2`  
Initial home: companion utility / testing tool standard

Desired capability:

Given a real Ordo YAML/process module, generate testcase artifacts that exercise:

```text
clean path
bounded noise
clarification without state change
deviation and resume
backtracking
attempt to skip ahead
attempt to answer stale node
terminal readiness checks
```

This should build on M60.7-style testcase-generation work and APF live-module confusion scenarios.

---

## LIP-13 — Two-tier rendering model for output templates

Priority: `P1`  
Initial home: language/rendering documentation + renderer capability standard

Maintain the separation between:

```text
simple deterministic substitutions
complex Jinja-like rendering layer
```

The language package should explain when simple rendering is enough and when advanced template constructs require a stronger renderer/gate.

---

## LIP-14 — Attribute/value schema documentation standard

Priority: `P1`  
Initial home: language book + schema docs

For every field/attribute in YAML/source model, document:

```text
meaning
allowed values if enum
meaning of each enum value
free-form semantics if not enum
compiler/runtime interpretation
validation behavior
```

This is needed because raw YAML attribute names are not self-explanatory for a first-time reader.

---

## LIP-15 — Visual graph annotation/highlight standard

Priority: `P2`  
Initial home: graph utility feature standard

Support highlighting not only nodes/edges on a path, but any visible graph element with comments/annotations:

```text
node
edge
gate
action
artifact
shared tail
rendered output section
```

Useful for explaining current design decisions and review findings directly on graph renders.
