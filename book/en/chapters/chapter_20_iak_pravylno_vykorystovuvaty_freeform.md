# Chapter 20. How to Use FREEFORM Correctly

## Why FREEFORM Is Needed

The previous chapter established an important principle: Ordo should not formalize absolutely everything.

Some content is better preserved as explanation, domain context, examples, rationale, or stylistic guidance.

This is what `FREEFORM` is for.

`FREEFORM` is a controlled textual block inside an Ordo program. It allows natural-language content to remain available to the model without pretending that every sentence is a separate opcode.

For example:

```yaml
FREEFORM:
  id: FF_HISTORY_EVENT_RATIONALE
  purpose: "domain_rationale"
  text: |
    A historical event should describe a real business fact.
    A business-friendly event name is not enough to determine the source type.
    The source row and actual stored field must be confirmed first.
```

This block carries useful domain meaning.

But `FREEFORM` is dangerous if used incorrectly.

If critical process rules are hidden inside it, the Ordo program gradually turns back into an ordinary large prompt.

![Nebu — idea: FREEFORM preserves meaning inside controlled boundaries](../assets/mascots/64x64/Nebu_idea_64x64.png)

## What FREEFORM Is Not

`FREEFORM` is not:

```text
- a place for all rules that were inconvenient to structure;
- a hidden gate;
- a hidden state machine;
- a hidden output contract;
- a hidden approval mechanism;
- a replacement for ASSERT.NOT;
- a replacement for NODE.DEF;
- a replacement for STATUS.SEMANTICS;
- a second playbook inside the playbook.
```

Bad:

```yaml
FREEFORM:
  text: |
    First ask for the alias.
    Then confirm the source field.
    Do not continue until the analyst approves.
    After approval, create four files.
    If validation fails, stop.
```

Almost every sentence here controls execution.

This content should be formalized as nodes, gates, assertions, and outputs.

`FREEFORM` should explain structured behavior, not secretly define it.

## Basic FREEFORM Rule

A practical rule is:

```text
FREEFORM may influence interpretation,
but it must not secretly control execution.
```

This distinction is central.

A model may use FREEFORM to understand:

```text
- why a rule exists;
- what a domain term means;
- what a typical case looks like;
- which examples are risky;
- which tone is appropriate;
- which historical defect caused a rule to appear.
```

But a model should not need to discover from FREEFORM:

```text
- whether it may continue;
- whether approval is required;
- which state transition is allowed;
- which output must be created;
- which action is forbidden;
- which gate blocks handoff.
```

Those things belong in formal structure.

## What a Correct FREEFORM Block Should Contain

A controlled FREEFORM block should have identity and context.

For example:

```yaml
FREEFORM:
  id: FF_SOURCE_ROW_EXPLANATION
  purpose: "domain_explanation"
  binding:
    type: "assertion"
    id: A_NO_SOURCE_TYPE_FROM_EVENT_NAME
  scope:
    phase: "contract_collection"
  text: |
    The event's business name may sound like an EDR event,
    but that does not prove that the changed field is stored
    in the EDR source row. Confirm the actual source first.
```

Useful metadata may include:

```text
id
purpose
binding
scope
owner
risk
review_status
```

Not every block needs every field. But the model and reviewer should be able to answer:

```text
Why does this FREEFORM exist?
Where does it apply?
What formal element is it related to?
How risky is it?
```

## Types of FREEFORM

FREEFORM should not be one undifferentiated text category.

Typical purposes include:

```text
domain_rationale
domain_background
example
counterexample
style_guidance
historical_note
migration_note
human_explanation
edge_case_commentary
```

Example:

```yaml
FREEFORM:
  id: FF_PM_STYLE
  purpose: "style_guidance"
  binding:
    type: "output"
    id: jira_task
  text: |
    Write at PM level. Describe the business problem and expected behavior.
    Do not turn the task into an implementation design.
```

Another example:

```yaml
FREEFORM:
  id: FF_OLD_DEFECT_CONTEXT
  purpose: "historical_note"
  binding:
    type: "gate"
    id: G_PACKAGE_SELF_CHECK
  text: |
    This gate was introduced after several final archives were generated
    before the package-level self-check had completed.
```

The purpose tells the model how the text should be interpreted.

## FREEFORM Must Be Bound to Execution Context

A FREEFORM block should not float through the entire program without scope.

Bad:

