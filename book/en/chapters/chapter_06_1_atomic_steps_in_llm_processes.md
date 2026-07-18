# Chapter 6.1. Atomicity of Steps in Processes with Language Models

> **One step — one responsibility, one result, and one point of validation or confirmation.**

A process executed by a person, a program, or a language model often looks simple only at the level of the step name. For example, the phrase “prepare the document” may hide fact collection, recovery of missing data, decision-making, writing, validation, approval, and a state change. For a person, such a phrase may sometimes be a convenient shorthand. For a language model, it is dangerous: the model may perform some actions, infer others, skip still others, and nevertheless declare the step complete.

Atomicity is not needed to split a process into artificial fragments. It is needed so that every step has a clear responsibility boundary, an observable result, and a local control point. Then an error can be found, fixed, and repeated exactly where it occurred instead of restarting the whole process.

## 1. Statement of the Principle

An **atomic step** is a complete operation with defined inputs, one primary responsibility, one observable result, and one set of completion criteria.

“One step” does not necessarily mean one short command or one sentence. A step may contain several mechanical actions if together they create one result and share one readiness criterion. For example, sorting keys in a structured document, formatting indentation, saving the file, and calculating a checksum may be one technical operation. But the same operation must not silently add missing requirements or approve a new version.

### One Step

One complete operation that can be started, completed, repeated, or rejected as a whole.

### One Responsibility

A step is responsible for one type of change: collect facts, form a decision, create an artifact, validate a result, or apply a state transition. If a step both determines facts and makes a decision, the two tasks begin to influence each other.

### One Result

A step must have one primary observable output. It may be an evidence artifact, a design decision, a completed document, a validation report, or a new state. Several files may count as one result only when they form an indivisible technical set and cannot have different readiness statuses.

### One Validation Point

A step must be checked against criteria that correspond specifically to its result. Factual-data validation differs from document-completeness validation, and document validation differs from user confirmation.

### One Confirmation Point

Confirmation is required where a decision, agreement, or confirmed state changes. It must not be replaced by a model assumption. At the same time, confirmation should not be required after every mechanical action that does not change meaning.

## 2. Why Mixing Responsibilities Is Dangerous

### Data Loss Between Internal Subtasks

When one large step contains several hidden operations, intermediate results often never materialize. The model may discover a contradiction but fail to record it before moving to generation. Later, it becomes impossible to determine whether the contradiction was lost, ignored, or resolved by assumption.

### Hidden Assumptions

If a missing value is needed for the next action, a model tends to insert a plausible value. Without a separate reconstruction step, that value quickly starts to look like a confirmed fact.

### Premature Transition

In a compound step, the first successful subcondition may incorrectly open the next stage. For example, data has been received but has not passed validation; nevertheless, the process moves to generation because `input_received = true`.

### Inability to Localize an Error

If a step simultaneously collects data, makes a decision, and creates a document, the status `failed` does not explain where the problem occurred. A status of `completed` may also hide a weak result from one of the internal operations.

### Formal Validation Instead of Semantic Validation

A large step is easy to check only for the presence of files, sections, or identifiers. This creates a false green: the structure exists, but the content is not executable.

### Inability to Repeat One Operation

If the final review finds a missing rollback, the correct action is to return to creation of the rollback section. In a monolithic step, the whole process must be repeated, including facts that were already confirmed.

### Mixing Facts, Assumptions, and Decisions

Facts must come from evidence. Assumptions must be marked. Decisions must rely on a recorded evidence artifact. If all of this happens in one context without intermediate outputs, the boundaries disappear.

### Excessive Compression of the Result

A language model tends to compress repetitive or similar actions. Several concrete scenarios may turn into the phrase “check the relevant cases,” even though the concrete detail was the main value.

### Self-Validation in the Same Context

The model may evaluate not the actual text but the intention it still holds in context. Therefore, post-render review must work with the materialized artifact rather than with the plan for creating it.

## 3. The Basic Pattern

>     obtain or prepare input data
>     → create one defined result
>     → validate the result separately
>     → show the result or status
>     → obtain confirmation if required
>     → move to the next operation

