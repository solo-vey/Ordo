# Chapter 8. Writing the First Ordo Source Program

## 8.1. Why Start with Ordo Source

So far, we have discussed Ordo as a way of thinking: there is a goal, a contract, state, nodes, answers, results, and checks. Sooner or later, this must be written in a form that a model or a future runtime can work with.

That is what Ordo Source is for.

![Nebu — idea: Ordo Source as the first program](../assets/mascots/64x64/Nebu_idea_64x64.png)

Ordo Source is a human-readable description of a model behavior program. It should be understandable to the person designing the process. It is not necessarily the best execution format for a model, but it is convenient for writing, discussion, review, and change.

An analogy with conventional programming is useful:

```text
a person writes source code
a compiler transforms it into an executable form
a machine executes the compiled form
```

The Ordo idea is similar:

```text
a person writes Ordo Source
the Ordo compiler / translator transforms it into Ordo IR
the model or runtime executes Ordo IR
```

At an early stage, we may not yet have a complete compiler. Even then, writing Ordo Source manually already structures an instruction much better than an ordinary prompt.

---

## 8.2. What the First Program Should Be Like

The first Ordo program should be very simple.

Do not begin with a large playbook containing dozens of gates and templates. Start with a task that is easy to understand:

```text
Summarize text in Ukrainian in no more than 3 bullet points.
Do not add facts that are absent from the input text.
If the text is insufficient, say so.
```

This is a good first example because it already contains the basic Ordo elements:

```text
goal;
input data;
result contract;
rules;
checks;
fallback behavior;
result.
```

An ordinary prompt might look like this:

```text
Summarize the provided text in Ukrainian in no more than 3 bullet points. Do not add facts that are absent from the input text. If the text is insufficient for a meaningful summary, say so.
```

That is perfectly acceptable for simple use. But we want to see how the same meaning looks as Ordo Source.

---

## 8.3. Minimal Ordo Source Structure

A minimal Ordo Source program may contain these parts:

```text
ordo
program
intent
contract
context
state
path
result
handoff
```

Not every program always needs every part in a fully expanded form, but a teaching example benefits from showing the complete structure.

General skeleton:

```yaml
ordo: "0.12-draft"
program: "minimal.summary.uk"

intent:
  goal: "summarize_text"

contract:
  input: {}
  output: {}
  rules: []

context: {}

state: {}

path:
  steps: []
  gates: []

result: {}

handoff: {}
```

This is not yet a program. It is only an empty skeleton. Now we will fill it in.

---

## 8.4. Describing Intent

`intent` answers the question: “What do we want to do?”

For our example:

```yaml
intent:
  goal: "summarize_text"
  language: "uk"
```

We do not write a long explanation here. We record the primary action: summarize the text.

![Nebu — attention: do not put all rules into intent](../assets/mascots/64x64/Nebu_attention_64x64.png)

Importantly, `intent` should not contain every rule. Do not put “do not invent facts,” “maximum 3 items,” and “if the text is insufficient” into the intent. Those belong to the contract and gates.

A typical mistake:

```yaml
intent:
  goal: "summarize_text_in_ukrainian_max_3_items_without_facts_and_with_fallback"
```

Avoid this. It turns intent into an uncontrolled phrase. Separate the concerns:

```yaml
intent:
  goal: "summarize_text"
```

and place the rest in `contract`.

---

## 8.5. Describing the Contract

`contract` defines what counts as a correct result.

For our example:

```yaml
contract:
  input:
    text: required

  output:
    format: "bullet_list"
    max_items: 3
    language: "uk"

  rules:
    - id: R1
      rule: "use_only_input_text"
    - id: R2
      rule: "do_not_invent_facts"
    - id: R3
      rule: "if_input_insufficient_return_insufficient_data_status"
```

Here we can already see how Ordo differs from a prompt. We do not merely ask, “please do not invent.” We create an explicit contract rule.

