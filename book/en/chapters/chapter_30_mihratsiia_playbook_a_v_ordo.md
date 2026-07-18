# Chapter 30. Migrating a Playbook to Ordo

## Why This Is Needed

Once we understand that an old Markdown playbook is a knowledge base, the next question appears: how do we turn it into an Ordo program?

This should not be a mechanical rewriting of text. Migrating a playbook to Ordo is a process in which we gradually extract executable structure from the document:

```text
intent → contract → context → state → paths → nodes → gates → outputs → tests → coverage
```

The goal of migration is not to make the document “prettier.” The goal is to make the process controllable, traceable, testable, and suitable for repeatable execution.

![Nebu — idea: migration turns knowledge into executable structure](../assets/mascots/64x64/Nebu_idea_64x64.png)

---

## Simple Explanation

Migrating a playbook to Ordo is similar to turning a large human instruction into a program for controlled execution by a model.

Before:

```text
Read the instruction, understand the context, ask questions, remember to check the package, and if everything is ready, create the archive.
```

After:

```yaml
intent:
  id: "create_history_event_package"

contract:
  requires:
    - "alias_confirmed"
    - "source_field_confirmed"
    - "expected_values_confirmed"

nodes:
  - id: "N_SELECT_PATH"
  - id: "N_COLLECT_ALIAS"
  - id: "N_COLLECT_SOURCE_FIELD"

required_gates:
  - "G_CONTRACT_CONFIRMED"
  - "G_PRE_ARCHIVE_APPROVAL"
  - "G_RENDERED_ARTIFACT_VALIDATED"
```

In other words, Ordo makes the hidden logic of a playbook explicit.

![Nebu — thinking: hidden logic should become explicit nodes, state, and gates](../assets/mascots/64x64/Nebu_thinking_64x64.png)

---

## Main Migration Stages

Migration is best described as a sequence of ten steps.

```text
1. Inventory
2. Classification
3. Contract extraction
4. Decision tree extraction
5. State model extraction
6. Gate extraction
7. Output mapping
8. FREEFORM binding
9. Test layer creation
10. IR compilation and validation
```

---

## Step 1. Inventory

First, we need to understand what the playbook actually contains.

Create a catalog of fragments:

```yaml
source_catalog:
  sections:
    - id: "S01_INTRO"
      type: "explanation"
    - id: "S02_DECISION_TREE"
      type: "decision_logic"
    - id: "S03_OUTPUT_PACKAGE"
      type: "output_rules"
    - id: "S04_QA"
      type: "qa_rules"
```

This step helps prevent knowledge from being lost during migration.

---

## Step 2. Classification

Next, classify every fragment.

Minimum categories include:

```text
- rule
- node
- gate
- status
- output
- template
- example
- anti-pattern
- freeform note
- improvement note
```

For example:

```yaml
fragment:
  id: "F_SELF_CHECK_BEFORE_ARCHIVE"
  original_type: "markdown paragraph"
  classified_as:
    - "gate"
    - "assert_not"
    - "test_candidate"
```

This matters because different fragment types become different Ordo constructs.

---

## Step 3. Contract Extraction

Every complex playbook has conditions without which the work cannot be considered sufficiently defined.

For a History Event package, such conditions may include:

```text
- confirmed alias;
- confirmed event type;
- confirmed source field;
- understood old/new values;
- understood path;
- confirmed expected outputs;
- confirmed QA expectations.
```

In Ordo, this becomes a contract:

```yaml
contract:
  required_inputs:
    - "event_alias"
    - "source_field"
    - "path_type"
    - "expected_values"

  missing_input_behavior:
    action: "ask_next_required_question"
    final_output_allowed: false
```

The main rule is:

![Nebu — attention: without a complete contract, final output is not allowed](../assets/mascots/64x64/Nebu_attention_64x64.png)

```text
if the contract has not been collected, the playbook must not proceed to final output
```

---

