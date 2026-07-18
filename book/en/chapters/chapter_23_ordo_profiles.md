# Chapter 23. Ordo Profiles

## Why Profiles Are Needed

In the previous chapter, we examined `Ordo Core` — the minimum set of constructs without which an Ordo program cannot be controlled. Core defines the basic execution shape: entry, node, state, gate, output, and trace.

But in real work, this is not enough.

One Ordo program may create an analytical package. Another may guide a user through guided intake. A third may produce QA documentation. A fourth may validate a rendered artifact. A fifth may work with approvals, evidence, templates, and a document catalog.

All of these scenarios use Core, but they need different additional rules.

This is why Ordo needs `Profiles`.

Simply put:

```text
An Ordo Profile is a standard set of additional rules and constructs for a particular type of work.
```

![Nebu — idea: Profile as an operating mode](../assets/mascots/64x64/Nebu_idea_64x64.png)

Core says: “every Ordo program must have controlled execution.”

A Profile says: “this is how execution should be controlled for a particular class of tasks.”

## Why Not Put Everything in Core

It may seem that every useful rule should be added directly to Core. For example:

```text
- document rules;
- QA rules;
- approval rules;
- rendered artifact validation rules;
- evidence matrix rules;
- documentation splitting rules;
- package generation rules.
```

But Core would quickly become too large.

Core should remain minimal and stable. It should not know every possible task type. Otherwise, Ordo will lose flexibility.

Ordo therefore separates:

```text
Core     → base execution language
Profile  → standard operating mode
Domain   → specific subject domain
Library  → reusable ready-made parts
```

![Nebu — thinking: separation of Core, Profile, Domain, and Library](../assets/mascots/64x64/Nebu_thinking_64x64.png)

This resembles ordinary programming. A language has base syntax, while separate frameworks and libraries are used for web, testing, databases, or UI.

In Ordo, a Profile serves as such a standard operating mode for a particular class of tasks.

## What a Profile May Contain

A Profile should not contain everything. It should contain only rules that recur across many Ordo programs of the same type.

For example, a Documentation Profile may contain:

```text
- template handling rules;
- rules for splitting large documents;
- rules for selecting required documents;
- rendered artifact validation rules;
- catalog / selected docs rules;
- self-check rules before handoff.
```

A QA Profile may contain:

```text
- test case structure;
- fixture rules;
- expected behavior;
- negative scenarios;
- regression suite;
- coverage report;
- manual QA runbook rules.
```

An Approval Profile may contain:

```text
- what requires human confirmation;
- which gates are blocking;
- which decisions the model may not make itself;
- how approval is recorded in state;
- how final output is prohibited without approval.
```

A Profile is therefore not a subject domain. It is an execution style and mode.

## Example: Documentation Profile

Imagine an Ordo program that creates a document package.

Without a Profile, the instruction may look like this:

```text
Create a README, passport, task, QA document, and validation report.
Before the archive, check that everything is consistent.
```

A human can understand this, but the description lacks structure for controlled execution.

A Documentation Profile may formalize it like this:

```yaml
profile:
  id: "ordo.profile.documentation"
  version: "0.1"

rules:
  - id: "DOC.CATALOG"
    description: "all package documents must be registered in the catalog"

  - id: "DOC.SELECT"
    description: "before responding, the model must determine which documents are required for the current step"

  - id: "TEMPLATE.BIND"
    description: "each output document must be bound to a template or explicitly described structure"

  - id: "RENDER.VALIDATE"
    description: "validate not only the template but the final rendered artifact"
```

Now every Ordo program that uses this Profile receives standard documentation-execution rules.

## Profile as a Behavior Contract

![Nebu — attention: a Profile changes the execution contract](../assets/mascots/64x64/Nebu_attention_64x64.png)

A Profile does not merely add useful advice. It changes the execution contract.

If an Ordo program uses the Documentation Profile, the model can no longer behave as though it were simply writing text.

It must:

```text
- know which documents exist;
- select relevant documents for the current step;
- not confuse a template with a rendered artifact;
- not create a final package without a self-check;
- record which documents were used;
- report a missing required artifact;
- execute validation gates.
```

This is an important distinction.

In an ordinary prompt, you can write: “check consistency.”

In a Profile, you can say: “consistency is a mandatory gate before handoff.”

## Profile in Ordo Source

In human-readable Ordo Source, Profile inclusion may look like this:

```yaml
ordo:
  version: "0.11"

profiles:
  use:
    - id: "ordo.profile.documentation"
      version: "0.1"
    - id: "ordo.profile.qa"
      version: "0.1"
    - id: "ordo.profile.approval"
      version: "0.1"
```

Such a program immediately communicates:

```text
this is not merely text generation;
this is a documentation process;
it has a QA structure;
some decisions require human approval.
```

## Profile in Compiled IR

In compiled IR, this may become a set of operations:

```json
[
  {
    "op": "PROFILE.USE",
    "id": "P1",
    "profile": "ordo.profile.documentation",
    "version": "0.1"
  },
  {
    "op": "PROFILE.USE",
    "id": "P2",
    "profile": "ordo.profile.qa",
    "version": "0.1"
  },
  {
    "op": "PROFILE.BIND_RULES",
    "id": "P3",
    "profiles": ["P1", "P2"]
  }
]
```