```yaml
FREEFORM:
  text: |
    Be careful with source fields.
```

Where is this relevant?

During path selection?

During contract collection?

During generation?

During QA?

A better version:

```yaml
FREEFORM:
  id: FF_SOURCE_FIELD_CAUTION
  purpose: "domain_rationale"
  scope:
    nodes:
      - N_COLLECT_SOURCE_FIELD
      - N_CONFIRM_SOURCE_ROW
  binding:
    type: "gate"
    id: G_SOURCE_ROW_CONFIRMED
  text: |
    The source field must reflect actual storage,
    not an assumption derived from the event name.
```

This makes the block part of a known execution context.

## FREEFORM Must Not Have Its Own Hidden Status

A common mistake is to write:

```yaml
FREEFORM:
  text: |
    If the analyst seems uncertain, consider the contract preliminary.
    When the explanation looks complete, treat the contract as ready.
```

This text creates hidden status semantics.

What does `preliminary` mean?

What does `ready` mean?

Which actions are allowed?

Which gates are required?

The correct solution is to formalize status:

```yaml
STATUS.SEMANTICS:
  contract_draft:
    meaning: "contract contains unresolved assumptions"
    allowed_actions:
      - ask_clarifying_question
      - update_contract
    forbidden_actions:
      - generate_final_package

  contract_confirmed:
    meaning: "mandatory contract fields are explicitly confirmed"
    allowed_next:
      - generation
```

FREEFORM may explain the distinction, but it should not define it secretly.

## FREEFORM Must Not Create New Outputs

Another dangerous pattern is:

```yaml
FREEFORM:
  text: |
    Also prepare a short migration note and a separate checklist
    if the change affects several modules.
```

This introduces outputs that do not exist in `OUTPUT.DEF`.

A model may create them inconsistently.

Instead:

```yaml
OUTPUT.DEF:
  id: migration_note
  when: "multi_module_change == true"

OUTPUT.DEF:
  id: module_checklist
  when: "multi_module_change == true"
```

FREEFORM may explain why these outputs are useful, but the output contract should be formal.

## FREEFORM and Examples

Examples are one of the best uses of FREEFORM.

For example:

```yaml
FREEFORM:
  id: FF_ALIAS_EXAMPLES
  purpose: "example"
  binding:
    type: "node"
    id: N_COLLECT_ALIAS
  text: |
    Good aliases are stable and describe the event meaning:
    LU_CHANGE_STATUS
    LU_CHANGE_NAME

    Avoid aliases based on temporary ticket numbers or implementation details.
```

Examples help the model interpret a formal rule.

But an example must not silently become a mandatory value.

If the only examples are:

```text
LU_CHANGE_STATUS
LU_CHANGE_NAME
```

the model must not assume that all aliases begin with `LU_CHANGE_` unless a formal rule says so.

This is why examples should be explicitly marked as examples.

## FREEFORM and Human Style

Style guidance often belongs in FREEFORM.

For example:

```yaml
FREEFORM:
  id: FF_ANALYST_CONVERSATION_STYLE
  purpose: "style_guidance"
  binding:
    type: "profile"
    id: analyst_guided_intake
  text: |
    Ask one focused question at a time.
    Use domain language the analyst already uses.
    Avoid exposing internal IR names unless they help resolve ambiguity.
    Keep confirmations concise.
```

Some style rules may eventually become formal if they affect process safety.

For example:

```text
ask one question at a time
```

may be only style guidance in one program.

But in another program, asking several questions at once may make state mapping unreliable. Then it should become a formal interaction rule.

The same sentence can therefore belong to different layers depending on its execution impact.

## FREEFORM and Migration of Old Playbooks

Old playbooks often contain large prose sections.

The wrong migration strategy is:

```text
copy the whole section into FREEFORM
```

That preserves the old prompt but does not create an Ordo program.

A better migration process is:

```text
1. Read the prose section.
2. Identify execution-control statements.
3. Extract gates.
4. Extract assertions.
5. Extract statuses.
6. Extract output requirements.
7. Extract node transitions.
8. Leave rationale, examples, and context in FREEFORM.
9. Bind each remaining FREEFORM block to the relevant formal element.
```

For example, an old paragraph may say:

```text
Before creating the archive, review the package carefully.
The archive has caused repeated issues in the past because missing files
were discovered only after handoff. Make sure README, SUMMARY,
and validation reports exist. If anything is missing, stop and fix it.
```