## Step 4. Decision Tree Extraction

If a playbook contains different scenarios, they should be extracted into a decision tree.

For example:

```yaml
paths:
  - id: "A1"
    name: "direct source field change"
    condition: "change detected in primary source row"

  - id: "A2"
    name: "related entity change"
    condition: "change belongs to entity linked through identification center"

  - id: "A4"
    name: "external history event"
    condition: "input is ExternalHistoryEvent candidate"
```

In debug mode, Ordo should show not only the selected path but also rejected paths:

```yaml
path_explain:
  selected: "A1"
  rejected:
    - path: "A2"
      reason: "related entity was not confirmed"
    - path: "A4"
      reason: "no external event input"
```

---

## Step 5. State Model Extraction

Markdown often hides state inside prose.

For example:

```text
When the analyst confirms the source field, the process may proceed to values.
```

In Ordo, this should become a state transition:

```yaml
state:
  source_field_confirmed: true
  next_node: "N_COLLECT_VALUES"
```

You need to define:

```text
- which state fields exist;
- who may change them;
- which values mean readiness;
- which values block the process;
- which transitions are allowed;
- which transitions are forbidden.
```

Without a state model, the model will “keep the process in its head,” which is unreliable.

---

## Step 6. Gate Extraction

A gate is a point where the process must stop or check a condition.

During migration, look for phrases such as:

```text
- before;
- only after;
- must be checked;
- must not be created;
- must be confirmed;
- if undefined, stop;
- do not continue without this.
```

Such phrases are almost always candidates for `GATE.DEF` or `ASSERT.NOT`.

Example:

```yaml
- op: "GATE.DEF"
  id: "G_PRE_ARCHIVE_APPROVAL"
  type: "blocking"
  before: "OUTPUT.FINAL_ARCHIVE"
  condition: "user_approval == true"
```

---

## Step 7. Output Mapping

Next, define exactly what the playbook must create.

For a simple process, this may be one document. For a complex one, it may be a package of files.

Ordo should describe output explicitly:

```yaml
outputs:
  - id: "O_ANALYTICAL_PACKAGE"
    kind: "file_set"
    required_files:
      - "README.md"
      - "SUMMARY.json"
      - "VALIDATION_REPORT.json"
      - "CONSISTENCY_CHECK_REPORT.json"
```

Rendered validation must also be described:

```yaml
render_validate:
  required:
    - "all_required_files_present"
    - "no_unexpected_files"
    - "no_unresolved_placeholders"
    - "cross_file_consistency_passed"
```

Output without validation is a weak point.

---

## Step 8. FREEFORM Binding

After the first seven steps, part of the playbook will still remain unformalized.

That is normal.

But it should be represented as controlled FREEFORM:

```yaml
freeform:
  id: "FF_DOMAIN_EDGE_CASES"
  type: "domain_notes"
  bound_to:
    - "PATH.A4"
    - "G_EXTERNAL_EVENT_NORMALIZED"
  reason: "edge cases are described as examples and not yet stable enough for full formalization"
```

The main rule is:

```text
FREEFORM must be bound to a specific part of execution
```

---

## Step 9. Test Layer Creation

After migration, create a test layer.

The minimum set includes:

```text
- one happy-path test for each path;
- negative tests for forbidden actions;
- gate tests;
- no-op tests;
- rendered artifact validation tests;
- regression suite.
```

Example:

```yaml
test:
  id: "TC_A1_HAPPY_PATH"
  fixture:
    user_message: "create a status change event"
  expected:
    path: "A1"
    gates:
      - id: "G_CONTRACT_CONFIRMED"
        status: "passed"
    output:
      package_created: true
```

Testing is what distinguishes an Ordo migration from merely rewriting a document.

---

## Step 10. IR Compilation and Validation

The final step is to compile Ordo Source into Semantic JSON IR and verify that all important parts of the playbook are represented.

The result should include:

```text
- compiled IR;
- traceability report;
- validation report;
- consistency check report;
- coverage report;
- freeform coverage report;
- regression suite summary.
```

If part of the playbook is not covered, that is not always an error. But it must be visible.

For example:

```yaml
migration_report:
  structured_core: "72%"
  controlled_freeform: "28%"
  uncovered_fragments: 0
  blocking_gates_defined: 14
  tests_defined: 18
  status: "passed_with_notes"
```

---

## Minimum Migration Result

After migration, the result should not be one large file but a set of linked artifacts.

For example:

```text
START_HERE_ORDO.md
ORDO_EXECUTION_CONTRACT.md
ORDO_CORE_BINDING.md
ORDO_PROFILE_BINDINGS.md
DOMAIN_PACK.md
PLAYBOOK_ORDO_SOURCE.md
PLAYBOOK_COMPILED_IR.json
FREEFORM_LEDGER.md
FREEFORM_COVERAGE.md
VALIDATION_REPORT.json
CONSISTENCY_CHECK_REPORT.json
```

This is not simply “more files.” These are different runtime views of the same process.

---

## How to Know Whether Migration Succeeded

Migration is successful if you can answer “yes” to the following questions:

```text
1. Is it clear which entry starts the process?
2. Is there a contract?
3. Is there a state model?
4. Are there decision paths?
5. Are there blocking gates?
6. Are outputs defined?
7. Is rendered validation present?
8. Is it clear what remains in FREEFORM?
9. Are there tests?
10. Can you explain why a run followed a particular path?
```

If the answer is “no” to several items, the playbook has not yet become a complete Ordo program.

---

## Typical Mistakes

### Mistake 1. Starting with IR

Do not begin by writing JSON IR manually.

First understand the contract, paths, state, and gates. IR is a compiled representation, not the first document from which work should begin.

---

### Mistake 2. Losing the Link to the Old Playbook

If, after migration, you cannot say where a rule came from, that is a problem.

A traceability matrix is required.

---

### Mistake 3. Formalizing Examples as Rules

An example shows a possible situation. A rule defines mandatory behavior.

These are different things.

---

### Mistake 4. Failing to Identify Blocking Gates

If a gate is not blocking, the model may continue even after a failed condition.

For critical processes, this is unacceptable.

---

### Mistake 5. Not Adding an Improvement Loop

The playbook will not become perfect after the first migration.

A mechanism for collecting problems and improvements should exist from the start.

---

## Mini-Exercise

Take one section of an old playbook and try a mini-migration.

Fill in this table:

```text
Fragment | Type | Ordo object | Gate? | Test needed? | FREEFORM?
```

For example:

```text
“Do not create an archive without self-check”
→ anti-pattern / gate candidate
→ ASSERT.NOT + GATE.DEF
→ yes
→ yes
→ no
```

This is a simple way to see how text begins to turn into an Ordo program.

---

## Short Summary

Migrating a playbook to Ordo is not rewriting a document in different words.

It is the extraction of executable structure:

```text
knowledge → rules → state → paths → gates → outputs → tests → IR
```

The main idea of this chapter is:

```text
an Ordo migration succeeds when a playbook can not only be read, but also executed, explained, verified, and improved
```

---

---

## The ARF legacy-instruction migration route

ARF treats legacy instruction migration as a dedicated factory mode rather than as informal rewriting. The route is:

```text
source intake
→ clause inventory
→ dependency reconstruction
→ Ordo mapping
→ completeness gate
→ shared package-generation tail
```

`source intake` records the authoritative source set. `clause inventory` ensures that every meaningful rule, prohibition, template dependency, approval, and output obligation is accounted for. `dependency reconstruction` makes hidden ordering and state dependencies explicit. `Ordo mapping` assigns clauses to contracts, nodes, gates, state, outputs, validators, or bounded freeform. The completeness gate blocks integration while any authoritative clause remains unmapped, duplicated without justification, or weakened.
