# Chapter 10. Why Semantic JSON IR Is the Best Choice Right Now

## 10.1. Why an IR Is Needed at All

In the previous chapter, we established that Ordo Source is a human-friendly form of a program. It can be read, discussed, edited, and reviewed with an analyst or developer. It resembles a well-structured YAML document in which intent, contract, state, gates, outputs, and handoff are visible.

But Ordo Source is not yet the best form for model execution.

A person can comfortably read:

```yaml
intent:
  goal: summarize_text

contract:
  output:
    format: bullet_list
    max_items: 3
    language: uk

rules:
  - use_only_input_text
  - do_not_invent_facts
```

A model can understand this too. But when a process grows to dozens of nodes, gates, statuses, libraries, templates, domain rules, and FREEFORM blocks, human-oriented YAML becomes too flexible. Fields may be nested differently. Some rules may be written as prose. Some links may remain implicit.

That is why an intermediate layer is needed: IR.

![Nebu — idea: IR as an execution form](../assets/mascots/64x64/Nebu_idea_64x64.png)

IR means Internal Representation.

In Ordo, IR is a form of the program designed primarily for more precise execution by a model or a future Ordo runtime rather than for comfortable human reading.

Ordo Source answers:

```text
How can a person conveniently describe the process?
```

Ordo IR answers:

```text
How can a model or runtime execute the process more reliably?
```

This distinction is fundamental.

## 10.2. Why Not Keep Only YAML

YAML may seem sufficient. It is readable, structured, and far better than one continuous prompt. For many simple tasks, it is sufficient.

But YAML remains an authoring format. It is good for writing and discussing an instruction, while execution exposes several weaknesses.

First, YAML does not always define strict execution order.

For example:

```yaml
steps:
  - read_input
  - extract_points
  - render_summary

gates:
  - input_present
  - no_unsupported_facts
```

A person understands that the gates should be applied at the correct moments. A model may not always know whether `input_present` runs before `extract_points`, after it, or only before handoff.

Second, YAML often allows levels to be mixed. Machine-readable fields and long human explanations may appear side by side.

Third, YAML is readable but not always easy to execute or validate. A runtime or weaker model benefits from a list of concrete operations:

```json
[
  {"op": "INTENT.SET", "goal": "summarize_text"},
  {"op": "CONTRACT.DEF", "output": {"format": "bullet_list", "max_items": 3}},
  {"op": "STEP.RUN", "fn": "READ_INPUT_TEXT"},
  {
    "op": "GATE.CHECK",
    "method": "mechanical",
    "trust_class": "deterministic",
    "assert": "INPUT_TEXT_PRESENT"
  }
]
```

Now the representation shows not only what exists in the program, but what must be done.

That is why Ordo Source and IR should remain separate layers.

## 10.3. Why Semantic JSON IR

At the current stage of AI-model development, the best primary IR for Ordo is Semantic JSON IR.

This means a JSON structure in which each operation has an explicit `op`, `id`, parameters, inputs, outputs, bindings, and expected behavior.

For example:

```json
{
  "op": "GATE.CHECK",
  "id": "G_NO_UNSUPPORTED_FACTS",
  "method": "self_verification",
  "trust_class": "model_judgment",
  "assert": "NO_UNSUPPORTED_FACTS",
  "source": "RESULT.summary",
  "on_fail": "REPAIR.REMOVE_UNSUPPORTED"
}
```

This is not JSON for the sake of JSON. The important word is Semantic.

Semantic JSON IR means that the structure directly carries execution meaning.

`op` says which action to perform.

`id` provides a stable identifier.

`assert` says what is checked.

`source` says what the check applies to.

`on_fail` says what happens after failure.

This form works well for models because it is simultaneously:

- structured enough;
- understandable enough;
- not excessively compressed;
- independent of a special binary or native runtime format;
- easy for a person to inspect;
- easy to map to a future runtime.

## 10.4. Why Not Compact Opcode IR Immediately

We have already seen a compact form:

```json
[
  ["I", "summarize_text", "uk"],
  ["C", {"out": {"type": "bullets", "max": 3}}],
  ["G", "NO_UNSUPPORTED_FACTS", "summary", "REPAIR.REMOVE_UNSUPPORTED"]
]
```

It is short and looks attractive as a future machine-native representation. But it is risky for current models.

Compactness reduces obviousness.

![Nebu — attention: compactness does not always help](../assets/mascots/64x64/Nebu_attention_64x64.png)

A person or model must remember what `I`, `C`, and `G` mean, the order of arguments, allowed values, and failure behavior. That is normal for a specially trained runtime. It is not yet ideal for a general language model.

Compact Opcode IR may become a good future format when:

```text
the model is specifically trained on Ordo;
or an Ordo execution layer exists;
or a compiler/runtime executes the opcodes itself;
or Compact IR is used only as an internal format rather than as the primary LLM instruction.
```

