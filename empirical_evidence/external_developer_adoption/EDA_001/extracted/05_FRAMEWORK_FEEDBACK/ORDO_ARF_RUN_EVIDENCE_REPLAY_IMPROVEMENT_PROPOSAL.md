# ORDO / ARF CORE IMPROVEMENT PROPOSAL
## Run Evidence, Replay, Human Authority, and Auditability

Status: proposed backlog input for the Ordo Language / ARF framework  
Source: lessons from building and validating an external External Workflow Preparation playbook  
Scope: framework-level capabilities that should be inherited by all future playbooks

---

## Rationale

During an end-to-end external playbook-development and execution exercise, several capabilities were found to be cross-cutting rather than domain-specific.

These requirements should not be reimplemented independently inside every playbook. They belong in the Ordo Language / ARF framework so that every generated or migrated playbook receives the same runtime evidence, replay, audit, and human-authority guarantees.

---

## Proposed framework backlog

### BL-ORDO-RUN-001 — Persistent Run Identity

The runtime must generate an immutable `run_id` at the beginning of every playbook execution.

The `run_id` must be included in:

- runtime state;
- node evidence;
- answer logs;
- transition logs;
- gate results;
- generated artifacts;
- package revisions;
- validation reports;
- evidence exports;
- replay packages.

A resumed run must preserve the same `run_id`. A restarted run must receive a new one.

---

### BL-ORDO-RUN-002 — Standard Runtime Timestamps

The runtime must record timestamps for all material execution events:

- run start;
- node entry;
- node exit;
- question asked;
- answer received;
- answer accepted or rejected;
- gate evaluation;
- correction;
- backtrack;
- branch switch;
- interruption;
- resume;
- draft approval;
- external evidence submission;
- terminal completion;
- evidence export.

If a timestamp is unavailable, the field must be explicitly marked `not_recorded`; it must not be inferred or fabricated.

---

### BL-ORDO-RUN-003 — Mandatory Run Trace

Every playbook run must produce a standard `RUN_TRACE.json`.

The trace must contain, in chronological order:

- node ID;
- node version;
- entry condition;
- entry timestamp;
- result;
- transition selected;
- gate evaluated;
- gate result;
- state revision;
- evidence IDs;
- backtrack or correction event;
- exit timestamp.

The schema must be domain-independent and reusable by all playbooks.

---

### BL-ORDO-RUN-004 — Standard Exact Answer Log

Every interactive playbook must produce `ANSWER_LOG.json`.

Each record must contain:

- `run_id`;
- node ID;
- question ID;
- exact observable user answer;
- normalized value;
- acceptance status;
- rejection reason;
- retry number;
- provenance/evidence reference;
- timestamp.

Raw answers must remain distinguishable from normalized state and generated conclusions.

---

### BL-ORDO-RUN-005 — State Snapshot History

The runtime must create state snapshots at defined checkpoints:

- initial state;
- after every passed node;
- after every material correction;
- after branch switching;
- before and after backtracking;
- before interruption;
- after resume;
- before terminal transition;
- final state.

Snapshots must be versioned, checksum-addressable, and linked from `RUN_TRACE.json`.

---

### BL-ORDO-RUN-006 — Standard Human Sign-off Record

The framework must define a reusable `SIGNOFF_RECORD.json` contract.

Each sign-off record must contain:

- role;
- person identifier or name, when available;
- exact confirmation text;
- sign-off scope;
- related artifact revision;
- timestamp;
- evidence reference;
- status: proposed, requested, confirmed, rejected, revoked, superseded.

A boolean such as `signoffs_complete: true` must never be sufficient evidence by itself.

---

### BL-ORDO-RUN-007 — Human Authority Enforcement

The runtime and validation layer must prevent the model from:

- approving on behalf of a human;
- inventing a sign-off;
- converting silence into approval;
- treating a workflow continuation as approval;
- collapsing a proposed approver list into confirmed sign-offs;
- claiming human authority from a generic completion flag.

The framework should provide standard gate semantics for explicit human confirmation.

---

### BL-ORDO-RUN-008 — Standard External Evidence Record

The framework must define a domain-independent structure for external references supplied by a user.

Each external evidence record should contain:

- evidence type;
- URL or external identifier;
- supplied-by role/person;
- exact observable answer;
- timestamp;
- related artifact;
- validation mode;
- accessibility status if checked;
- provenance ID.

The framework must distinguish:

- format validation;
- remote accessibility validation;
- human attestation only.

---

### BL-ORDO-RUN-009 — Standard Evidence Export Package

