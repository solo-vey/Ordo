# Chapter 24. Domain Packs

## Why Domain Packs Are Needed

In the previous chapters, we divided Ordo into several layers.

`Ordo Core` defines the minimum execution language.

`Ordo Profiles` add rules for standard operating modes: documentation, QA, approval, guided intake, debug, and testing.

But this is still not enough for real processes.

Almost every serious process has its own subject-matter logic.

For example, creating a historical event has its own concepts:

```text
HistoryEvent
ChangeRecord
source row
alias
display name
old value
new value
Path A1
Path A2
Path A4
no-op
rollback
manual QA package
automation spec
```

A monitoring event has different concepts:

```text
monitoring event
configuration
translation tree
sandbox evaluate
REST runbook
business passport
technical package
trigger condition
expected notification
```

Legal analysis has yet another vocabulary:

```text
jurisdiction
legal basis
risk factor
evidence
finding
recommendation
exception
```

These concepts should not be placed in Core.

They are not exactly Profiles either. A Profile says: “this process has QA,” “this process requires approval,” or “this process uses documentation runtime.”

A Domain Pack says: “this subject area has these objects, rules, paths, gates, and edge cases.”

Ordo therefore needs a separate layer:

```text
Domain Pack
```

![Nebu — idea: Domain Pack as Ordo's subject-matter layer](../assets/mascots/64x64/Nebu_idea_64x64.png)

## Simple Explanation

A `Domain Pack` is a package of subject-matter knowledge and rules for a specific domain.

Very simply:

```text
Core is Ordo's grammar.
Profile is the operating style.
Domain Pack is knowledge of a specific domain.
```

Or:

```text
Core knows what NODE and GATE are.
Profile knows that a QA process needs tests and coverage.
Domain Pack knows that History Event work must distinguish A1 from A2,
no-op from real change, and a source row from a generated event.
```

A Domain Pack turns the general Ordo language into a tool for concrete work.

![Nebu — thinking: a Domain Pack does not replace Core or Profile](../assets/mascots/64x64/Nebu_thinking_64x64.png)

## Why a Domain Pack Cannot Be Replaced by a Long Prompt

Of course, a large subject-matter description can be written directly in a prompt.

But familiar problems then appear:

```text
- the model does not know which rules are mandatory;
- examples become mixed with rules;
- edge cases are lost;
- gates do not behave as blocking controls;
- new scenarios are added chaotically;
- there is no test coverage;
- it is unclear which part of the instruction should be changed;
- user feedback is not linked to a specific rule or path.
```

A Domain Pack is intended to solve this.

It structures the domain:

```text
- which objects exist;
- which statuses exist;
- which paths exist;
- which questions must be asked;
- which gates are blocking;
- which outputs are created;
- which edge cases exist;
- which rules remain in controlled FREEFORM;
- which tests verify behavior.
```

## What a Domain Pack Contains

A minimum Domain Pack may contain:

```text
DOMAIN.DEF
DOMAIN.VOCABULARY
DOMAIN.OBJECTS
DOMAIN.PATHS
DOMAIN.RULES
DOMAIN.GATES
DOMAIN.STATUS
DOMAIN.OUTPUTS
DOMAIN.FREEFORM
DOMAIN.TESTS
DOMAIN.COVERAGE
```

### DOMAIN.DEF

This defines the subject domain.

For example:

```yaml
domain:
  id: "history_event"
  name: "History Event Domain Pack"
  version: "0.1"
  purpose: "Guided intake and package generation for history event creation or update."
```

This block answers:

```text
What is this domain?
Why does it exist?
Which task does it help perform?
```

### DOMAIN.VOCABULARY

This is the term dictionary.

For example:

```yaml
vocabulary:
  HistoryEvent: "final internal historical event shown in company/person history"
  ChangeRecord: "technical record describing detected source-level change"
  source_row: "input source object from which change is detected"
  no_op: "case where no new event should be created"
```

The vocabulary is not decorative. It reduces the risk that the model will confuse similar concepts.

For example, without a defined distinction between `ChangeRecord` and `HistoryEvent`, the model may treat a technical record as a completed historical event.

### DOMAIN.OBJECTS

This describes the main domain objects.

```yaml
objects:
  - id: "HistoryEvent"
    required_fields:
      - "alias"
      - "display_name"
      - "event_date"
      - "old_value"
      - "new_value"

  - id: "ChangeRecord"
    required_fields:
      - "field"
      - "old"
      - "new"
      - "status"
```

In a real Domain Pack, these fields may be more complex. The basic idea is simple: the model must know which entities it works with.

### DOMAIN.PATHS

This describes the main scenarios.

For example:

```yaml
paths:
  - id: "A1"
    name: "direct source row field change"
    when:
      - "change is detected directly in source row"
    requires:
      - "source field confirmed"
      - "old/new values confirmed"

  - id: "A2"
    name: "related entity change"
    when:
      - "change belongs to entity related through identification center"
    requires:
      - "main entity confirmed"
      - "related entity confirmed"
      - "relation context confirmed"
```

Paths prevent the model from guessing a scenario based on a general impression.

The model must select a path and explain why.

### DOMAIN.RULES

These are subject-matter rules.

For example:

```yaml
rules:
  - id: "R_NO_EVENT_FOR_NOOP"
    text: "If old and new normalized values are equal, no HistoryEvent should be created."
    enforcement: "blocking"

  - id: "R_CURRENCY_NORMALIZATION"
    text: "Capital amount comparison must use normalized amount and normalized currency."
    enforcement: "required"
```

A rule should not be merely a paragraph in documentation. It should have an identifier and enforcement semantics.

### DOMAIN.GATES

These are domain-specific control points.

```yaml
gates:
  - id: "G_SOURCE_FIELD_CONFIRMED"
    type: "approval"
    blocking: true
    description: "Source field must be confirmed before generating event passport."

  - id: "G_NOOP_CHECK_DONE"
    type: "validation"
    blocking: true
    description: "No-op check must be completed before event creation decision."
```

A Domain Pack may use general Profile gates while adding its own subject-specific gates.

### DOMAIN.OUTPUTS

This describes the results the process must create.

For example:

```yaml
outputs:
  - id: "history_event_passport"
    format: "markdown"
    required: true

  - id: "jira_task"
    format: "markdown"
    required: true

  - id: "manual_qa_package"
    format: "markdown"
    required: true
```

This matters because different domains have different outputs.

### DOMAIN.FREEFORM

Even in a Domain Pack, some knowledge may remain in controlled FREEFORM.

For example:

```yaml
freeform:
  - id: "FF_DOMAIN_EXAMPLES"
    purpose: "Examples of valid and invalid history event descriptions."
    binding:
      applies_to:
        - "DOMAIN.PATHS"
        - "DOMAIN.RULES"
    must_not_contain:
      - "blocking gates"
      - "status semantics"
```

A Domain Pack therefore does not prohibit free text. It controls it.

### DOMAIN.TESTS

A Domain Pack should contain or include tests.

```yaml
tests:
  - id: "TC_A1_DIRECT_FIELD_CHANGE"
    expects:
      path: "A1"
      required_gates:
        - "G_SOURCE_FIELD_CONFIRMED"

  - id: "TC_NOOP_NORMALIZED_VALUES_EQUAL"
    expects:
      noop: true
      history_event_created: false
```

Without tests, a Domain Pack quickly begins to break as it changes.

## Domain Pack as a Contract Between People and the Model

A Domain Pack is not merely a technical specification.

It is a contract between:

```text
- the author of the domain logic;
- the analyst;
- the model;
- compiler/runtime;
- tests;
- future users.
```

The domain author says:

```text
This is how we work in this subject area.
These are our concepts.
These are our paths.
These are our gates.
This is where the model must stop.
This is what it must not do.
This is how we verify that it has not broken.
```

The model should not invent domain logic from nothing.

It should execute the Domain Pack.

## Example: History Event Domain Pack

The main parts of a History Event Domain Pack may look like this:

```text
DOMAIN.DEF:
  History Event guided intake and package generation

DOMAIN.VOCABULARY:
  HistoryEvent
  ChangeRecord
  source row
  ExternalHistoryEvent
  no-op
  rollback
  manual QA
  automation spec

DOMAIN.PATHS:
  A1 — direct source row field change
  A2 — related entity change through identification center
  A3 — generated/calculated data change
  A4 — external history event input
  A5 — correction / rollback / special case

DOMAIN.GATES:
  G_ALIAS_CONFIRMED
  G_DISPLAY_NAME_CONFIRMED
  G_SOURCE_ROW_CONFIRMED
  G_VALUES_CONFIRMED
  G_NOOP_CHECK_DONE
  G_PRE_ARCHIVE_APPROVAL
  G_SELF_CHECK_DONE

DOMAIN.OUTPUTS:
  README
  SUMMARY
  VALIDATION_REPORT
  CONSISTENCY_CHECK_REPORT
  HISTORY_EVENT_PASSPORT
  JIRA_TASK
  IMPLEMENTATION_PROMPT
  QA_PACKAGE
  PROCESS_IMPROVEMENT_FEEDBACK
  QA_AUTOMATION_SPEC
  QA_AUTOMATION_README
```

This is no longer a “long prompt.” It is a domain rule system.

## Example: Monitoring Event Domain Pack

Another domain has a different package.

```text
DOMAIN.DEF:
  Monitoring Event business and technical package generation

DOMAIN.VOCABULARY:
  monitoring event
  business passport
  registry row
  Monitoring Center config
  translation tree
  sandbox evaluation
  REST runbook
  notification payload

DOMAIN.PATHS:
  business passport creation
  technical config package
  sandbox QA
  REST execution runbook
  registry row after Confluence URL

DOMAIN.GATES:
  G_BUSINESS_CONFIRMATION
  G_CONFIG_VALUES_CONFIRMED
  G_SANDBOX_EVALUATION_READY
  G_REST_RUNBOOK_SELF_CONTAINED
  G_CONFLUENCE_URL_REQUIRED_BEFORE_REGISTRY_ROW
```

This Domain Pack may use the same Core and Profiles, but its domain rules are different.

## Relationship Between a Domain Pack and Core

A Domain Pack must not redefine Core.

![Nebu — attention: a Domain Pack must not rewrite Core](../assets/mascots/64x64/Nebu_attention_64x64.png)

Bad:

```text
The Domain Pack changes the meaning of NODE or GATE.
```

Good:

```text
The Domain Pack uses NODE and GATE for its subject-matter rules.
```

Core should remain stable.

A Domain Pack should extend the language rather than rewrite its foundation.

## Relationship Between a Domain Pack and Profiles

A Domain Pack may require specific Profiles.

For example:

```yaml
domain:
  id: "history_event"

requires_profiles:
  - "ordo.profile.guided_intake"
  - "ordo.profile.documentation"
  - "ordo.profile.qa"
  - "ordo.profile.approval"
  - "ordo.profile.debug_test_improvement"
```

This means:

```text
Core alone is not enough for this domain.
Guided intake, documentation, QA, approval, and debug/test/improvement are mandatory.
```

Profiles provide general mechanisms.

The Domain Pack fills them with subject-matter meaning.

## Relationship Between a Domain Pack and Libraries

A Domain Pack may use libraries.

For example:

```yaml
include:
  - library: "ordo.validation.noop_checks"
    version: "0.1"
    as: "noop"

  - library: "ordo.qa.manual_runbook"
    version: "0.1"
    as: "manual_qa"
```

But a Domain Pack is not simply a library.

The distinction is:

```text
Library — a reusable ready-made solution.
Domain Pack — a subject-matter rule system for a specific domain.
```

A Domain Pack may include many libraries while remaining the owner of domain semantics.

## Domain Pack Versioning

A Domain Pack must have a version.

```yaml
domain:
  id: "history_event"
  version: "0.10"
```

This is necessary because changes to domain rules may change model behavior.

For example, if version `0.10` interpreted Path A4 ExternalHistoryEvent one way and version `0.11` clarified the rules, old tests may behave differently.

It is therefore important to know:

```text
- which Domain Pack version was used;
- which tests passed;
- which compatibility checks were performed;
- which breaking changes were introduced;
- whether the changelog was updated.
```

## Domain Pack and the Compiler

The Ordo compiler must be able to validate a Domain Pack.

Minimum checks include:

```text
- DOMAIN.DEF exists;
- vocabulary has no critical gaps;
- paths have selection conditions;
- blocking gates have enforcement;
- outputs have required/optional status;
- tests cover the main paths;
- FREEFORM blocks have binding;
- the Domain Pack does not redefine Core without explicit permission;
- required Profiles are active;
- libraries have pinned versions.
```

For complex Domain Packs, the compiler should also generate:

```text
- coverage report;
- conflict report;
- unresolved ambiguity report;
- compatibility report;
- improvement backlog.
```

## Domain Pack and Debug

Debug mode should show exactly which parts of a Domain Pack were used.

For example:

```yaml
trace_source: "model_self_report"
knowledge_trace:
  - source: "history_event_domain_pack"
    version: "0.10"
    section: "DOMAIN.PATHS.A1"
    used_for: "path selection"

  - source: "history_event_domain_pack"
    version: "0.10"
    section: "DOMAIN.GATES.G_NOOP_CHECK_DONE"
    used_for: "gate evaluation"
```

Without this, the user sees only the answer.

With it, the user can see which domain rule caused the decision.

## Domain Pack and the Improvement Loop

When a user identifies a problem, the improvement record should bind it to the Domain Pack.

For example:

```yaml
improvement_record:
  classification:
    type: "missing_domain_gate"
    severity: "high"

  affected_unit:
    kind: "domain_pack"
    id: "history_event"
    version: "0.10"
    section: "DOMAIN.GATES"

  proposed_patch:
    - "add blocking gate G_MANUAL_QA_INSTRUCTIONS_ARE_ACTIONABLE"
    - "add regression test TC_MANUAL_QA_NOT_TOO_GENERIC"
```

This is important: the problem is not lost in chat but becomes a change to a specific part of domain logic.

## Typical Mistakes

### Mistake 1. Making a Domain Pack One Continuous Text

If a Domain Pack is simply 100 pages of Markdown, the model will again treat it as a long prompt.

Structure is required:

```text
vocabulary
objects
paths
rules
gates
outputs
tests
freeform
```

### Mistake 2. Putting General Rules in a Domain Pack

If a rule applies to any documentation process, it belongs in a Documentation Profile or library, not in one specific Domain Pack.

For example:

```text
Rendered artifact must be validated, not only template.
```

This is a general rule. It is better placed in a Profile or library.

### Mistake 3. Not Separating Examples from Rules

Examples may live in FREEFORM, but they must not become rules without an explicit `DOMAIN.RULE`.

### Mistake 4. Having No Tests

A Domain Pack without tests is an unstable instruction.

It may work today and break after the smallest change.

### Mistake 5. Not Pinning the Version

If a Domain Pack changes but its version does not, it becomes impossible to understand why old behavior can no longer be reproduced.

## Mini-Exercise

Take any process you know well.

For example:

```text
- creating a historical event;
- preparing a monitoring event;
- reviewing a contract;
- analyzing company risks;
- creating a Jira task;
- preparing QA instructions.
```

Try to describe its Domain Pack:

```text
1. What is the domain name?
2. Which core terms must be defined?
3. What are the main objects?
4. Which paths exist?
5. Which rules are blocking?
6. Which gates are mandatory?
7. Which outputs are created?
8. Which parts may remain in FREEFORM?
9. What is the minimum test set?
10. Which problems and improvements should be collected after real use?
```

It does not need to be perfect on the first attempt.

The important thing is to begin distinguishing domain logic from general instructions.

## Short Summary

A `Domain Pack` is a package of subject-matter logic for a specific domain.

Core defines the base language.

Profiles define operating modes.

Libraries provide reusable ready-made solutions.

Domain Packs describe a concrete subject area: vocabulary, objects, paths, rules, gates, outputs, tests, and controlled FREEFORM.

A Domain Pack exists so that the model executes agreed domain rules instead of inventing domain logic itself.

A good Domain Pack is structured, versioned, tested, and visible to the debug/improvement layer.

In complex Ordo processes, the Domain Pack often becomes the main place where real business logic lives.

<!-- REVIEWED: chapter 24; Nebu markers checked -->