At the practical stage, there is no need to rush.

Semantic JSON IR is a compromise between human intelligibility and machine precision.

## 10.5. Why Not Just Natural Language

Natural language is powerful. It lets us explain complex ideas without formal schemas. But it is often ambiguous.

For example:

```text
Do not create the final package if the contracts are not confirmed.
```

A person understands the intention. Execution still raises questions:

- which contracts are mandatory;
- what `confirmed` means;
- where the condition is checked;
- which status is set on failure;
- whether a draft package is allowed;
- whether the user must be asked;
- whether this is a hard stop;
- whether the rule applies to all outputs or only the archive.

Semantic JSON IR can describe the rule more precisely:

```json
{
  "op": "GATE.CHECK",
  "id": "G_NO_FINAL_ARCHIVE_BEFORE_CONTRACTS",
  "method": "mechanical",
  "trust_class": "deterministic",
  "assert": "ALL_MANDATORY_CONTRACTS_CONFIRMED",
  "scope": "final_archive",
  "on_fail": "BLOCK_FINAL_ARCHIVE",
  "failed_status": "no_go_requires_confirmation"
}
```

There is less room for accidental interpretation.

Natural language remains important in `FREEFORM`, explanations, descriptions, and templates. Hard rules, however, are better represented as structured operations.

## 10.6. The Same Instruction in Three Forms

Consider a simple rule:

```text
Before the final result, check that there are no invented facts.
```

Natural language is understandable but not very formal.

In Ordo Source:

```yaml
gates:
  - id: no_unsupported_facts
    check: no_unsupported_facts
    source: result
    on_fail: remove_or_mark_unsupported
```

In Semantic JSON IR:

```json
{
  "op": "GATE.CHECK",
  "id": "G_NO_UNSUPPORTED_FACTS",
  "method": "self_verification",
  "trust_class": "model_judgment",
  "assert": "NO_UNSUPPORTED_FACTS",
  "source": "RESULT.primary",
  "on_fail": "REPAIR.REMOVE_OR_MARK_UNSUPPORTED"
}
```

In Compact Opcode IR:

```json
["G", "NO_UNSUPPORTED_FACTS", "RESULT.primary", "REPAIR.REMOVE_OR_MARK_UNSUPPORTED"]
```

All three forms describe the same idea, but they serve different roles.

![Nebu — thinking: one instruction in three forms](../assets/mascots/64x64/Nebu_thinking_64x64.png)

Natural language is for explanation.

Ordo Source is for the author.

Semantic JSON IR is for execution by a current model or runtime.

Compact Opcode IR is for future optimized execution.

## 10.7. Main Advantages of Semantic JSON IR

Semantic JSON IR has several strong advantages.

### 1. Explicit Execution Order

IR can be a list of operations. The model receives a sequence rather than merely a set of rules:

```text
first load documentation;
then determine entry;
then ask the node question;
then update state;
then check the gate;
then move to the next node.
```

This is especially important for playbooks.

### 2. Stable Identifiers

Every operation has an `id`.

This allows explicit references:

```json
{
  "op": "APPROVAL.REQUIRE",
  "id": "A_PASSPORT_APPROVAL",
  "target": "OUTPUT.01_HISTORY_EVENT_PASSPORT"
}
```

A validation report can later say:

```json
{
  "approval_id": "A_PASSPORT_APPROVAL",
  "status": "passed"
}
```

This creates traceability.

### 3. Simple Logging

When a program executes step by step, the runtime or model can maintain a trace:

```json
{
  "executed_op": "G_CONTRACTS_CONFIRMED",
  "status": "failed",
  "reason": "source_field_paths missing",
  "next_action": "ASK_CONFIRMATION"
}
```

This is much more informative than “some data needs clarification.”

### 4. Easier Gate Validation

A structured gate is easier to inspect and potentially automate:

```json
{
  "op": "ASSERT.NOT",
  "id": "A_NO_ITEM_PREFIX_IN_DELTA_FIELD",
  "target": "ChangeRecord.delta.field",
  "forbidden_pattern": "^item\\."
}
```

This is already close to an executable check.

### 5. Easier Portability Between Models

The same Semantic JSON IR can be given to different models. Their response style may differ, but the task structure remains stable.

This matters for Ordo as a future standard.

## 10.8. Disadvantages of Semantic JSON IR

Semantic JSON IR is not perfect.

Its main disadvantage is length. One gate may occupy a single line in compact form and ten lines in Semantic JSON IR.

That length buys clarity.

The second disadvantage is the need for discipline. If every author invents new operation names, the IR quickly becomes chaotic. Ordo therefore needs a standard operation catalog.

The third disadvantage is that JSON is not pleasant to write manually. That is why a person writes Ordo Source and a compiler or model assistant translates it into IR.

