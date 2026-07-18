# Model Instructions — Office Opening Process

## 1. Purpose

These instructions define how an AI model must execute the office-opening process from start to finish.

The model must:

1. follow the process step by step;
2. collect and retain values for attributes `P01–P50`;
3. avoid inventing missing business-critical values;
4. generate the required documents at the defined process points;
5. optionally verify generated documents with the user;
6. assemble the final office-opening package;
7. include an execution trace and the final attribute set in the package.

This is a test process for evaluating how reliably a general-purpose model can follow a long, stateful, document-generating workflow.

---

## 2. Source files

The model must use the following files as the active process definition:

1. `04_NEW_OFFICE_OPENING_ENRICHED_PROCESS.md`
   - defines the 20 process steps;
   - defines attributes `P01–P50`;
   - defines branching rules;
   - defines which documents must be created;
   - defines final completion conditions.

2. `09_TEMPLATE_OFFICE_OPENING_BUSINESS_AND_LOCATION_BRIEF.md`
   - template for Document 1.

3. `10_TEMPLATE_OFFICE_BUILD_TECHNOLOGY_AND_OPERATIONS_PLAN.md`
   - template for Document 2.

4. `11_TEMPLATE_OFFICE_READINESS_AND_OPENING_DECISION_REPORT.md`
   - template for Document 3.

The process file is the source of truth for execution order and attribute collection.

The templates are the source of truth for document structure.

---

## 3. Required output package

At the end of the process, the model must produce:

```text
OFFICE_OPENING_PACKAGE/
├── 01_OFFICE_OPENING_BUSINESS_AND_LOCATION_BRIEF.md
├── 02_OFFICE_BUILD_TECHNOLOGY_AND_OPERATIONS_PLAN.md
├── 03_OFFICE_READINESS_AND_OPENING_DECISION_REPORT.md
├── 04_EXECUTION_TRACE.md
└── 05_COLLECTED_ATTRIBUTES.md
```

The package is not complete until all five files exist.

---

## 4. Operating rules

### 4.1. Execute sequentially

The model must process steps in the order defined in the process file.

It must not skip ahead to later steps merely because it can infer likely values.

### 4.2. Maintain process state

The model must maintain an internal state containing:

```text
current_step
completed_steps
active_branch
branch_history
collected_attributes
unresolved_attributes
generated_documents
verified_documents
blocking_issues
```

### 4.3. Attribute status

Every attribute must have one of these statuses:

```text
collected
confirmed
derived
not-applicable
unresolved
```

The model must not silently leave an attribute empty.

### 4.4. Do not invent critical values

For business, legal, financial, regulatory, location, security, staffing or readiness attributes, the model must:

1. use a value supplied by the user;
2. derive it only when the derivation is direct and obvious;
3. otherwise ask the user;
4. if the user cannot answer, mark it `unresolved`.

### 4.5. Ask only relevant questions

At each step, ask only for attributes required at that step.

Do not ask for all 50 attributes at once.

Do not ask again for values already collected unless:

- the value changed;
- the branch requires confirmation;
- the user gave inconsistent information;
- the value affects a final decision and has not been confirmed.

### 4.6. Branches return to the main process

When a branch is triggered:

1. record the branch in the execution trace;
2. collect any additional information required by that branch;
3. resolve the branch outcome;
4. return to the main process at the specified step.

The model must not create a separate uncontrolled workflow outside the main process.

---

## 5. Step execution protocol

For every process step, the model must perform the following sequence:

```text
1. Announce the current step briefly.
2. Show the purpose of the step.
3. List the attributes to be collected.
4. Ask the minimum set of questions required.
5. Record answers.
6. Validate completeness and consistency.
7. Resolve any branch triggered by the answers.
8. Mark the step complete.
9. Update the execution trace.
10. Continue to the next step.
```

The model must not mark a step complete while a blocking attribute for that step is unresolved.

---

## 6. Attribute collection by process phase

### Phase A — Business initiation

Steps 1–3 collect:

```text
P01–P10
```

The model must establish:

- company identity;
- industry and scale;
- business purpose;
- target geography;
- target date;
- initial budget.

### Phase B — Workplace and location criteria

Steps 4–6 collect:

```text
P11–P21
```

The model must establish:

- growth assumptions;
- work model;
- office-capacity requirements;
- special spaces;
- location priorities;
- lease and rent limits.

### Phase C — Legal and regulatory model

Step 7 collects:

```text
P22–P28
```

If `P22 legal_entity_required = true`, the model must execute the local-entity branch and record the chosen legal/tax model.

If `P26 visa_support_required = true`, the model must mark the relocation/immigration workstream as required.

If `P27 data_residency_requirement` contains restrictions, the model must mark a compliance section as required in Documents 1 and 2.

### Phase D — Location selection

Steps 8–11 collect or finalize:

```text
P29–P32
```

The model must:

- evaluate candidate locations;
- reject candidates that violate mandatory criteria;
- record the selected and backup locations;
- support fallback to the backup location if lease negotiation fails.

### Phase E — Build, technology and suppliers

Steps 12–15 collect:

```text
P33–P42
```

The model must establish:

- renovation scope;
- renovation budget;
- fit-out deadline;
- technology requirements;
- server-room requirement;
- physical security level;
- access-control model;
- furniture standard;
- contractor;
- critical suppliers.

### Phase F — People and ownership

Steps 16–17 collect:

```text
P43–P47
```

The model must identify:

- local hiring target;
- relocation target;
- HR owner;
- IT owner;
- facilities owner.

### Phase G — Readiness and decision

Steps 18–20 collect:

```text
P48–P50
```

The model must establish:

- readiness-test date;
- pilot participants;
- final opening decision.

Allowed final decisions:

```text
open
conditional open
delay
```

---

## 7. Document generation rules

### 7.1. Document 1 generation point

Generate Document 1 after Step 11, when the following are sufficiently complete:

```text
P01–P32
```

Output file:

```text
01_OFFICE_OPENING_BUSINESS_AND_LOCATION_BRIEF.md
```

Use:

```text
09_TEMPLATE_OFFICE_OPENING_BUSINESS_AND_LOCATION_BRIEF.md
```

The model must replace every applicable placeholder with the collected value.

Conditional sections must be included or excluded according to attribute values.

After generation, the model may present the document to the user for verification.

If the user requests changes:

1. update the affected attributes;
2. record the change in the execution trace;
3. regenerate Document 1;
4. continue only after the document is accepted or explicitly marked `provisional`.

### 7.2. Document 2 generation point

Generate Document 2 after Step 17, when the following are sufficiently complete:

```text
P29
P31–P47
```

Output file:

```text
02_OFFICE_BUILD_TECHNOLOGY_AND_OPERATIONS_PLAN.md
```

Use:

```text
10_TEMPLATE_OFFICE_BUILD_TECHNOLOGY_AND_OPERATIONS_PLAN.md
```

The model must include all triggered conditional sections, including server-room, supplier-dependency and relocation workstreams.

The document may be verified with the user before proceeding to readiness testing.

### 7.3. Document 3 generation point

Generate Document 3 at Step 20, after readiness testing and pilot execution.

Output file:

```text
03_OFFICE_READINESS_AND_OPENING_DECISION_REPORT.md
```

Use:

```text
11_TEMPLATE_OFFICE_READINESS_AND_OPENING_DECISION_REPORT.md
```

The content must reflect:

```text
P48 readiness_test_date
P49 pilot_day_participants
P50 final_opening_decision
```

If `P50 = conditional open`, the model must add opening conditions with owners, deadlines and evidence requirements.

If `P50 = delay`, the model must add a recovery plan and revised target date.

---

## 8. User verification protocol

Document verification with the user is optional unless:

- a critical attribute is uncertain;
- the document contains a derived assumption;
- legal, budget, security or final decision content has not been confirmed;
- the user explicitly requests review;
- the model detects inconsistency between attributes and generated text.

When verification is needed, the model must:

1. show or provide the generated document;
2. identify any provisional or derived values;
3. ask the user to approve or correct only the relevant points;
4. update the attribute state;
5. regenerate the document if required;
6. record the verification outcome.

Allowed document statuses:

```text
draft
provisional
user-verified
final
```

---

## 9. Execution trace

The model must create:

```text
04_EXECUTION_TRACE.md
```

For every step, the trace must include:

```markdown
## Step <number> — <name>

- Status:
- Started:
- Completed:
- Attributes collected:
- Values changed:
- Branch triggered:
- Branch outcome:
- Questions asked:
- User confirmations:
- Documents generated or updated:
- Open issues:
```

The trace must reflect the actual path taken, not merely copy the expected process.

If the process returns to an earlier step, the trace must record that return explicitly.

---

## 10. Collected attributes file

The model must create:

```text
05_COLLECTED_ATTRIBUTES.md
```

Required structure:

```markdown
# Collected Attributes

| ID | Attribute | Value | Status | Collected at step | Last updated at step | Used in documents |
|---|---|---|---|---|---|---|
```

All attributes `P01–P50` must be present.

The `Used in documents` column must identify one or more of:

```text
Document 1
Document 2
Document 3
```

No attribute may be omitted.

---

## 11. Consistency checks

Before generating or finalizing any document, the model must verify:

- all placeholders required by the active template have a value or allowed fallback;
- attribute values used in multiple documents are identical;
- selected and backup locations are not accidentally reversed;
- budget values do not conflict;
- dates follow a coherent order;
- owners are consistently named;
- conditional sections match the triggering attributes;
- final decision matches readiness and pilot findings.

If inconsistency is found, the model must stop document finalization and resolve it.

---

## 12. Final package assembly

At Step 20, the model must:

1. confirm all process steps are complete or explicitly resolved;
2. confirm all 50 attributes have a valid status;
3. generate or regenerate all three documents from the latest attribute state;
4. create the execution trace;
5. create the collected-attributes file;
6. assemble all five files into `OFFICE_OPENING_PACKAGE`;
7. verify that no required file is missing;
8. verify that no stale document version is included;
9. provide the package to the user.

---

## 13. Completion gate

The process is complete only if:

```text
- Steps 1–20 were executed.
- All triggered branches were resolved.
- P01–P50 are present.
- Every attribute has an explicit status.
- Documents 1–3 were generated from the latest values.
- Conditional sections match attribute values.
- Execution trace reflects the actual path.
- Collected attributes file is complete.
- Final decision is recorded.
- The final package contains exactly the required files.
```

If any condition fails, the model must report the process as:

```text
blocked
```

or:

```text
completed-with-open-issues
```

It must not report a clean completion when required values or files are missing.

---

## 14. Benchmark-relevant observations

During execution, the model should preserve evidence for later quality assessment:

- number of questions asked;
- number of repeated questions;
- attributes collected at the correct step;
- attributes collected too early or too late;
- branch-selection accuracy;
- number of user corrections;
- document regeneration count;
- placeholder-completion rate;
- cross-document inconsistency count;
- number of unresolved values at finalization;
- whether the final package is complete.

These observations may be included at the end of `04_EXECUTION_TRACE.md`.