After this, the compiler or runtime must know that additional rules are active in the program.

For example, if the Documentation Profile is active, final package generation cannot occur without `RENDER.VALIDATE` or an equivalent gate.

## Typical Profile Constructs

In the current Ordo concept, the following Profile-level constructs can be identified:

```text
TEMPLATE.BIND
EVIDENCE.MATRIX
APPROVAL.REQUIRE
DOC.SPLIT
DOC.CATALOG
DOC.SELECT
RENDER.VALIDATE
QA.CASE.DEF
QA.RUNBOOK.DEF
PACKAGE.SELF_CHECK
HANDOFF.NOTE
```

This is not necessarily a complete list. But it shows the difference between Core and Profile.

Core says:

```text
there must be a gate
```

A Profile says:

```text
before the archive, there must be a rendered artifact validation gate
```

Core says:

```text
there must be an output
```

A Profile says:

```text
the output must comply with template binding and be included in the document catalog
```

Core says:

```text
there must be state
```

A Profile says:

```text
state must contain approval status, selected docs, and validation result
```

## Profile and Domain Pack

Profiles are often confused with Domain Packs. The distinction must be very clear.

A Profile answers:

```text
what type of process is this?
```

A Domain Pack answers:

```text
what subject domain is this process about?
```

For example, a History Event Playbook may use:

```text
Documentation Profile
QA Profile
Approval Profile
Debug/Test Profile
History Event Domain Pack
```

Profiles provide general rules for documents, QA, and approval.

The Domain Pack provides historical-event specifics:

```text
- Path A1/A2/A3/A4/A5;
- HistoryEvent;
- ChangeRecord;
- source row;
- no-op rules;
- event alias;
- history event package structure.
```

These are different layers.

If they are mixed, the Ordo program becomes difficult to maintain.

## Profile and Libraries

Later in the book, we will discuss Ordo Libraries separately. But it is already useful to establish the distinction.

A Profile is a standard behavior mode.

A Library is a reusable package of ready-made parts.

For example:

```text
ordo.profile.qa
```

may define that a QA process must have fixtures, expected behavior, and a regression suite.

A library:

```text
ordo.library.qa.history_event_basic_tests
```

may contain ready-made test cases for a specific type of History Event.

A Profile therefore defines the rules of the game, while a Library may provide reusable elements for that game.

## Why Profiles Matter to the Compiler

The Ordo compiler must understand active Profiles.

Without this, it cannot validate a program correctly.

For example, if the QA Profile is active, the compiler may require:

```text
- presence of TEST.DEF;
- presence of at least a minimum coverage report;
- a negative test for blocking gates;
- expected behavior for key paths.
```

If the Documentation Profile is active, the compiler may check:

```text
- whether all required documents are described;
- whether a document catalog exists;
- whether a validation report exists;
- whether an archive is created before self-check;
- whether rendered artifact validation has been replaced by template validation.
```

A Profile is therefore also a mechanism for compiler validation.

## Typical Mistakes

### Mistake 1. Making a Profile Too Domain-Specific

Bad:

```text
Profile for changing a company's authorized capital
```

This is already a domain pack or library, not a Profile.

A Profile should be broader:

```text
Documentation Profile
QA Profile
Approval Profile
Guided Intake Profile
```

### Mistake 2. Putting Every Rule in Core

If everything becomes Core, Core becomes unmanageable.

Core should remain small. Profiles should extend it for standard operating modes.

### Mistake 3. Not Declaring the Active Profile

If an Ordo program effectively works as a QA process but does not use the QA Profile, the compiler cannot require the necessary tests.

Bad:

```text
somewhere in the text it says that QA should be checked
```

Good:

```yaml
profiles:
  use:
    - id: "ordo.profile.qa"
      version: "0.1"
```

### Mistake 4. Mixing a Profile and a Library

A Profile should not become a warehouse of ready-made examples for every case.

Reusable ready-made parts belong in libraries.

A Profile should define rules, obligations, and gates.

## Mini-Exercise

Take any complex process you want to execute through an AI model.

For example:

```text
- creating an analytical package;
- reviewing a document;
- preparing QA instructions;
- guided intake for a new task;
- reviewing code changes;
- preparing a developer handoff.
```

Try to answer:

```text
1. Which Core is needed here?
2. What type of process is this?
3. Which Profile fits best?
4. Is a Documentation Profile needed?
5. Is a QA Profile needed?
6. Is an Approval Profile needed?
7. Which gates should the Profile add?
8. Which checks should the compiler perform?
9. What is domain-specific and should not enter the Profile?
```

If you can answer these questions, you are already beginning to think in Ordo layers rather than prompts.

## Short Summary

`Ordo Profile` is a standard set of additional rules for a particular type of Ordo process.

Core defines the base execution language.

A Profile defines the operating mode.

A Domain Pack defines the subject domain.

A Library provides reusable ready-made parts.

Correct separation of these layers allows Ordo to remain simple, extensible, and suitable for large playbooks.

Without Profiles, every complex playbook will reinvent documentation, QA, approval, and validation rules.

With Profiles, these rules become reusable and understandable to the compiler.

<!-- REVIEWED: chapter 23; Nebu markers checked -->
