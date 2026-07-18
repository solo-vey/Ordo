# Chapter 9. Compiling Ordo Source into Semantic JSON IR

## 9.1. Why Compile Anything at All

Ordo Source is designed for people. It should be readable, discussable, and convenient to edit.

Execution has different needs.

A model or runtime benefits from explicit operations, stable identifiers, ordered steps, visible gates, state updates, and defined failure behavior. If all of this remains only in a human-oriented document, the executor must repeatedly interpret the author's intent.

Compilation reduces that interpretive burden.

![Nebu — idea: compilation creates an execution form](../assets/mascots/64x64/Nebu_idea_64x64.png)

The basic flow is:

```text
Ordo Source
    ↓
compiler / translator
    ↓
Semantic JSON IR
    ↓
model or runtime execution
```

Compilation does not mean turning Ordo into a conventional programming language. It means projecting human-readable process semantics into a more explicit execution representation.

## 9.2. What Semantic JSON IR Is

Semantic JSON IR is Ordo's structured intermediate representation.

It is **semantic** because every operation carries execution meaning.

It is **JSON** because the representation is explicit, portable, and easy to inspect or process.

It is **IR** because it sits between authoring and execution.

A small operation may look like this:

```json
{
  "op": "INTENT.SET",
  "id": "I_SUMMARIZE_TEXT",
  "goal": "summarize_text",
  "language": "uk"
}
```

The important part is not the braces. The important part is that the executor no longer has to infer whether the text describes a goal, a rule, a gate, or an output. The `op` makes the operation class explicit.

## 9.3. Why JSON

JSON is not chosen because it is the most pleasant format for authors. It is not.

It is useful because:

```text
objects and arrays are explicit;
field names are visible;
nesting is deterministic;
the format is widely supported;
schemas can validate it;
runtime tools can consume it;
models are already familiar with it.
```

A person should normally write Ordo Source. The compiler should produce JSON IR.

The authoring format and the execution format do not need to be identical.

## 9.4. Ordo Source and IR in One Example

Consider this source fragment:

```yaml
intent:
  goal: summarize_text
  language: uk

contract:
  output:
    format: bullet_list
    max_items: 3
  rules:
    - do_not_invent_facts

context:
  source:
    text: "$USER_INPUT.text"

path:
  steps:
    - read_input_text
    - extract_supported_points
    - render_summary

  gates:
    - id: no_unsupported_facts
      check: no_unsupported_facts
      on_fail: remove_or_mark_unsupported
```

A semantic IR projection may be:

```json
[
  {
    "op": "INTENT.SET",
    "id": "I_SUMMARIZE_TEXT",
    "goal": "summarize_text",
    "language": "uk"
  },
  {
    "op": "CONTRACT.DEF",
    "id": "C_SUMMARY_OUTPUT",
    "output": {
      "format": "bullet_list",
      "max_items": 3
    }
  },
  {
    "op": "RULE.ADD",
    "id": "R_NO_INVENTED_FACTS",
    "rule": "do_not_invent_facts"
  },
  {
    "op": "CONTEXT.LOAD",
    "id": "CTX_USER_TEXT",
    "source": "$USER_INPUT.text",
    "bind": "STATE.input_text"
  },
  {
    "op": "STEP.RUN",
    "id": "S_READ_INPUT",
    "fn": "READ_INPUT_TEXT"
  },
  {
    "op": "STEP.RUN",
    "id": "S_EXTRACT_POINTS",
    "fn": "EXTRACT_SUPPORTED_POINTS"
  },
  {
    "op": "STEP.RUN",
    "id": "S_RENDER_SUMMARY",
    "fn": "RENDER_SUMMARY"
  },
  {
    "op": "GATE.CHECK",
    "id": "G_NO_UNSUPPORTED_FACTS",
    "method": "self_verification",
    "trust_class": "model_judgment",
    "assert": "NO_UNSUPPORTED_FACTS",
    "source": "RESULT.summary",
    "on_fail": "REPAIR.REMOVE_OR_MARK_UNSUPPORTED"
  },
  {
    "op": "HANDOFF.EMIT",
    "id": "H_FINAL",
    "include": ["status", "result", "gate_report"]
  }
]
```

The source is easier to author.

The IR is easier to execute step by step.

## 9.5. What the Compiler Actually Does

A compiler should not merely convert YAML syntax into JSON syntax.

That would be serialization, not semantic compilation.

The compiler must recognize the role of each construct and project it into execution operations.

For example:

```text
intent        → INTENT.SET
contract      → CONTRACT.DEF
rule          → RULE.ADD
context       → CONTEXT.LOAD
state         → STATE.INIT / STATE.UPDATE
step          → STEP.RUN
gate          → GATE.CHECK
approval      → APPROVAL.REQUIRE
output        → OUTPUT.DEF
handoff       → HANDOFF.EMIT
```

The compiler may also:

- normalize identifiers;
- resolve references;
- expand shorthand;
- attach source-map information;
- validate operation names;
- detect missing required fields;
- preserve controlled FREEFORM blocks;
- emit diagnostics for ambiguous constructs.

A compiler must not invent domain rules merely because they look plausible.

## 9.6. Compilation Must Not Distort Meaning

The most important compiler rule is semantic preservation.

If the source says:

```text
final archive is blocked until mandatory contracts are confirmed
```

the IR must not weaken it to:

```text
prefer confirmation before creating the archive
```

If the source distinguishes:

```text
candidate
proposed
confirmed
blocked
ready_for_first_run
```

the IR must preserve those distinctions.

Compilation may make semantics more explicit. It must not silently change them.

![Nebu — attention: compilation must preserve meaning](../assets/mascots/64x64/Nebu_attention_64x64.png)

A useful principle is:

```text
Source meaning in
    ↓
explicit execution meaning out
```

not:

```text
Source meaning in
    ↓
compiler interpretation
    ↓
new policy out
```

When the compiler cannot safely formalize a fragment, it should preserve the fragment in a controlled `FREEFORM` representation or emit a diagnostic.

## 9.7. Source Map: How Not to Lose the Link to Human Text

Compilation creates another representation of the program. We therefore need to know where each IR operation came from.

That is the role of a source map.

Example:

```json
{
  "ir_id": "G_NO_UNSUPPORTED_FACTS",
  "source": {
    "file": "minimal_summary.ordo.yaml",
    "path": "path.gates[1]",
    "line_start": 31,
    "line_end": 34
  }
}
```

A source map helps answer:

```text
Which source construct created this operation?
Where should the author edit the rule?
Did two source fragments compile into one op?
Was any source fragment lost?
```

Without a source map, IR becomes detached from the human source of truth.

This is especially dangerous during review and debugging.

## 9.8. Execution Trace: What the Model Actually Executed

A source map describes the relation between source and IR.

An execution trace describes what happened during a concrete run.

For example:

```json
{
  "run_id": "RUN-2026-0017",
  "events": [
    {
      "op_id": "S_READ_INPUT",
      "status": "completed"
    },
    {
      "op_id": "S_EXTRACT_POINTS",
      "status": "completed",
      "output_ref": "ARTIFACT.points.1"
    },
    {
      "op_id": "G_NO_UNSUPPORTED_FACTS",
      "status": "failed",
      "reason": "one point has no source support"
    },
    {
      "op_id": "REPAIR.REMOVE_OR_MARK_UNSUPPORTED",
      "status": "completed"
    },
    {
      "op_id": "G_NO_UNSUPPORTED_FACTS",
      "status": "passed"
    }
  ]
}
```

The trace makes the run reproducible and inspectable.

It can show:

- which operations executed;
- in which order;
- which gates passed or failed;
- which repairs ran;
- which state fields changed;
- which outputs were created;
- which prompt or behavior version was used.

The trace is not the same as the source program. It is evidence of one execution of that program.

![Nebu — thinking: source map and execution trace answer different questions](../assets/mascots/64x64/Nebu_thinking_64x64.png)

## 9.9. IR Does Not Have to Be Comfortable for Humans

This is an important point: Ordo Source and Semantic JSON IR have different goals.

Ordo Source should be understandable to a person.

IR should be convenient for execution.

Therefore, IR does not need to be beautiful to read. It may be longer, drier, and more formal.

That is normal.

In the future, an even more compact format may exist:

```json
[
  ["I", "summarize_text", "uk"],
  ["C", {"out": {"type": "bullets", "max": 3, "lang": "uk"}}],
  ["G", "NO_UNSUPPORTED_FACTS", "summary", "REPAIR.REMOVE_UNSUPPORTED"],
  ["H", ["status", "result", "gate_report"]]
]
```

This is hardly convenient for a person, but it may be useful for a runtime or a model specifically trained on Ordo.

The current Semantic JSON IR is an intermediate practical format. It remains readable enough while already being structured enough.

## 9.10. What Good IR Must Contain

Good Ordo IR should follow several rules.

### 1. Every Operation Must Have `op`