### Obtain or Prepare Input Data

**Responsibility:** collect confirmed data and explicitly mark gaps.

**Allowed inputs:** sources, previously confirmed artifacts, user answers.

**Expected output:** a structured input artifact.

**Completion criterion:** it is known what is confirmed, what is contradictory, and what is missing.

**Must not do:** make business decisions or silently reconstruct critical values.

### Create One Defined Result

**Responsibility:** materialize one artifact or decision result.

**Allowed inputs:** only recorded and permitted data.

**Expected output:** a concrete document, record, decision, or state proposal.

**Completion criterion:** the result exists in a form suitable for separate validation.

**Must not do:** independently declare the result validated or confirmed.

### Validate the Result Separately

**Responsibility:** check the materialized output against explicit criteria.

**Allowed inputs:** the completed artifact and validation rules.

**Expected output:** evidence with status `passed`, `failed`, or `needs_review`.

**Completion criterion:** every mandatory criterion has evidence.

**Must not do:** silently rewrite the result and then set `passed`.

### Show the Result or Status

**Responsibility:** make process state visible to a person or the next node.

**Expected output:** artifact reference, diagnostic summary, or stage status.

**Must not do:** hide partial success behind a general `completed`.

### Obtain Confirmation

**Responsibility:** record a decision where confirmed state changes.

**Expected output:** `approved`, `rejected`, or `revision_requested`.

**Must not do:** treat silence or plausibility as consent.

### Move to the Next Operation

**Responsibility:** apply an explicit state transition after all preconditions are satisfied.

**Completion criterion:** the previous step's completion criteria are fully satisfied.

**Must not do:** transition on one partial positive signal.

## 4. Atomic Node Pattern

>     step:
>       purpose:
>       inputs:
>       action:
>       output:
>       completion_criteria:
>       validation:
>       confirmation_required:
>       next_step:
>       failure_route:

### `purpose`

One sentence explaining why the step exists. If the purpose contains several independent verbs, that is a signal to decompose the step.

### `inputs`

An exact list of allowed inputs. It is important to distinguish confirmed data, proposed data, and open gaps.

### `action`

The operation that creates the result. The `action` is what changes an artifact or forms a new output.

### `output`

One primary observable result that can be passed to validation.

### `completion_criteria`

Conditions under which the action is genuinely complete. They must not be limited to checking that a file exists.

### `validation`

A separate check of the result. It must not silently fix or regenerate the output. If a fix is needed, validation returns a failure route.

### `confirmation_required`

An explicit rule stating whether human or system confirmation is required. Missing confirmation must not be replaced by an assumption.

### `next_step`

The next step is allowed only after completion criteria, validation, and, where required, confirmation have been satisfied.

### `failure_route`

A route back to the nearest step capable of fixing the specific error. It must not automatically restart the entire process.

## 5. Correct Decomposition Patterns

### Pattern Card: Collect → Resolve → Confirm

**When to use:** when sources contain gaps, contradictions, or incomplete values.

**Problem it removes:** mixing facts with reconstruction and confirmation.

**Minimal structure:**

>     Collect confirmed facts and gaps
>     → Resolve one gap as proposal
>     → Confirm or reject proposal

**Abstract example — a mixed document-preparation step.**

Incorrect:

> Analyze the request, recover missing information, define processing rules, create the instruction, validate it, and mark it ready.

The model reads the request, notices that `delivery_mode` is missing, assumes `scheduled`, forms the rules, creates the document, validates it itself, and moves the process to `approved`.

Problem: it is impossible to determine whether `scheduled` was a fact, a reconstruction, or an assumption.

Correct:

>     Step 1 — Extract confirmed data from the request
>     Result: list of facts and list of gaps
>
>     Step 2 — Process the delivery_mode gap
>     Result: proposed value or explicit open gap
>
>     Step 3 — Show the reconstruction for confirmation
>     Result: confirmed value or return to clarification
>
>     Step 4 — Form processing rules
>     Result: separate design artifact
>
>     Step 5 — Generate the instruction
>     Result: completed document
>
>     Step 6 — Validate the document independently
>     Result: passed or failed validation
>
>     Step 7 — Confirm the document
>     Result: approved state

