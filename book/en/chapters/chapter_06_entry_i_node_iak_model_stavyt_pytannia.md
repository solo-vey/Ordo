# Chapter 6. Entry and Node: How the Model Asks Questions

## 6.1. Why Ordo needs Entry and Node

In an ordinary conversation with a model, the user often expects the model to understand where to begin.

For example, the user writes:

```text
I want to create a new historical event.
```

The model may react in different ways. It may immediately propose an alias. It may ask for a source row. It may start building a passport. It may move to QA. It may ask ten questions at once.

For a simple conversation, this is not always critical. For a playbook, that freedom is dangerous.

If a process has a correct order, the model should not decide on its own where to begin. The starting point must be explicit.

![Nebu — idea: Entry as the process entry point](../assets/mascots/64x64/Nebu_idea_64x64.png)

Ordo uses `ENTRY.DEF` for this.

`ENTRY.DEF` answers:

```text
Where does this process begin?
```

And `NODE.DEF` answers:

```text
Which concrete step or decision node is being executed now?
```

Together, they turn a conversation with a model into a governed route.

---

## 6.2. Entry is the door into the process

You can think of `ENTRY.DEF` as a door.

When the user says, “Let's begin,” the model should not run across the entire playbook. It should enter through the defined door.

Example:

```json
{
  "op": "ENTRY.DEF",
  "id": "START_HISTORY_EVENT_INTAKE",
  "description": "Start guided intake for a new History Event",
  "first_node": "N1_INPUT_TYPE"
}
```

This means:

```text
The historical-event creation process always starts at N1_INPUT_TYPE.
```

Not with the alias.
Not with display names.
Not with QA.
Not with automation.
Not with the complete passport template.

It starts with the first question in the tree.

That is the value of `ENTRY.DEF`: it prevents the model from starting with whatever happens to look useful.

---

## 6.3. Node is one governed step

`NODE.DEF` describes one process node.

A node may be a question, a choice, a check, or an intermediate decision. In the introductory model, the easiest way to think about a node is as one question that the model asks the user.

Example:

```json
{
  "op": "NODE.DEF",
  "id": "N1_INPUT_TYPE",
  "kind": "question",
  "question": "How should the system understand that the historical event occurred?",
  "answers": ["A", "B", "C", "D", "E", "F"],
  "state_write": "entry_input_type"
}
```

Such a node clearly defines:

```text
which question to ask;
which answers are allowed;
where to write the answer;
what to do after the answer.
```

This matters because the model no longer has to invent the dialogue format while executing it.

---

## 6.4. Why you should not ask every question at once

![Nebu — attention: do not ask every question at once](../assets/mascots/64x64/Nebu_attention_64x64.png)

When a model receives a complex task, it often tries to be helpful and asks everything at once:

```text
Provide the alias, Ukrainian and English names, source row, type/sub_type,
field path, values contract, QA fixture, automation scope, and runner status.
```

This looks efficient. But it overloads the user and creates process risk.

Why?

Because some questions do not make sense until the path has been selected.

For example, until we know whether this is Path 1, Path 3, Path 4, or Path 5, we cannot correctly ask about a specific source contract. Until the source or ChangeRecord is confirmed, asking about `HistoryEvent.item.values` is unsafe. Until the contract is confirmed, it is too early to move to QA automation.

Ordo introduces the rule:

```text
one node — one primary question
```

This does not mean that the process has few questions. It means that questions arrive in the correct order.

---

## 6.5. Answer Registry: allowed answers

In a normal conversation, the user may answer in any form. That is good for natural language, but risky for a governed process.

If a node expects `A`, `B`, `C`, `D`, `E`, or `F`, and the user writes `5`, the model should not guess what the user meant. It should validate the answer.

This is what `ANSWER.REGISTRY` is for.

Example:

```json
{
  "op": "ANSWER.REGISTRY",
  "node": "N1_INPUT_TYPE",
  "allowed": [
    {
      "key": "A",
      "meaning": "internal_mongo_source_row_change"
    },
    {
      "key": "B",
      "meaning": "new_source_or_data_block_extension"
    },
    {
      "key": "C",
      "meaning": "existing_internal_changerecord"
    },
    {
      "key": "D",
      "meaning": "external_history_fact_or_change_payload"
    },
    {
      "key": "E",
      "meaning": "state_comparison_or_data_block_comparison"
    },
    {
      "key": "F",
      "meaning": "unknown_or_other"
    }
  ],
  "on_invalid": "ASK_VALID_OPTION_AGAIN"
}
```

This means that the user's answer must be validated before execution moves on.

If the answer is not in the allowed list, the model must not proceed to the next node.

---

## 6.6. State update after an answer

A node does not exist in isolation. Its result must enter state.

For example, the user answered:

```text
A
```

The model should record:

```yaml
state:
  entry_input_type: internal_mongo_source_row_change
  path_candidate: Path 1 or Path 2
```

Only then can execution move to the next node.