Bad:

```json
{
  "goal": "summarize_text"
}
```

Better:

```json
{
  "op": "INTENT.SET",
  "goal": "summarize_text"
}
```

`op` shows what must be done.

### 2. Every Important Operation Must Have `id`

```json
{
  "op": "GATE.CHECK",
  "id": "G_NO_UNSUPPORTED_FACTS",
  "method": "self_verification",
  "trust_class": "model_judgment"
}
```

Without an `id`, trace, source maps, and validation reports become difficult.

### 3. Gates Must Be Explicit

Bad:

```json
{
  "rules": ["do not invent facts"]
}
```

Better:

```json
{
  "op": "GATE.CHECK",
  "method": "self_verification",
  "trust_class": "model_judgment",
  "assert": "NO_UNSUPPORTED_FACTS",
  "on_fail": "REPAIR.REMOVE_UNSUPPORTED"
}
```

### 4. State Must Be Explicit

If the model must remember a user answer, that information belongs in state.

```json
{
  "op": "STATE.UPDATE",
  "key": "request_type",
  "value": "incident"
}
```

### 5. Handoff Must Be Described

The model must know what to return.

```json
{
  "op": "HANDOFF.EMIT",
  "include": ["status", "result", "gate_report"]
}
```

## 9.11. Typical Compilation Mistakes

### Mistake 1. Leaving an Important Gate in Ordinary Text

If a rule blocks the final result, it should compile into `GATE.CHECK`, not remain only a sentence.

### Mistake 2. Turning a Domain Explanation into a Universal Rule

For example, `HistoryEvent.item.values` is a domain contract, not an Ordo Core rule.

### Mistake 3. Losing Status Semantics

If the source contains `candidate`, `confirmed`, `blocked`, and `ready_for_first_run`, the IR must preserve the differences.

### Mistake 4. Failing to Preserve Non-Formalized Content in FREEFORM

If a fragment cannot be safely structured, it must not simply disappear.

### Mistake 5. Omitting the Source Map

Without a source map, it is difficult to prove that the IR corresponds to the source program.

### Mistake 6. Making IR Too Human-Oriented

IR is not an essay. If it contains too much free prose, the model is once again working from a prompt rather than an execution contract.

## 9.12. What This Looks Like in a Real Playbook

A simple example may contain 10–20 operations.

A real playbook may contain dozens or hundreds.

For example, an Ordo-native History Event Playbook contains operation groups such as:

```text
PROGRAM.DEF
PROFILE.USE
DOMAIN_PACK.LOAD
ENTRY.DEF
NODE.DEF
ANSWER.REGISTRY
STATE.SCHEMA
OUTPUT.DEF
TEMPLATE.BIND
GATE.DEF
APPROVAL.REQUIRE
DOC.SPLIT
DOC.CATALOG
DOC.SELECT
RENDER.VALIDATE
FREEFORM.ADD
HANDOFF.DEF
```

This does not mean the model must show every operation to the user. The user may only need to see the current node, selected documents, state changes, and the next question.

Internally, however, the process should remain controlled.

## 9.13. Short Chapter Summary

Ordo Source is for people.

Semantic JSON IR is for execution.

Compiling Ordo Source into IR makes the process more explicit:

```text
intent becomes INTENT.SET;
contract becomes CONTRACT.DEF;
context becomes CONTEXT.LOAD;
state becomes STATE.INIT / STATE.UPDATE;
steps become STEP.RUN;
gates become GATE.CHECK;
result and handoff become HANDOFF.EMIT.
```

Good IR has:

```text
explicit op values;
stable IDs;
gates;
state;
a source map;
an execution trace;
controlled FREEFORM for content that cannot be safely formalized.
```

The main idea is:

```text
compilation should not make an instruction prettier;
it should make it more executable.
```

## Mini-Exercise

Take this simple Ordo Source program:

```yaml
intent:
  goal: write_customer_reply

contract:
  output:
    type: email
    language: uk
  rules:
    - polite_tone
    - no_specific_deadline
    - acknowledge_request

context:
  customer_message: "$USER_INPUT.message"

result:
  primary: customer_reply
```

Try to transform it manually into Semantic JSON IR.

At minimum, you need these operations:

```text
INTENT.SET
CONTRACT.DEF
RULE.ADD
CONTEXT.LOAD
STATE.INIT
STEP.RUN
GATE.CHECK
HANDOFF.EMIT
```

Then consider separately: which rule should become `GATE.CHECK`, and which may remain style guidance?