Every completed, blocked, cancelled, or safely stopped run must support export of a standard evidence ZIP.

Minimum contents:

- `RUN_SUMMARY.md`;
- `RUN_TRACE.json`;
- `ANSWER_LOG.json`;
- `GATE_HISTORY.json`;
- `SIGNOFF_RECORD.json`;
- `EXTERNAL_EVIDENCE.json`;
- `ERROR_AND_CORRECTION_LOG.json`;
- state snapshots;
- artifact manifest;
- decision log;
- uncertainty register;
- replay input;
- replay instructions;
- checksums;
- export validation report.

Playbooks may add domain-specific evidence, but must not remove the standard core.

---

### BL-ORDO-RUN-010 — Standard Replay Input

The framework must define `REPLAY_INPUT.json` as a machine-readable ordered representation of the observable run inputs.

It must preserve:

- node/question mapping;
- original answers;
- accepted/rejected status;
- corrections;
- branch selections;
- explicit approvals;
- external evidence submissions;
- interruption/resume events.

Replay input must not contain hidden chain-of-thought.

---

### BL-ORDO-RUN-011 — Replay Validation Modes

The framework must distinguish at least three replay readiness levels:

1. `semantic_replay_available`
   - inputs and node mapping are sufficient to reproduce the same business meaning.

2. `deterministic_replay_available`
   - the same compatible runtime and inputs reproduce the same state and materially equivalent artifacts.

3. `byte_replay_available`
   - the same runtime reproduces byte-identical artifacts where deterministic timestamps and generated IDs are controlled.

A playbook must not claim a stronger replay level than the evidence supports.

---

### BL-ORDO-RUN-012 — Replay Gap Gate

If mandatory data for the requested replay level is missing, the runtime must generate `REPLAY_GAP_REPORT.md`.

The report must identify:

- missing timestamps;
- missing exact answers;
- missing node versions;
- missing snapshots;
- missing sign-off identity;
- missing external evidence provenance;
- nondeterministic fields;
- unavailable runtime dependencies.

The run must not be marked deterministic-replay-ready while blocking gaps remain.

---

### BL-ORDO-RUN-013 — Evidence and Replay Schemas

Add canonical schemas for:

- run trace;
- answer log;
- state snapshot manifest;
- sign-off record;
- external evidence;
- gate history;
- correction log;
- replay input;
- replay gap report;
- evidence export manifest.

These schemas must be versioned independently and referenced from the playbook release compatibility metadata.

---

### BL-ORDO-RUN-014 — Framework-Level Conformance Tests

The sanctioned ARF validation gate must include reusable tests for:

- immutable `run_id`;
- timestamp presence;
- exact-answer preservation;
- human-authority enforcement;
- snapshot continuity;
- trace-transition consistency;
- sign-off evidence completeness;
- replay export completeness;
- replay gap detection;
- checksum verification;
- post-unpack evidence validation.

Domain playbooks should inherit these tests rather than duplicate them.

---

## Expected framework outcome

After implementation, any new Ordo playbook should receive the following capabilities by default:

```text
playbook execution
→ immutable run identity
→ observable answer capture
→ state and transition trace
→ explicit human authority evidence
→ external evidence provenance
→ validated evidence export
→ declared replay readiness
→ replay or explicit gap report
```

Domain playbooks should only define:

- which decisions require sign-off;
- which roles may sign;
- which external evidence types are required;
- which artifacts are compared during replay;
- which domain-specific evidence is added.

---

## Migration impact for existing playbooks

Existing playbooks should be upgraded through a framework migration step:

1. adopt the new runtime evidence schemas;
2. add compatibility metadata;
3. map existing node evidence to standard trace records;
4. replace aggregate sign-off flags with structured records;
5. declare supported replay level;
6. add inherited framework conformance tests;
7. regenerate release and validation reports.

The External Workflow Preparation Playbook should be upgraded only after the new Ordo/ARF release is available, except for domain-specific backlog items that remain local to that playbook.

---

## Classification

Framework / Language package:

- persistent run identity;
- timestamps;
- run trace;
- exact answer log;
- snapshot history;
- sign-off evidence schema;
- human-authority enforcement;
- external evidence provenance;
- evidence export;
- replay package;
- replay readiness levels;
- replay gap gate;
- canonical schemas;
- inherited conformance tests.

Domain playbook:

- role proposal rules;
- domain-specific sign-off matrix;
- business lifecycle requirements;
- domain-specific external link types;
- domain artifact semantic comparison.
