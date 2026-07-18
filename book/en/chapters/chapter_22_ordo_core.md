# Chapter 22. Ordo Core

## Why Ordo Core Is Needed

By this point, we have already examined many individual parts of Ordo: intent, contract, state, nodes, gates, output, status semantics, debug, tests, the feedback loop, and FREEFORM. But if these concepts remain merely a collection of ideas, every Ordo-program author will assemble them differently.

One author will call the starting node `start`.
Another will call it `entry`.
A third will use `initial_question`.
A fourth will hide the beginning of the process inside a long text block.

The same may happen with gates, statuses, output, state, checks, trace, and FREEFORM. Formally, everyone will be “writing Ordo,” but in practice every program will live by its own rules.

This is why `Ordo Core` is needed.

`Ordo Core` is the minimum mandatory set of concepts, rules, and constructs without which an Ordo program is not considered a complete Ordo program.

Core does not describe the entire domain. It does not know what a historical event, monitoring event, legal opinion, company check, or QA package is. Core is responsible for something else: the basic shape of controlled execution.

Simply put:

```text
Ordo Core is the skeleton of the language.
```

![Nebu — idea: Core as the skeleton of the language](../assets/mascots/64x64/Nebu_idea_64x64.png)

Profiles, domain packs, libraries, and concrete playbooks are then layered onto this skeleton.

## What Is Included in Ordo Core

Ordo Core should answer several basic questions:

```text
Where does execution begin?
Which contract must be confirmed?
What state is maintained during the process?
Which process nodes exist?
Which answers may be accepted?
Which gates block or allow a transition?
Which output must be created?
Which negative assertions prohibit incorrect actions?
How is the execution trace recorded?
How are FREEFORM and its coverage represented?
```

Core is therefore not a library of ready-made solutions and not a domain pack. It is the basic grammar of execution.

In the first version, Ordo Core can be understood through these key blocks:

```text
ENTRY.DEF
NODE.DEF
STATE.SCHEMA
ANSWER.REGISTRY
OUTPUT.DEF
ASSERT.NOT
STATUS.SEMANTICS
ASSUMPTION.LEDGER
FREEFORM.COVERAGE
TRACE.REQUIRE
GATE.REQUIRE
```

We will now examine them in simple terms.

## ENTRY.DEF

`ENTRY.DEF` describes how an Ordo program begins.

In an ordinary prompt, the beginning is often informal. The user writes something, the model interprets it somehow, and starts answering.

In Ordo, the start must be defined.

For example:

```yaml
entry:
  id: "ENTRY_MAIN"
  accepts:
    - "new_user_request"
    - "uploaded_playbook"
    - "existing_state"
  first_node: "NODE_CLASSIFY_REQUEST"
```

This means that when a new request arrives, the program must not immediately create the final result. It must move to the first defined node and classify the request.

ENTRY exists so the model does not invent “where to begin.”

## NODE.DEF

`NODE.DEF` describes one step or node in the process.

A node is not merely a paragraph of instructions. It is a place where the model must perform a particular action: ask a question, accept an answer, update state, select a path, check a gate, or move forward.

Example:

```yaml
node:
  id: "NODE_COLLECT_ALIAS"
  purpose: "collect event alias"
  asks:
    question: "What is the event alias?"
  writes_to_state:
    - "event.alias"
  next:
    when_answered: "NODE_COLLECT_SOURCE_FIELD"
```

This is no longer merely advice to “ask for the alias.” It is a formal part of the execution flow.

Core does not define which exact nodes every domain needs. But Core defines that a node should have an id, purpose, expected action, state impact, and transition rule.

## STATE.SCHEMA

`STATE.SCHEMA` describes which data the process remembers during execution.

Without state, the model can easily lose context. It may ask the same question twice, forget a confirmation, confuse a draft with a final result, or treat an assumption as fact.

Example:

```yaml
state_schema:
  event:
    alias:
      type: "string"
      required: true
      status: "unconfirmed"
    source_field:
      type: "string"
      required: true
      status: "unconfirmed"
  approvals:
    pre_archive:
      type: "boolean"
      default: false
```