**Success criterion:** every reconstructed value has a separate status and is not used as confirmed before confirmation.

> If a missing value affects rules, reconstruction must be a separate step. If the value does not affect the result, it may remain an open gap.

### Pattern Card: Design → Materialize → Review

**When to use:** when a structure or contract must be defined before creating the actual artifact.

**Problem it removes:** treating a plan or coverage list as the completed result.

**Minimal structure:**

>     Design artifact
>     → Materialized artifact
>     → Post-render review evidence

**Abstract example — a test plan is incorrectly treated as a completed instruction.**

Incorrect: a positive scenario, empty value, no-change case, and error case are identified, after which `MANUAL_CHECKS.md` is created:

>     1. Prepare positive data.
>     2. Perform the update.
>     3. Check the expected result.
>     4. Roll back if necessary.

The file exists and formally has sections, but the executor must invent the query, values, checks, and rollback.

Correct: first create an execution specification:

>     manual_case:
>       id: CASE-01
>       fixture_lookup:
>         source: sample_records
>         filter:
>           external_key: "EXAMPLE-1042"
>         projection:
>           external_key: 1
>           current_value: 1
>       action:
>         method: PATCH
>         path: /api/example-records/EXAMPLE-1042
>         body:
>           current_value: "new-example-value"
>       expected_result:
>         current_value: "new-example-value"
>         audit_status: "recorded"
>       rollback:
>         method: PATCH
>         path: /api/example-records/EXAMPLE-1042
>         body:
>           current_value: "original-example-value"
>       post_rollback:
>         expected_value: "original-example-value"

Only after a completeness gate may the specification be transformed into a document for a person.

**Success criterion:** the executor can perform the instruction without constructing material commands or expectations.

> If, after reading the document, the executor still has to invent material commands or criteria, the document is not an executable instruction.

### Pattern Card: Generate → Validate → Approve

**When to use:** for any result that must be checked and confirmed.

**Problem it removes:** generate-and-self-approve and automatic transition to confirmed state.

**Minimal structure:**

>     Generate draft
>     → Validate final artifact
>     → Request approval
>     → Apply state transition

**Abstract example — explicit state transition.**

Incorrect:

>     draft → confirmed

immediately after document generation.

Correct:

>     GENERATE_DOCUMENT
>     output: draft_document
>
>     VALIDATE_DOCUMENT
>     output: validation_evidence
>
>     REQUEST_CONFIRMATION
>     output: approved | rejected | revision_requested
>
>     APPLY_STATE_TRANSITION
>     precondition:
>       validation_status == passed
>       approval_status == approved
>     output:
>       state == confirmed

**Success criterion:** confirmed state changes only through a separate operation with explicit preconditions.

### Pattern Card: One Artifact at a Time

**When to use:** when a package contains documents with different purposes and quality criteria.

**Problem it removes:** a general `completed` status that hides a weak file.

**Abstract example — one step generates several documents.**

Incorrect:

> Based on confirmed requirements, create the specification, user instruction, validation checklist, and final manifest.

Three files are meaningful, but the checklist consists of generic phrases. The overall step status is `completed`.

Correct:

>     Artifact A: specification
>     → generate
>     → validate
>     → approve
>
>     Artifact B: user instruction
>     → generate
>     → validate
>     → approve
>
>     Artifact C: validation checklist
>     → generate
>     → validate
>     → approve
>
>     Artifact D: manifest
>     → assemble from approved artifacts
>     → cross-document validation

**Success criterion:** the package is assembled only from artifacts that have an individual ready status.

> If results may have different readiness statuses, they must not be created as one indivisible result.

### Pattern Card: Reconstruction as a Separate Branch

**When to use:** when the process must create something that the normal branch only reads.

**Problem it removes:** hidden reconstruction and mixing operations with different risk levels.

**Abstract example — reconstruction of a record inside ordinary processing.**

