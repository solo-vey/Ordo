# Chapter 2. What Ordo Is in Simple Terms

## 2.1. Ordo is not another “prompt format”

When people first hear about Ordo, it is easy to assume that it is simply another way to format prompts: some YAML, some JSON, and names such as `intent`, `gate`, `state`, and `result`.

That is not quite right.

A prompt is an address to a model.

Ordo is a description of a process that the model must execute.

A prompt often sounds like:

```text
Create the result for me.
```

Ordo sounds different:

```text
Here is the goal.
Here is the contract.
Here is what is already known.
Here are the questions you may ask.
Here is the order in which to proceed.
Here is what is forbidden.
Here is where you must stop.
Here are the checks you must pass.
Here is the result you may deliver.
```

Ordo therefore does not merely ask a model to do something. It defines the execution boundaries.

<p><img src="../assets/mascots/64x64/Nebu_idea_64x64.png" alt="Nebu idea" width="64" /></p>

```text
A prompt is a request.
Ordo is an instructional program.
```

Or even more simply:

```text
A prompt tells the model: “do it.”
Ordo tells the model: “execute the process.”
```

## 2.2. An everyday analogy: a recipe and a kitchen

Imagine asking someone to cook borscht.

You can say:

```text
Cook borscht.
```

An experienced person may do it well. But the result depends on their memory, habits, taste, and assumptions.

You can provide a recipe:

```text
1. Prepare the ingredients.
2. Cook the stock.
3. Add the beetroot.
4. Add the cabbage.
5. Check the salt.
6. Serve with sour cream.
```

That is better. Yet even a recipe may be ambiguous. What happens if beetroot is unavailable? May an ingredient be substituted? When is the dish considered ready? Who confirms the taste?

Ordo is not merely a recipe. It is a recipe with execution rules:

```text
- if an ingredient is missing, do not invent a substitute; ask;
- do not move to serving until readiness has been checked;
- if the dish is oversalted, do not mark it finished;
- if the user requested a vegetarian version, do not use meat stock;
- at the end, show which checks were passed.
```

That is how Ordo works with an AI model.

It describes not only the desired result, but also how the model must move toward it.

## 2.3. Ordo as a route map

Another simple analogy is navigation.

A prompt may resemble:

```text
Drive to Lviv.
```

The model can choose the route itself. Sometimes that is fine. But if you must avoid toll roads, avoid a particular region, make a stop, check fuel, and not complete the route without arrival confirmation, one sentence is no longer enough.

Ordo is a route with checkpoints:

```text
start
→ choose direction
→ check constraints
→ pass checkpoint
→ if the road is closed, switch to an alternative path
→ do not finish without arrival confirmation
```

In Ordo terms:

```text
ENTRY.DEF
→ NODE.DEF
→ STATE.UPDATE
→ GATE.CHECK
→ PATH.SELECT
→ OUTPUT.DEF
→ HANDOFF
```

Ordo gives the model not only the destination, but the rules of movement.

## 2.4. The main parts of Ordo

At the simplest level, Ordo consists of several basic parts.

### Intent

`Intent` is the goal.

```yaml
intent:
  goal: create_summary
```

or:

```yaml
intent:
  goal: guide_user_through_history_event_intake
```

Intent answers:

```text
Why is this process being started?
```

### Contract

`Contract` defines the result and its rules.

```yaml
contract:
  output:
    format: bullet_list
    max_items: 3
  rules:
    - do_not_invent_facts
    - use_only_input_text
```

Contract answers:

```text
What counts as a correct result?
What is forbidden?
Which constraints must be satisfied?
```

### Context

`Context` contains input data, documents, sources, or previous decisions.

```yaml
context:
  source_text: "$USER_INPUT.text"
  playbook: "history_event_playbook_ordo_v0_10"
```

Context answers:

```text
Where does the model obtain the data it works with?
```

### State

`State` is the current process state.

```yaml
state:
  current_node: N1
  selected_path: null
  confirmed_contracts: []
  open_questions: []
```

State answers:

```text
What is already known?
Where are we now?
What remains unconfirmed?
```

### Path

`Path` is the selected execution route.

```yaml
path:
  selected: Path_1
  reason: "internal source row change"
```

Path answers:

```text
Which scenario are we following?
```

### Step

`Step` is a concrete action.

```yaml
step:
  id: S1
  do: read_input_text
```

Step answers:

```text
What is the model doing now?
```

### Gate

`Gate` is a blocking check.

A gate is not a suggestion. If its condition is not satisfied, the process must not move forward.

```text
GATE.CHECK(method=self_verification) self_validation_passed
```

Gate answers:

```text
What must be true before execution may continue?
```