A state schema does not guarantee that the model will never make a mistake. But it provides a clear map of what must be remembered and what status each item has.

## ANSWER.REGISTRY

`ANSWER.REGISTRY` describes which types of user answers an Ordo program can accept.

This is important for guided intake. A user does not always answer in a perfectly structured form. They may write:

```text
yes
confirmed
no
I changed my mind
go back
continue
that's not it
```

Without a registry, the model decides what each answer means every time. That is dangerous.

Example:

```yaml
answer_registry:
  confirm:
    examples:
      - "yes"
      - "confirmed"
      - "ok"
    effect: "mark_current_contract_part_confirmed"

  reject:
    examples:
      - "no"
      - "doesn't work"
      - "that's not it"
    effect: "keep_state_unconfirmed"

  go_next:
    examples:
      - "next"
      - "continue"
    effect: "advance_if_current_gate_passed"
```

Core should not know every phrase in every language. But Core should require important answers to be classified and to have a defined effect.

## OUTPUT.DEF

`OUTPUT.DEF` describes exactly what an Ordo program must create.

Output is not merely “give an answer.” It is a defined result structure.

For example:

```yaml
output:
  id: "FINAL_PACKAGE"
  type: "archive"
  required_files:
    - "README.md"
    - "SUMMARY.json"
    - "VALIDATION_REPORT.json"
    - "CONSISTENCY_CHECK_REPORT.json"
  gates_before_creation:
    - "G_CONTRACT_CONFIRMED"
    - "G_PRE_ARCHIVE_APPROVED"
    - "G_SELF_CHECK_PASSED"
```

Output definition prevents the model from mixing a draft, explanation, final document, and handoff into one chaotic text.

## ASSERT.NOT

`ASSERT.NOT` represents negative checks. They describe what an Ordo program is not allowed to do.

For example:

```yaml
assert_not:
  - id: "NO_FINAL_ARCHIVE_BEFORE_APPROVAL"
    condition: "pre_archive_approval != true"
    forbidden_action: "create_final_archive"
```

This is especially important in Core. Positive rules say what should be done. But for an AI model, it is often even more important to state explicitly what must not be done.

This especially includes:

```text
- do not create final output before approval;
- do not invent missing data;
- do not mark unconfirmed as confirmed;
- do not hide a gate in FREEFORM;
- do not treat an example as a rule;
- do not change domain logic without explicit instruction.
```

## STATUS.SEMANTICS

`STATUS.SEMANTICS` describes the meaning of statuses.

In complex processes, words such as “ready,” “confirmed,” “draft,” “blocked,” and “passed” can easily become mixed together.

Core should require statuses to have clear semantics.

For example:

```yaml
status_semantics:
  draft:
    meaning: "created but not approved"
    allows_final_handoff: false

  confirmed:
    meaning: "explicitly approved by user"
    allows_gate_pass: true

  blocked:
    meaning: "execution cannot continue until condition is resolved"
    allows_next_step: false
```

This is especially important in Ordo because the language works not only with text but with process.

## ASSUMPTION.LEDGER

`ASSUMPTION.LEDGER` is a record of assumptions.

A model often has to make assumptions. The problem is not the assumptions themselves but the fact that they can become invisible.

Core should require important assumptions to be recorded.

For example:

```yaml
assumption_ledger:
  - id: "A-001"
    assumption: "source field belongs to EDR factual data"
    reason: "user provided EDR-like payload"
    status: "needs_confirmation"
    used_for:
      - "path_selection"
```

If an assumption affects a path, gate, or output, it cannot remain hidden.

## FREEFORM.COVERAGE

Core does not prohibit FREEFORM. On the contrary, it recognizes that part of an instruction may remain in natural language.

But Core should require FREEFORM to be controlled.

This is why `FREEFORM.COVERAGE` is needed:

```yaml
freeform_coverage:
  entries_total: 5
  structured_bindings: 4
  unbound_entries:
    - "FF_DOMAIN_EXAMPLES"
  risk: "medium"
```

This makes it possible to see which parts of the playbook are not yet formalized and where errors may arise.

## TRACE.REQUIRE