The contract should be as concrete as possible. If the result must be a list, say so. If it may contain at most three items, say so. If the language must be Ukrainian, say so. If the model may not add external facts, say that too.

The contract is not a recommendation. It is a validity condition for the result.

---

## 8.6. Describing Context

`context` defines where the model gets its data.

In our example, there is one source: the user's text.

```yaml
context:
  source:
    text: "$USER_INPUT.text"
```

This means: do not take text from memory, do not search for additional facts, and do not add external knowledge. The primary source is the user's input text.

In more complex programs, context may contain:

```text
documents;
tables;
a source row;
previous state;
examples;
project rules;
confirmed contracts;
environment constraints.
```

For the first program, one source is enough.

---

## 8.7. Describing State

Even a simple program may have state.

For the summary task, this is sufficient:

```yaml
state:
  status: "draft"
  assumptions: []
  unsupported_facts: []
```

Why is this useful?

`status` shows that the result is not final until the gates pass.

`assumptions` records assumptions if the model is forced to make any.

`unsupported_facts` records facts that the model cannot support from the input text.

This may look excessive for a simple summary, but the principle matters: an Ordo program should know what it has collected, what it has checked, and what it cannot confirm.

---

## 8.8. Describing the Path and Steps

`path` describes how the model reaches the result.

Our path is simple:

```yaml
path:
  id: "summarize_or_report_insufficient_input"
  steps:
    - id: S1
      do: "read_input_text"
    - id: S2
      do: "extract_supported_points"
    - id: S3
      do: "select_up_to_3_key_points"
    - id: S4
      do: "render_ukrainian_bullet_summary"
```

The important point is that we do not ask the model to immediately “write a summary.” We define the order:

```text
first read;
then extract supported points;
then select at most 3;
then render them in Ukrainian.
```

This reduces the risk that the model immediately starts generating polished but unverified prose.

---

## 8.9. Adding Gates

Now add control points:

```yaml
path:
  gates:
    - id: G1
      check: "input_text_present"
      on_fail: "return_insufficient_data"

    - id: G2
      check: "no_unsupported_facts"
      on_fail: "remove_or_mark_unsupported"

    - id: G3
      check: "max_3_items"
      on_fail: "compress_to_3_items"

    - id: G4
      check: "output_language_uk"
      on_fail: "rewrite_in_ukrainian"
```

![Nebu — thinking: a gate as a check point](../assets/mascots/64x64/Nebu_thinking_64x64.png)

A gate is a place where the model must stop and check a condition.

`G1` checks whether input text exists.

`G2` checks for invented facts.

`G3` checks that there are no more than three items.

`G4` checks the output language.

Importantly, `on_fail` does not always mean “error and terminate.” Sometimes it is a repair action. If there are five items, the model can compress them to three. If the output is not in Ukrainian, the model can rewrite it. But if there is no input text, the process must return the fallback.

---

## 8.10. Describing Result and Handoff

`result` defines what is returned:

```yaml
result:
  primary: "summary"
  fallback: "insufficient_data_message"
```

`handoff` defines what the model shows at the end:

```yaml
handoff:
  include:
    - "status"
    - "result"
    - "gate_report"
```

This means the user receives not only the summary but also the status and, where needed, a short gate report.

A simple UI may hide the gate report. For learning and complex tasks, however, it is very useful.

---

## 8.11. The Complete First Ordo Source Program

Now put everything together:

```yaml
ordo: "0.12-draft"
program: "minimal.summary.uk"

intent:
  goal: "summarize_text"
  language: "uk"

contract:
  input:
    text: required
  output:
    format: "bullet_list"
    max_items: 3
    language: "uk"
  rules:
    - id: R1
      rule: "use_only_input_text"
    - id: R2
      rule: "do_not_invent_facts"
    - id: R3
      rule: "if_input_insufficient_return_insufficient_data_status"

context:
  source:
    text: "$USER_INPUT.text"

state:
  status: "draft"
  assumptions: []
  unsupported_facts: []

path:
  id: "summarize_or_report_insufficient_input"
  steps:
    - id: S1
      do: "read_input_text"
    - id: S2
      do: "extract_supported_points"
    - id: S3
      do: "select_up_to_3_key_points"
    - id: S4
      do: "render_ukrainian_bullet_summary"

  gates:
    - id: G1
      check: "input_text_present"
      on_fail: "return_insufficient_data"
    - id: G2
      check: "no_unsupported_facts"
      on_fail: "remove_or_mark_unsupported"
    - id: G3
      check: "max_3_items"
      on_fail: "compress_to_3_items"
    - id: G4
      check: "output_language_uk"
      on_fail: "rewrite_in_ukrainian"

result:
  primary: "summary"
  fallback: "insufficient_data_message"

handoff:
  include:
    - "status"
    - "result"
    - "gate_report"
```

This is already a complete small Ordo Source program.

---

## 8.12. What Is Important to Notice

First, the program is not very long, but it already has structure.

Second, the rules are not hidden inside one sentence. They are separated into the contract and gates.

Third, the model has fallback behavior when the input text is insufficient.

Fourth, the result has constraints: format, item count, and language.

Fifth, there is a handoff that defines what is returned to the user.

All of this could also be written in an ordinary prompt, but Ordo makes the structure explicit.

---

## 8.13. How a Person Can Execute Such a Program Through a Model

If we do not yet have an Ordo runtime, we can provide this program to a model as an instruction and ask it to execute the program literally:

```text
Use the provided Ordo Source program as the execution contract.
Do not execute the task as an ordinary prompt.
Check the gates first, then return the result and gate_report.
```

This is not ideal because the model is still interpreting Ordo Source itself. Even so, behavior becomes more disciplined.

In the future, a runtime can read Ordo Source or compiled IR and control execution order itself.

---

## 8.14. Typical Mistakes When Writing the First Ordo Program

### Mistake 1. Put Everything into Intent

Bad:

```yaml
intent:
  goal: "summarize text in 3 bullets without unsupported facts and fallback if insufficient"
```

Better:

```yaml
intent:
  goal: "summarize_text"

contract:
  output:
    max_items: 3
  rules:
    - do_not_invent_facts
```

### Mistake 2. Do Not Describe Gates

Bad:

```yaml
rules:
  - do_not_invent_facts
```

but there is no gate that checks the rule.

Better:

```yaml
gates:
  - id: G_NO_UNSUPPORTED_FACTS
    check: "no_unsupported_facts"
    on_fail: "remove_or_mark_unsupported"
```

### Mistake 3. Do Not Describe a Fallback

If there is no input data, the model must not invent content. The fallback must therefore be explicit.

### Mistake 4. Mix Source and Result

`context` says where the data comes from.

`result` says what is returned.

Do not mix them.

### Mistake 5. Treat Ordo Source as the Final Machine Format

Ordo Source is a convenient human form. Compiled IR is preferable for execution. The next chapter covers this.

---

## 8.15. Short Chapter Summary

Ordo Source is the human-readable representation of an Ordo program.

It allows an author to describe a process not as one continuous prompt, but as a structured execution contract.

A first simple Ordo program should contain:

```text
intent;
contract;
context;
state;
path;
steps;
gates;
result;
handoff.
```

The main principle is:

```text
Do not write “model, please do this correctly.”
Explicitly describe what “correctly” means.
```

---

## Mini-Exercise

Try rewriting an ordinary prompt as Ordo Source.

Prompt:

```text
Write a short email to a client in Ukrainian. Explain that we received the request, will investigate the situation, and will return with an answer. The tone must be polite and must not promise a specific response time.
```

Describe:

```text
1. intent;
2. contract.output;
3. contract.rules;
4. context;
5. gates;
6. result;
7. handoff.
```

Hint: create a separate gate that checks that the email does not contain a specific response deadline.

---

<!-- REVIEWED: chapter 08; Nebu markers checked -->