### Result

`Result` is the outcome that the process is allowed to produce after its requirements are satisfied.

It may be a document, answer, package, decision, structured record, or another process artifact.

### Handoff

`Handoff` defines what is passed to a person or another process after the current process reaches the required state.

It answers:

```text
What is being transferred?
To whom or to what?
In which status?
With which open questions, warnings, or evidence?
```

These concepts are simple individually. Their value appears when they are combined into one execution structure.

## 2.5. Ordo does not require everything to become machine code

A common misunderstanding is that a formal language must describe every sentence with a rigid operator.

Ordo does not require that.

Some parts of a process should be deterministic:

```text
allowed statuses;
required fields;
blocking conditions;
path transitions;
forbidden actions.
```

Other parts should remain semantic:

```text
explain the issue clearly;
compare two variants;
ask a natural follow-up question;
write a useful summary;
propose wording.
```

The model is still a model. Ordo does not remove its ability to understand language. It gives that ability a process rail.

## 2.6. Ordo has several reading levels

The same process may be represented at several levels.

### Human level

A person reads the process as an explanation, guide, or playbook.

### Ordo Source

The author describes the process in a source form designed for editing and review.

### Semantic JSON IR

The compiler produces a machine-readable semantic representation in which entities, links, contracts, and execution rules are explicit.

### Compact IR

Where useful, the process may also have a compact representation optimized for transport or runtime use.

These levels do not compete with one another. They serve different readers and different stages of the toolchain.

![Nebu — attention](../assets/mascots/64x64/Nebu_attention_64x64.png)

## 2.7. Ordo does not replace the model

Ordo is not an attempt to reduce an AI model to a traditional script.

The model still interprets meaning, works with incomplete language, writes, compares, summarizes, and communicates with the user.

Ordo governs where that freedom is allowed and where a hard rule must take priority.

```text
The model reasons.
Ordo holds the process.
```

## 2.8. Ordo is not rigid bureaucracy

A small process should remain small.

If the task is simply:

```text
Summarize the text in three bullets without inventing facts.
```

the Ordo program does not need fifty nodes and twenty gates.

The language should add structure where structure reduces risk. It should not create ceremony for its own sake.

![Nebu — thinking](../assets/mascots/64x64/Nebu_thinking_64x64.png)

## 2.9. A small example: an ordinary task

Suppose the user wants a short summary.

A minimal process may be understood as:

```text
intent: create a short summary
context: source text
contract: three bullets, no invented facts
step: read and summarize
gate: every bullet must be supported by the source
result: bullet list
```

The important difference is that the desired behavior has been separated into roles. The goal is not mixed with the data, and the check is not hidden in a final sentence.

## 2.10. A large example: a playbook

Now imagine a playbook for creating a complex domain artifact.

The process may contain:

```text
entry;
guided intake;
answer registries;
state;
candidate paths;
path confirmation;
hard contracts;
assumption ledger;
blocking gates;
artifact generation;
QA;
handoff;
execution trace.
```

The principle is still the same as in the small example. The process is simply larger.

Ordo should scale by composition, not by turning one prompt into an ever-growing wall of text.

![Nebu — interesting](../assets/mascots/64x64/Nebu_interesting_64x64.png)

## 2.11. Ordo as a discipline of thought

Even before a compiler or runtime executes an Ordo program, writing a process in Ordo forces useful questions:

```text
What is the actual intent?
What is the contract?
What is data and what is a rule?
Which facts are confirmed?
Which assumptions remain?
Where may the process branch?
What blocks completion?
What is the final result?
```

This makes Ordo useful not only as syntax, but also as a method for designing processes.

## 2.12. Short chapter summary

Ordo is a language for describing governed processes executed with an AI model.

It is not simply a prompt format.

It separates goal, contract, context, state, route, actions, checks, result, and handoff.

It preserves the semantic strengths of the model while making the process more explicit, testable, and explainable.

## Mini-exercise

Take a task you would normally describe with one prompt.

Write one line for each item:

```text
Intent:
Contract:
Context:
State:
Path:
Step:
Gate:
Result:
Handoff:
```

If several of these concepts are mixed in the same sentence, try separating them.

## Ordo after the Process Rail reframing

The preferred operating model of Ordo is the Process Rail.

The AI remains the active semantic executor. It communicates, interprets, proposes, and reasons. The rail holds the process structure: state, route, gates, transitions, and completion conditions.

```text
AI reasons and communicates.
The Process Rail holds the process.
Semantic JSON IR preserves the machine-readable rail.
The CLI validates deterministic parts.
```

This is why Ordo is neither “just a prompt” nor “a replacement for the model.” It is the governed process layer between intent and execution.