Incorrect: the step “Process the record and move to result generation” silently reconstructs a missing record from two sources, sets `valid`, and continues without evidence.

Correct:

>     Check whether the intermediate record exists
>         ├─ record exists → standard processing branch
>         └─ record missing → separate reconstruction branch
>                                ↓
>                         reconstruction evidence
>                                ↓
>                         validation of reconstruction
>                                ↓
>                         confirmation or rejection
>                                ↓
>                         return to standard branch

**Success criterion:** the reconstructed object has evidence, validation, and an explicit status before it returns to the main branch.

> If a process creates what it normally only reads, that is a different operation type and a separate branch.

### Pattern Card: Explicit State Transition

**When to use:** when `draft`, `approved`, `confirmed`, `released`, or another meaningful state changes.

**Problem it removes:** a state transition occurring as a side effect of generation.

**Success criterion:** the transition has preconditions, a separate action, and a separate output state.

### Pattern Card: Independent Post-Render Review

**When to use:** after materializing a document, file, table, PDF, or other final representation.

**Problem it removes:** checking intention instead of the actual result.

**Abstract example — self-validation against the plan.**

Incorrect: the model had the requirement “every section must contain a concrete example,” saw examples in its own plan, and returned `validation_status: passed`, even though one section of the completed document has no example.

Correct:

>     Generation:
>     create final_document.md
>
>     Post-render review:
>     open final_document.md
>     enumerate required sections
>     find a concrete example in every section
>     record missing examples
>     return passed or failed

**Success criterion:** validation evidence refers to the actual artifact, not to the plan or prompt.

> Validate the artifact after materialization. The presence of a requirement in the plan does not prove its presence in the result.

## 6. Antipatterns

### Antipattern Card: Combined Node

**Signs:** one node collects data, makes a decision, generates a result, and moves on.

**Why it appears:** the author wants to shorten the flow or reduce the number of nodes.

**Consequences:** hidden subtasks have different success levels but one overall status.

**How to detect:** purpose or action contains more than one independent verb; there are several outputs; different parts need different gates.

**Replace with:** Collect → Resolve → Confirm, Design → Materialize → Review.

### Antipattern Card: Hidden Reconstruction

**Signs:** missing data is reconstructed and immediately used as confirmed.

**Why it appears:** the model tries to complete the task without leaving an open gap.

**Consequences:** downstream logic depends on an unconfirmed value.

**How to detect:** the trace contains no reconstruction event, but the result contains a value absent from the sources.

**Replace with:** Reconstruction as a Separate Branch.

### Antipattern Card: Design Equals Artifact

**Signs:** a plan, scenario list, or coverage list is incorrectly treated as a completed instruction.

**Why it appears:** the structure looks complete and the file formally exists.

**Consequences:** the executor reconstructs concrete actions, inputs, and expected results.

**How to detect:** the document contains many words such as “appropriate,” “required,” or “expected,” but few concrete values.

**Replace with:** Design → Materialize → Review.

### Antipattern Card: Generate and Self-Approve

**Signs:** the same step creates the result and declares it ready.

**Why it appears:** an attempt to save a separate review step.

**Consequences:** the model evaluates its intention rather than the artifact.

**How to detect:** there is no validation evidence between generation and approved state.

**Replace with:** Generate → Validate → Approve.

### Antipattern Card: Validation by Presence

**Signs:** validation checks only whether a file, section, or ID exists.

**Why it appears:** such checks are easy to automate.

**Consequences:** generic phrases pass the gate even though the result is not executable.

**How to detect:** validation does not check specificity, completeness, or executability.

**Replace with:** artifact-level completeness and post-render review.

### Antipattern Card: Automatic Transition on Partial Success

**Abstract example — partial success starts the next stage.**

Incorrect: a step must receive data, validate it, and determine a mode. The data is received, but an attribute fails validation; the process moves to generation because `input_received = true`.

Correct:

>     input_status: received
>     validation_status: failed
>     decision_status: not_started
>     generation_status: blocked
>     overall_status: blocked_by_input_validation