Migration should produce:

```yaml
GATE.DEF:
  id: G_REQUIRED_FILES_PRESENT
  method: "mechanical"
  trust_class: "deterministic"
  before: final_archive
  require:
    - README.md
    - SUMMARY.json
    - VALIDATION_REPORT.json
  on_fail: repair
```

and:

```yaml
FREEFORM:
  id: FF_REQUIRED_FILES_HISTORY
  purpose: "historical_note"
  binding:
    type: "gate"
    id: G_REQUIRED_FILES_PRESENT
  text: |
    This gate exists because missing files were previously discovered
    only after handoff.
```

This is controlled migration.

## Signs of Incorrect FREEFORM

There are several warning signs.

### Sign 1. FREEFORM Contains Words Such as “Mandatory,” “Forbidden,” or “Must Not”

These words do not automatically mean the block is wrong.

But they are a signal that a formal rule may be hidden inside.

Example:

```text
You must not create the archive before approval.
```

This is probably an assertion or gate.

The reviewer should ask:

```text
Where is the formal control?
```

### Sign 2. FREEFORM Defines the Order of Steps

Example:

```text
First ask A, then B, then validate C, and only after that create D.
```

This is process topology.

It probably belongs in nodes and transitions.

### Sign 3. FREEFORM Creates a New Document

Example:

```text
Also create a separate risk report.
```

This belongs in `OUTPUT.DEF`.

### Sign 4. FREEFORM Changes the Meaning of a Status

Example:

```text
For this process, "ready" also means QA has approved the package.
```

This belongs in `STATUS.SEMANTICS`.

### Sign 5. FREEFORM Allows a Gate to Be Bypassed

Example:

```text
If the model is sufficiently confident, it may continue without explicit approval.
```

This is a critical conflict.

If approval is required by a formal gate, FREEFORM must not override it.

![Nebu — attention: FREEFORM must not bypass formal control](../assets/mascots/64x64/Nebu_attention_64x64.png)

## How to Decide: Formalize or Keep as FREEFORM

Use a simple decision sequence.

Ask:

```text
1. Does this fragment change the execution path?
2. Does it allow or block an action?
3. Does it define a status?
4. Does it change state?
5. Does it require approval?
6. Does it create an output?
7. Does it define a validation condition?
8. Does it prohibit behavior?
```

If the answer to any of these is `yes`, the fragment probably needs formalization.

If all answers are `no`, ask:

```text
Does the fragment help the model understand meaning, examples, context, or style?
```

If yes, it is a good FREEFORM candidate.

A compact heuristic is:

```text
controls behavior → formalize
explains behavior → FREEFORM
```

## Example: Incorrect and Correct Versions

Incorrect:

```yaml
FREEFORM:
  text: |
    Ask the analyst for the source field.
    Do not continue until it is confirmed.
    Then create the Jira task.
    The task must contain acceptance criteria and manual tests.
    Never include implementation details.
```

This is a hidden process.

Correct:

```yaml
NODE.DEF:
  id: N_COLLECT_SOURCE_FIELD
  required_input:
    - source_field

GATE.DEF:
  id: G_SOURCE_FIELD_CONFIRMED
  method: "human"
  trust_class: "human_decision"
  require:
    - source_field.status == confirmed
  on_fail: block

OUTPUT.DEF:
  id: jira_task
  must_include:
    - acceptance_criteria
    - manual_tests

ASSERT.NOT:
  id: A_NO_IMPLEMENTATION_DETAILS
  forbidden:
    - implementation_design_in_jira_task

FREEFORM:
  id: FF_JIRA_PM_RATIONALE
  purpose: "style_guidance"
  binding:
    type: "output"
    id: jira_task
  text: |
    The Jira task is intended for PM-level communication.
    It should describe the problem and expected behavior without
    prescribing the developer's implementation approach.
```

Now the process control is formal, while the explanation remains natural.

## FREEFORM Must Be Visible in Reports

A reviewer should be able to see how much of an Ordo program remains in FREEFORM.

A report may show:

```yaml
freeform_report:
  total_blocks: 12

  by_purpose:
    domain_rationale: 4
    example: 3
    style_guidance: 2
    historical_note: 2
    edge_case_commentary: 1

  unbound_blocks: 1
  high_risk_blocks: 2
```

This does not mean FREEFORM is bad.

