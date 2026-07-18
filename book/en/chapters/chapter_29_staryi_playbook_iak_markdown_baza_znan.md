# Chapter 29. The Old Playbook as a Markdown Knowledge Base

## Why This Is Needed

Many complex instructions are born not as a language, a program, or a formal workflow. They begin as a large Markdown document: rules, examples, exceptions, tables, reminders, checklists, historical explanations, and decisions once made in chats or tasks.

Such a document can be extremely useful. It preserves team knowledge. It explains context. It shows how an analyst thinks about the process. The problem is that a large Markdown playbook is not an executable instruction.

![Nebu — idea: a Markdown playbook is a knowledge base, not a runtime](../assets/mascots/64x64/Nebu_idea_64x64.png)

A model can read it, but that does not mean it will execute it the same way every time.

It may:

```text
- skip an important gate;
- confuse an example with a rule;
- treat an outdated fragment as current;
- use an instruction for the wrong path;
- forget that a decision requires human confirmation;
- read an all-in-one document as ordinary text rather than as a process.
```

This is why an old Markdown playbook should be treated not as the final format but as a knowledge base from which an Ordo program is gradually extracted.

---

## Simple Explanation

An old playbook is like a large folder of instructions on a desk.

It may contain everything:

```text
- process descriptions;
- business rules;
- technical rules;
- examples;
- exceptions;
- templates;
- checklists;
- decision history;
- notes for the future;
- warnings about mistakes.
```

But if a person or model is told to “just execute everything in this folder,” a problem appears: it is unclear what is mandatory, what is reference material, what is an example, what is an old note, and what is an active rule.

Ordo proposes a different approach:

```text
Markdown playbook → knowledge source → structured extraction → Ordo Source → compiled IR → execution
```

The old playbook is not discarded. It becomes a knowledge source. But execution should happen not directly from chaotic text, but through a structured Ordo layer.

---

## What Is Useful in an Old Playbook

In an old Markdown playbook, it is important not only to find ready-made rules. Different types of information must also be classified correctly.

For example:

```text
1. Mandatory rules
2. Decision tree
3. Questions / intake flow
4. Gates
5. Output templates
6. QA rules
7. Validation rules
8. Examples
9. Anti-patterns
10. Domain notes
11. Historical decisions
12. Process improvement feedback
```

These do not all have the same status.

A mandatory rule should become a gate or assertion.

A decision tree should become a set of `NODE.DEF` and path rules.

A template should become `OUTPUT.DEF` or `TEMPLATE.BIND`.

An example may remain in FREEFORM, but with a binding to a specific rule or node.

A warning about a common mistake may become `ASSERT.NOT`.

User feedback may become an `IMPROVEMENT.RECORD` or regression test.

---

## Why All-in-One Markdown Is Dangerous

An all-in-one document appears convenient because everything is in one place. But as an execution format, it is dangerous.

![Nebu — attention: all-in-one is dangerous as a runtime source](../assets/mascots/64x64/Nebu_attention_64x64.png)

Reasons include:

```text
- the model may get lost in a long context;
- different parts of the document may contradict one another;
- an old note may look like an active rule;
- an example may be executed incorrectly as a universal template;
- it is difficult to understand which rules cover which path;
- it is difficult to debug which fragment influenced a decision;
- it is difficult to test whether a change broke an old scenario.
```

In Ordo, all-in-one may be useful as a rendered artifact or archival form, but not as the main runtime source.

The main runtime source should be structured.

---

## How Ordo Views a Markdown Playbook

Ordo does not say:

```text
Markdown is bad.
```

Ordo says:

```text
Markdown is good for explanation, but insufficient for controlled execution.
```

The old playbook should therefore be divided into layers:

```text
1. Human explanation layer
   Text for people.

2. Ordo Source layer
   Human-readable structured program.

3. Semantic JSON IR layer
   Machine-oriented execution map.

4. Debug/Test layer
   Traces, tests, coverage, improvement records.
```

Markdown may remain in the first layer. But everything that affects execution must either be formalized or explicitly bound as controlled FREEFORM.

---

## Example of Fragment Classification

Imagine that an old playbook contains this sentence:

```text
Before creating the final archive, a self-check must be performed and the package must be checked for extra files.
```

In Markdown, this is merely a sentence.

In Ordo, it should become:

```yaml
- op: "GATE.DEF"
  id: "G_PACKAGE_SELF_CHECK"
  type: "blocking"
  before: "HANDOFF.FINAL_PACKAGE"
  requires:
    - "validation_report.status == passed"
    - "unexpected_files == []"
```

And also a negative assertion:

```yaml
- op: "ASSERT.NOT"
  id: "A_NO_HANDOFF_WITHOUT_SELF_CHECK"
  condition: "final_package_created == true and self_check_passed != true"
  severity: "blocking"
```

And a test case:

```yaml
test:
  id: "TC_NO_PACKAGE_WITHOUT_SELF_CHECK"
  method: mechanical
  trust_class: deterministic
  expected:
    gate: "G_PACKAGE_SELF_CHECK"
    final_package_created: false
```

This is how one sentence from Markdown becomes an executable part of an Ordo program.

---

## What Should Not Be Formalized Immediately

Not every part of an old playbook needs to be converted into strict opcodes immediately.

Some parts may temporarily remain in controlled FREEFORM:

```text
- long business explanations;
- examples for an analyst;
- historical reasons why a rule exists;
- edge cases that have not yet stabilized;
- term explanations;
- domain commentary.
```

But every FREEFORM block should have a binding:

```yaml
freeform:
  id: "FF_HISTORY_EVENT_EDGE_CASES"
  bound_to:
    - "NODE.SELECT_PATH"
    - "G_SOURCE_FIELD_CONFIRMED"
  reason: "domain examples are not yet fully formalized"
```

Without binding, FREEFORM becomes chaotic Markdown again.

---

## The Role of Traceability

When migrating an old playbook, it is important not to lose the connection between the old text and the new Ordo constructs.

A traceability matrix is therefore needed:

![Nebu — thinking: preserve the connection between old text and Ordo objects](../assets/mascots/64x64/Nebu_thinking_64x64.png)

```text
old fragment → Ordo Source object → IR op → test coverage → rendered artifact
```

For example:

```yaml
traceability:
  source_fragment: "section_12.self_check_before_archive"
  mapped_to:
    - "G_PACKAGE_SELF_CHECK"
    - "ASSERT.NOT.A_NO_HANDOFF_WITHOUT_SELF_CHECK"
    - "TC_NO_PACKAGE_WITHOUT_SELF_CHECK"
```

This makes it possible to answer:

```text
- where does this rule now live in Ordo?
- is it covered by a test?
- is it blocking?
- does it enter compiled IR?
- is it used during execution?
```

---

## Typical Mistakes

### Mistake 1. Simply Renaming Markdown to Ordo

If an old Markdown document is renamed Ordo Source, nothing changes.

Ordo requires structure: nodes, gates, state, outputs, tests, and traceability.

---

### Mistake 2. Moving Everything into FREEFORM

FREEFORM is a controlled escape hatch, not a dumping ground for unformatted rules.

If everything remains in FREEFORM, Ordo gains no controllability.

---

### Mistake 3. Losing Decision History

During formalization, it is easy to discard explanations of why a rule appeared.

But history matters for future improvement. It can be preserved as a note, evidence, or improvement history.

---

### Mistake 4. Not Adding Tests

Migration without tests is a cosmetic change.

An Ordo migration should end with a test layer and coverage report.

---

### Mistake 5. Not Validating Rendered Artifacts

If a playbook generates documents or packages, the finished result must be validated, not only the rules.

---

## Mini-Exercise

Take any large instructional document.

Mark its fragments using five colors or categories:

```text
1. rule
2. gate
3. example
4. explanation
5. warning / anti-pattern
```

Then, for each rule, try to answer:

```text
- should this become NODE, GATE, ASSERT.NOT, OUTPUT, or FREEFORM?
- does it need a test?
- should this rule be blocking?
- does it always apply, or only to one path?
```

This is the first step toward migrating an old playbook into Ordo.

---

## Short Summary

An old Markdown playbook is a valuable knowledge base, but not a reliable execution format.

Ordo does not destroy Markdown. It extracts executable structure from it:

```text
rules → gates
questions → nodes
templates → outputs
warnings → ASSERT.NOT
examples → controlled FREEFORM
decisions → state/status semantics
feedback → improvement records
```

The main idea of this chapter is:

```text
an old playbook is a knowledge source, not the runtime execution layer
```

---