Transition is allowed only when:

>     input_status == received
>     AND validation_status == passed
>     AND required_gaps == 0

**Replace with:** NO_PARTIAL_SUCCESS_TRANSITION_GATE.

> A transition depends on full completion criteria, not on the first positive signal.

### Antipattern Card: Package-Level Success Hides Artifact Failure

**Signs:** the overall package is `passed` although one artifact failed or was not validated.

**Consequences:** the user receives a set in which a weak component is hidden by the aggregate status.

**Replace with:** One Artifact at a Time and ARTIFACT_LEVEL_STATUS_GATE.

### Antipattern Card: Generic Instruction as Completed Work

**Abstract example — semantic placeholders.**

Incorrect:

>     Find the appropriate record.
>     Apply the required change.
>     Make sure the result is correct.
>     Perform a rollback.

The words `appropriate`, `required`, and `correct` hide unresolved decisions.

Correct:

>     Find the record in the fictional sample_items dataset
>     using the filter { "sample_key": "ITEM-204" }.
>
>     Change the display_label field
>     from "Old sample label"
>     to "New sample label".
>
>     After the update, verify:
>     - display_label == "New sample label";
>     - change_status == "applied".
>
>     To roll back, restore:
>     display_label = "Old sample label".
>
>     After rollback, repeat the lookup
>     and verify the original value.

**Replace with:** explicit input/output contract and executable specification.

> If an adjective or pronoun replaces a concrete object, value, or criterion, it is a semantic placeholder.

### Antipattern Card: Evidence Collection Mixed with Decision

**Abstract example — fact collection is mixed with decision-making.**

Incorrect:

> Collect information about the request and determine whether it can be approved automatically.

While reading, the model immediately classifies ambiguous values as positive in order to complete the decision.

Correct:

>     Step A — Evidence collection
>     Output:
>     - confirmed facts;
>     - source references;
>     - contradictions;
>     - open gaps.
>
>     Step B — Eligibility evaluation
>     Input:
>     - only the recorded evidence artifact.
>     Output:
>     - eligible;
>     - not eligible;
>     - needs review.
>
>     Step C — Approval
>     Input:
>     - evaluation result.
>     Output:
>     - confirmed decision.
>
> If an action determines what counts as a fact, it must not simultaneously decide which outcome is desirable.

## 7. When a Step Must Be Split

Split a step if at least one of the following is true:

- it creates more than one independent result;
- different parts need different quality criteria;
- one part can succeed while another fails;
- one part requires confirmation and another does not;
- an error must be fixed without repeating the whole process;
- facts, assumptions, and decisions are mixed;
- one context creates and validates the same result;
- different activity types are combined: analysis, reconstruction, generation, validation;
- the step can hide uncertainty;
- the result of one internal part becomes the input of another without explicit recording.

A practical test: if the failure route says “repeat the step,” but in reality only one part of the step must be repeated, the step is not atomic.

## 8. When Combining Actions Is Acceptable

The atomicity principle does not require every tiny mechanical action to become a separate node.

Combining actions is acceptable if they:

- have one responsibility;
- create one result;
- share one completion criterion;
- contain no new business decision;
- do not change confirmed state;
- do not hide reconstruction;
- can be safely repeated as one operation;
- are a mechanical transformation of a confirmed source.

### Abstract Example of Acceptable Combination

After a structured document is confirmed, the process must:

- sort keys;
- format indentation;
- save the file;
- calculate a checksum.

These may be performed as one technical step: meaning does not change, no decisions are added, and the output is one release artifact.

### Unacceptable Combination

The same step must not:

- add missing requirements;
- rewrite ambiguous rules;
- remove sections as “unnecessary”;
- automatically confirm the new version.

> Mechanical transformations may be grouped. Semantic decisions, reconstruction, and confirmation may not.

## 9. Validating Process Atomicity

The following are methodological gates. They help a process author inspect structure, but by themselves they do not change the normative language contract.

### `SINGLE_RESPONSIBILITY_GATE`

**Checks:** whether the step has one type of responsibility.