Semantic JSON IR is not necessarily what an analyst should write by hand. It is what the model should receive for execution.

## 10.9. The Role of the Compiler

In a mature Ordo architecture, a compiler or translator should sit between the person and the model.

A person writes or says:

```text
I want the model to guide the analyst through a tree, collect contracts, avoid creating the final package without confirmation, and validate documents before archiving.
```

The compiler turns this into Ordo Source:

```yaml
entry:
  id: guided_intake

state:
  contracts_confirmed: false
  approvals: pending

gates:
  - no_final_archive_before_contracts
  - rendered_artifacts_validated
```

Then it compiles the source into Semantic JSON IR:

```json
[
  {"op": "ENTRY.DEF", "id": "guided_intake"},
  {"op": "STATE.SCHEMA", "fields": {"contracts_confirmed": "boolean"}},
  {
    "op": "GATE.CHECK",
    "id": "G_NO_FINAL_ARCHIVE",
    "method": "mechanical",
    "trust_class": "deterministic",
    "assert": "ALL_CONTRACTS_CONFIRMED"
  }
]
```

The model no longer has to extract the entire process from prose. It receives a structured execution map.

## 10.10. Why This Matters for Weaker Models

A strong model can often infer what the author intended. A weaker model may not.

Ordo should not be useful only for the strongest model. One of its purposes is to make complex instructions executable even by models that hold long context less reliably.

Semantic JSON IR helps weaker models because it:

- reduces ambiguity;
- makes order explicit;
- separates operations;
- provides stable statuses;
- shows what to do on failure;
- reduces the need to guess.

It is easier for a weaker model to execute:

```json
{"op": "NODE.ASK", "id": "N1", "allowed_answers": ["A", "B", "C"]}
```

than a long instruction explaining that the first tree question should be asked only if the path is not yet selected.

## 10.11. Why This Matters for a Future Runtime

Semantic JSON IR is also a bridge to a future Ordo runtime.

A runtime may perform part of the work without a model:

- maintain state;
- determine the current node;
- validate allowed answers;
- run gates;
- check status transitions;
- determine which documents to load;
- block the final archive;
- generate validation reports.

The model then does what it does best:

- explains questions to the user;
- interprets answers;
- forms document content;
- works with domain prose;
- writes understandable text.

The runtime controls the process; the model fills the semantic content.

This is an important strategic idea in Ordo.

## 10.12. Practical Format-Selection Rule

For the current Ordo version, the rule can be stated as follows:

```text
Ordo Source — primary format for people.
Semantic JSON IR — primary format for model execution.
Compact Opcode IR — future format for optimization or a native runtime.
FREEFORM — controlled container for content that cannot be safely formalized.
```

If you write a playbook manually, start with Ordo Source.

If you give an instruction to a model or runner, prefer Semantic JSON IR.

If a specialized Ordo runtime appears, it may compile Semantic JSON IR into a compact or native form.

## 10.13. Typical Mistakes

### Mistake 1. Giving the Model Only YAML and Expecting Runtime Behavior

YAML helps, but it does not guarantee execution. Complex processes need an execution map.

### Mistake 2. Moving to Compact Opcodes Too Early

Compact representation looks elegant, but current models benefit from semantic structure.

### Mistake 3. Hiding Prose Rules Inside `description`

If a rule blocks an action, it should be a gate or assertion rather than only prose.

### Mistake 4. Having No Stable IDs

Without IDs, reliable traceability, validation reports, and source maps are impossible.

### Mistake 5. Allowing Different `op` Values for the Same Meaning

If one author writes `CHECK.GATE`, another writes `GATE.CHECK`, and a third writes `VALIDATE`, the standard begins to fragment. A standard operation catalog is required.

## 10.14. Short Chapter Summary

Semantic JSON IR is currently the best primary execution format for Ordo because it balances readability and strictness.

It is better than pure natural language because it is less ambiguous.

It is better than YAML as an execution layer because it explicitly describes operations and order.

It is more practical than Compact Opcode IR because current models can understand it more easily.

The main rule is:

```text
A person writes Ordo Source.
A model or runtime executes Semantic JSON IR.
A future native runtime may use Compact Opcode IR.
```

Semantic JSON IR is the bridge between human instruction and controlled AI-model execution.

## Mini-Exercise

Take this simple instruction:

```text
Ask the user to select a task type. If they select incident, ask about severity. If the answer is not one of the allowed options, ask again.
```

Write it in three forms:

1. natural language;
2. Ordo Source;
3. Semantic JSON IR.

Compare which form makes these elements clearest:

- allowed answers;
- current node;
- state update;
- error handling;
- next node.

If Semantic JSON IR makes them most explicit, you have understood the main idea of this chapter.

---

<!-- REVIEWED: chapter 10; Nebu markers checked -->