It means FREEFORM is visible.

Invisible FREEFORM debt is dangerous. Visible FREEFORM can be reviewed and improved.

## High-Risk FREEFORM

Some FREEFORM blocks deserve additional attention.

A block may be high-risk if it:

```text
- contains prohibition language;
- mentions approval;
- describes ordering;
- references final output;
- describes stop conditions;
- mentions state transitions;
- has no binding;
- is very large;
- repeatedly appears in feedback records;
- conflicts with formal structure.
```

Example:

```yaml
FREEFORM:
  id: FF_ARCHIVE_EDGE_CASES
  risk: "high"
  review_status: "needs_formalization_review"
```

A high-risk block does not automatically mean an error.

It means:

```text
review whether hidden execution logic exists here.
```

## FREEFORM as Formalization Debt

Sometimes an author knows that a block should eventually be formalized but does not yet have enough understanding.

Ordo should allow this to be recorded explicitly.

For example:

```yaml
FREEFORM:
  id: FF_COMPLEX_PRIORITY_RULES
  purpose: "edge_case_commentary"
  risk: "high"
  formalization_debt:
    status: "open"
    reason: "priority semantics are not stable yet"
    target:
      - "STATUS.SEMANTICS"
      - "GATE.DEF"
```

This is better than pretending the block is fully controlled.

The language can then report formalization debt.

![Nebu — thinking: visible debt is safer than hidden pseudo-formalization](../assets/mascots/64x64/Nebu_thinking_64x64.png)

## How the Model Should Work with FREEFORM

A model executing an Ordo program should follow this discipline:

```text
1. Read formal structure first.
2. Determine the active node, state, and gates.
3. Load only relevant FREEFORM blocks by scope and binding.
4. Use FREEFORM to interpret or explain the formal context.
5. Never use FREEFORM to override a formal prohibition or blocking gate.
6. If FREEFORM conflicts with formal structure, record a conflict.
7. If FREEFORM repeatedly determines execution, flag it for formalization review.
```

This ordering matters.

The model should not read a large FREEFORM block and then reinterpret the formal program around it.

Formal structure has priority.

## Priority of Formal Structure

The base priority rule is:

```text
formal control > controlled FREEFORM
```

For example:

```yaml
GATE.DEF:
  id: G_APPROVAL_REQUIRED
  require:
    - approval.status == confirmed
  on_fail: block
```

and:

```yaml
FREEFORM:
  text: |
    In obvious cases, approval may sometimes be unnecessary.
```

This is a conflict.

The gate wins.

The model should not silently choose the FREEFORM interpretation.

It should record something like:

```yaml
conflict:
  type: "freeform_vs_formal"
  formal_unit: "G_APPROVAL_REQUIRED"
  freeform_unit: "FF_APPROVAL_NOTE"
  resolution: "formal_control_applied"
  improvement_suggested: true
```

This makes the inconsistency visible.

## Mini-Exercise

Take this prose block:

```text
Before generating the final package, ask the analyst to confirm the event alias and source field. If both look clear, run validation. The final archive must include README, SUMMARY, and a validation report. Do not add implementation details to the Jira task. The wording should remain at PM level because the task is intended to explain the business problem, not prescribe code.
```

Split it into:

```text
NODE.DEF
GATE.DEF
OUTPUT.DEF
ASSERT.NOT
FREEFORM
```

A possible classification is:

```text
ask for alias and source field → NODE.DEF
require confirmation → GATE.DEF
required archive files → OUTPUT.DEF
no implementation details → ASSERT.NOT
PM-level rationale → FREEFORM
```

Then add `binding` and `purpose` to the FREEFORM block.

## Short Summary

`FREEFORM` is a controlled natural-language layer inside an Ordo program.

It exists to preserve:

```text
rationale
examples
domain background
style guidance
historical context
edge-case commentary
human explanation
```

It must not secretly define:

```text
paths
gates
statuses
state transitions
approvals
forbidden actions
outputs
validation conditions
```

The main rule is:

```text
controls behavior → formalize
explains behavior → FREEFORM
```

A good FREEFORM block has identity, purpose, scope, and binding. It is visible in reports, may be marked as high-risk, and may carry explicit formalization debt.

Formal structure always has priority over FREEFORM.

`FREEFORM` is not a dumping ground for unstructured instructions. It is a controlled mechanism for preserving meaning without sacrificing execution control.