**Passes:** purpose and action describe one operation.

**Blocks:** the step simultaneously collects, reconstructs, decides, and generates.

**Diagnostic:**
`STEP_ATOMICITY_001: step mixes evidence collection and decision making.`

### `SINGLE_OUTPUT_GATE`

**Checks:** whether there is one primary result.

**Passes:** output has one artifact/status contract.

**Blocks:** independent results may have different readiness.

**Diagnostic:**
`STEP_ATOMICITY_002: multiple independently validatable outputs detected.`

### `EXPLICIT_INPUT_OUTPUT_GATE`

**Checks:** whether inputs and output are defined.

**Blocks:** semantic placeholders or unrecorded intermediate data are used.

**Diagnostic:** `STEP_ATOMICITY_003: output depends on implicit input.`

### `NO_HIDDEN_RECONSTRUCTION_GATE`

**Checks:** whether recovery of missing data is modeled as a separate branch.

**Blocks:** a reconstructed value is used as confirmed without evidence.

**Diagnostic:**
`STEP_ATOMICITY_004: reconstructed value has no proposal/confirmation state.`

### `SEPARATE_GENERATION_VALIDATION_GATE`

**Checks:** whether validation works with a completed result separately from generation.

**Blocks:** the same step generates, fixes, and sets `passed`.

**Diagnostic:**
`STEP_ATOMICITY_005: generation and validation share one uncontrolled action.`

### `EXPLICIT_CONFIRMATION_GATE`

**Checks:** whether confirmation of required decisions is recorded explicitly.

**Blocks:** confirmed state is reached without approval evidence.

**Diagnostic:**
`STEP_ATOMICITY_006: confirmed transition has no explicit approval.`

### `NO_PARTIAL_SUCCESS_TRANSITION_GATE`

**Checks:** whether the next step depends on complete completion criteria.

**Blocks:** a transition starts after one successful subcondition.

**Diagnostic:**
`STEP_ATOMICITY_007: transition triggered by partial success.`

### `FAILURE_LOCALIZATION_GATE`

**Checks:** whether the failure route leads to the nearest operation capable of fixing the error.

**Blocks:** a local error restarts the entire process.

**Diagnostic:**
`STEP_ATOMICITY_008: failure route is broader than affected responsibility.`

### `ARTIFACT_LEVEL_STATUS_GATE`

**Checks:** whether every independent artifact has its own status.

**Blocks:** package-level `passed` hides a failed or unvalidated artifact.

**Diagnostic:**
`STEP_ATOMICITY_009: aggregate status masks artifact failure.`

## 10. Statuses and Errors

One general status is insufficient for a process in which different stages may have different states.

>     input_status:
>     decision_status:
>     generation_status:
>     validation_status:
>     approval_status:
>     execution_status:
>     overall_status:

### Abstract Example of Different Statuses

Incorrect:

>     status: passed

while the document has been created, quality review has not been performed, execution is blocked, and confirmation is missing.

Correct:

>     input_status: confirmed
>     design_status: completed
>     generation_status: completed
>     validation_status: not_started
>     approval_status: pending
>     execution_status: blocked
>     overall_status: awaiting_validation

Another variant:

>     generation_status: completed
>     validation_status: failed
>     approval_status: blocked
>     execution_status: not_started
>     overall_status: failed_quality_gate
>
> Status shows exactly where the process is. `File created` does not mean `file is high quality`, and `file is high quality` does not mean `file is confirmed`.

Partial success must remain visible. `overall_status` aggregates but does not replace detailed statuses.

## 11. Relationship to Language-Model Behavior

Language models have several properties that make atomicity especially important.

### Tendency to Compress Repetitive Steps

When many scenarios share a similar structure, a model may combine them into a general phrase. Intermediate artifacts and separate gates preserve concrete detail.

### Turning a Specification into a Description

A model may replace exact values with words such as “appropriate,” “relevant,” or “expected.” An atomic output contract makes it possible to check whether safe specificity is present.

### Inferring Missing Information