After the introduction of the Debug, Test & Improvement Layer, Core should include a minimum trace requirement.

Even when a run is not launched in full debug mode, a complex Ordo program should leave basic execution traces:

```text
- which entry was used;
- which path was selected;
- which gates passed;
- which gates were blocked;
- which state fields changed;
- which output was created;
- which warnings were recorded.
```

This does not always need to be a large detailed log. But execution should not be completely opaque.

## GATE.REQUIRE

Core should also require important transitions to be protected by gates.

For example, final output should not be created merely because the user wrote “go ahead.” The conditions must be checked.

```yaml
gate_require:
  before:
    - action: "create_final_output"
      required_gates:
        - "G_CONTRACT_CONFIRMED"
        - "G_VALIDATION_PASSED"
```

This is one of Ordo's main principles: a gate is not a recommendation but a control point.

## How Core Differs from a Profile

Core is responsible for the base language.

A Profile is responsible for the process type.

For example:

```text
Core says: output must be defined.
Profile says: for documentation, output must have a template, rendered validation, and catalog.

Core says: gates must be explicit.
Profile says: a QA package needs manual QA readiness and automation readiness gates.

Core says: state must be described.
Profile says: for guided intake, state must contain current node, confirmed answers, and pending questions.
```

A profile therefore extends Core but does not replace it.

## How Core Differs from a Domain Pack

A Domain Pack knows the subject domain.

Core does not know what `HistoryEvent`, `ChangeRecord`, `ExternalHistoryEvent`, `Monitoring Center`, `EDR`, `source row`, or `QA package` means.

A Domain Pack describes:

```text
- domain vocabulary;
- domain-specific paths;
- domain gates;
- domain statuses;
- domain outputs;
- domain examples;
- domain no-op rules.
```

Core ensures that all of this is executable, controlled, and verifiable.

## How Core Differs from a Library

A Library is a reusable ready-made solution.

For example, a library may contain a ready-made set of contract-first gates or rendered artifact validation.

Core defines how such things are connected, checked, and prevented from conflicting with the program.

In short:

```text
Core — base language.
Profile — process style/type.
Domain Pack — subject domain.
Library — reusable fragment.
```

![Nebu — thinking: do not mix Core, Profile, Domain Pack, and Library](../assets/mascots/64x64/Nebu_thinking_64x64.png)

## Typical Mistakes

### Mistake 1. Making Core Too Large

Core should not contain everything. If historical events, QA packages, legal opinions, API configurations, and document templates are all placed in Core, it becomes unwieldy.

Core should remain minimal.

![Nebu — attention: Core should not become too large](../assets/mascots/64x64/Nebu_attention_64x64.png)

### Mistake 2. Hiding Core Rules in FREEFORM

If a rule blocks execution, it should not live only in explanatory text.

Bad:

```text
It is advisable to perform a self-check before the archive.
```

Good:

```yaml
gate:
  id: "G_SELF_CHECK_PASSED"
  method: mechanical
  trust_class: deterministic
  blocking: true
```

### Mistake 3. Treating Core as Documentation

Core is not a description for reading. It is part of the executable process model.

### Mistake 4. Allowing a Domain Pack to Break Core

A Domain Pack may extend Core but should not cancel base rules without an explicit override and trace.

## Mini-Exercise

Take any complex prompt you have used before and try to identify its Core part:

```text
1. Where does the process begin?
2. Which nodes or steps exist?
3. Which state must be maintained?
4. Which gates should be blocking?
5. Which output is expected?
6. Which actions must be explicitly prohibited?
7. Which assumptions may arise?
8. What should be logged for debug?
```

If these questions have no answers, you do not yet have an Ordo program, only an informal instruction.

## Short Summary

`Ordo Core` is the minimum mandatory set of constructs that makes an Ordo program controllable.

Core does not describe the domain and does not replace a domain pack. It defines the basic execution shape:

```text
entry → node → state → gate → output → trace
```

Without Core, Ordo will become a collection of attractive prompt templates.

With Core, it becomes a language for controlling AI-model behavior.

---

<!-- REVIEWED: chapter 22; Nebu markers checked -->