Without state, the model may “remember” the answer from the conversation text, but that is unreliable. In a long process, the answer may be lost or reinterpreted.

Ordo forces the model to update state explicitly.

---

## 6.7. Node as a way to prevent jumping ahead

In a correctly described Ordo process, every node has boundaries.

For example, `N1_INPUT_TYPE` is allowed only to identify the input type. It is not allowed to confirm an alias, invent `type/sub_type`, or create a QA package.

This can be described as:

```json
{
  "op": "NODE.DEF",
  "id": "N1_INPUT_TYPE",
  "allowed_actions": [
    "ASK_QUESTION",
    "VALIDATE_ANSWER",
    "STATE.UPDATE",
    "PATH.CANDIDATE.SET"
  ],
  "forbidden_actions": [
    "ALIAS.CONFIRM",
    "SOURCE_ROW.REQUEST_FULL",
    "VALUES.CONTRACT.DEFINE",
    "PACKAGE.GENERATE"
  ]
}
```

This is an important idea.

![Nebu — thinking: the boundaries of one node](../assets/mascots/64x64/Nebu_thinking_64x64.png)

A node does not only say what to do. It also says what must not be done at this step.

---

## 6.8. Example of a small tree

Imagine a simple support process.

The user writes:

```text
I have a problem with the service.
```

The Ordo process might begin like this:

```yaml
entry:
  id: START_SUPPORT_TRIAGE
  first_node: N1_REQUEST_TYPE

nodes:
  N1_REQUEST_TYPE:
    question: "What kind of request is this?"
    answers:
      incident: "incident / outage"
      change_request: "change request"
    write_to: request_type

  N2_INCIDENT_SEVERITY:
    when: request_type == incident
    question: "How critical is the problem?"
    answers:
      high: "blocks work"
      normal: "does not fully block work"
    write_to: severity

  N3_INCIDENT_EVIDENCE:
    when: request_type == incident
    question: "Do you have reproduction steps or an example?"
    answers:
      present: "yes"
      missing: "no"
    write_to: reproduction_evidence
```

This is already a decision tree. The model does not improvise the route; it executes it.

---

## 6.9. Node and user experience

It may seem that this approach makes the dialogue slower. In practice, it often makes it easier.

The user does not receive a huge questionnaire. They receive one question at a time.

The model does not burden the user with technical details too early. It guides them along the route.

This is especially important when the user does not know the system's internal terminology. An analyst does not need to know what Path 1 or Path 5 means. They can simply answer:

```text
How should the system understand that the event occurred?
```

The model maps the answer to a candidate path.

---

## 6.10. Typical Entry and Node mistakes

The first mistake is having no explicit entry.

Then the model starts differently every time.

The second mistake is mixing several decisions in one node.

For example:

```text
Select the Path, alias, source row, and QA fixture.
```

This is a bad node. It combines several different hard contracts.

The third mistake is having no allowed answers.

If answers are undefined, the model starts guessing.

The fourth mistake is failing to write the answer to state.

Then the answer exists in the chat but not in execution state.

The fifth mistake is allowing a node to do more than it should.

For example, the starting node must not be allowed to create the final package.

---

## 6.11. Short chapter summary

`ENTRY.DEF` and `NODE.DEF` prevent the model from starting a process arbitrarily or jumping between steps.

`ENTRY.DEF` defines the entry point.

`NODE.DEF` defines the concrete process node.

`ANSWER.REGISTRY` defines allowed answers.

`STATE.UPDATE` preserves the result of the answer.

The main principle is:

```text
one node — one primary decision
```

This makes the dialogue governed, verifiable, and convenient for the user.

---

## Mini-exercise

Take any complex process in which the model must ask the user questions.

Describe:

```text
1. Which ENTRY starts the process?
2. What is the first NODE?
3. What one primary question does it ask?
4. Which answers are allowed?
5. Where is the answer written in STATE?
6. Which actions are forbidden at this node?
```

If you cannot answer these questions, the process is not yet ready for stable model execution.

---

---

## 6.12. Deterministic node contracts

For strict ARF execution, every executable node has one explicit profile and one atomic responsibility. A node contract should define:

```yaml
node_contract:
  profile: execution_node
  prerequisites: []
  allowed_inputs: []
  allowed_actions: []
  forbidden_actions: []
  required_outputs: []
  validation_gates: []
  explicit_transitions: []
  invalidation_effects: []
  authorization_boundary: null
```

An action absent from `allowed_actions` is blocked in closed-world execution. A node cannot combine routing, execution, validation, and authorization responsibilities merely for convenience. Such a node must be split.

The standard profiles are:

- `routing_node` — selects an explicit transition but performs no domain work;
- `capture_node` — obtains and records bounded input;
- `execution_node` — performs the declared atomic action;
- `validator_node` — evaluates a target without changing it;
- `authorization_node` — records explicit authorization for an exact scope;
- `terminal_node` — computes a final status from mandatory evidence.

The model may discuss related topics without changing the active node. Execution leaves the current node only through an explicit transition.