A model often tries to finish the task. A separate reconstruction branch makes assumptions visible and prevents them from becoming facts without confirmation.

### Plausible Does Not Mean Confirmed

A logically probable value may still be wrong for the specific process. Evidence collection is therefore separated from decision evaluation.

### Self-Evaluation Against Intention

The model remembers that it intended to add a section and may consider the section present. Independent post-render review forces validation of the actual text or file.

### Silent Transition to the Next Task

After generation, a model may begin the next stage without an explicit state transition. Completion criteria and a next-step gate stop such transitions.

### One Large Prompt Loses Local Constraints

The more responsibilities a prompt contains, the more likely a local condition is to disappear among global instructions. Decomposition reduces the active context of each step.

## 12. Practical Process-Design Template

1. Name the final results.
2. Define a separate responsibility for every result.
3. Separate fact collection from reconstruction.
4. Separate decision-making from materialization.
5. Separate generation from validation.
6. Add completion criteria.
7. Add a local failure route.
8. Add a confirmation point only where a decision or state changes.
9. Forbid transition on partial success.
10. Assemble the aggregate result only from individually ready parts.

### Abstract Example of a Local Failure Route

Incorrect: final validation finds a missing rollback, and the process returns to the beginning, collecting already confirmed data again.

Correct:

>     POST_RENDER_REVIEW
>         ↓ failed: rollback section missing
>     ROLLBACK_SPEC_RESOLUTION
>         ↓
>     DOCUMENT_REGENERATION_FOR_AFFECTED_SECTION
>         ↓
>     POST_RENDER_REVIEW

The following are not repeated:

- fact collection;
- contract confirmation;
- scenario selection;
- independent artifacts that already passed.

> A failure route returns to the nearest step capable of fixing the error, not to the beginning of the process.

## 13. Final Comparison Table

| **Situation** | **What Is Mixed** | **Primary Risk** | **Correct Separation** | **Gate** |
|---|---|---|---|---|
| Preparing a document with a missing field | facts, reconstruction, design, generation, approval | assumption becomes fact | Collect → Resolve → Confirm → Generate → Validate → Approve | `NO_HIDDEN_RECONSTRUCTION_GATE` |
| A test plan is treated as a runbook | design and materialization | non-executable document | Design → execution specification → rendered guide → review | `EXPLICIT_INPUT_OUTPUT_GATE` |
| A missing record is reconstructed during processing | read and create | no evidence | separate reconstruction branch | `NO_HIDDEN_RECONSTRUCTION_GATE` |
| One step creates several documents | independent outputs | weak file hidden by package | One Artifact at a Time | `SINGLE_OUTPUT_GATE` |
| The model validates its own plan | intention and result | false green | Independent Post-Render Review | `SEPARATE_GENERATION_VALIDATION_GATE` |
| Data is received but invalid | partial success and transition | premature generation | full completion criteria | `NO_PARTIAL_SUCCESS_TRANSITION_GATE` |
| Generic phrases replace specifics | design and execution | semantic placeholders | executable specification | `EXPLICIT_INPUT_OUTPUT_GATE` |
| Fact collection immediately determines eligibility | evidence and decision | biased evidence | Evidence → Evaluation → Approval | `SINGLE_RESPONSIBILITY_GATE` |
| Formatting, saving, checksum | mechanical actions for one output | low risk | acceptable combination | `SINGLE_OUTPUT_GATE` |
| A local error restarts everything | failure route and global restart | lost time and drift | nearest corrective step | `FAILURE_LOCALIZATION_GATE` |
| One `passed` for everything | detailed statuses and aggregate status | hidden incompleteness | separate stage statuses | `ARTIFACT_LEVEL_STATUS_GATE` |
| Generation automatically confirms | generation and state transition | confirmed without approval | Generate → Validate → Approve → Transition | `EXPLICIT_CONFIRMATION_GATE` |

## Final Rule

> **Do not combine in one step actions that may have different results, different quality criteria, different failure routes, or different confirmation needs.**

Practical formula:

> **First create one observable result. Then validate it separately. Only after that move forward.**
