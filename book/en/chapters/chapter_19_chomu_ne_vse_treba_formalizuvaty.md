# Chapter 19. Why Not Everything Should Be Formalized

In previous chapters, we discussed structure extensively: `Intent`, `Contract`, `Context`, `State`, `Node`, `Gate`, `Output`, `ASSERT.NOT`, and `STATUS.SEMANTICS`. This may create a natural impression: if Ordo aims for controllability, then absolutely everything in Ordo should be formalized.

But that conclusion is wrong.

Ordo does not require every sentence, example, and explanation to become a separate machine instruction. On the contrary, a good Ordo program distinguishes what must be formal from what can remain in controlled human-readable description.

This chapter explains why excessive formalization can be harmful, where the boundary between structure and explanation lies, and why Ordo needs a special mechanism for non-formalized but controlled content.

## Why This Is Needed

In traditional programming, we are used to computers executing only what is written in a formal language. If an instruction is not code, the machine does not execute it.

AI models are different. A model works well with meaning, context, examples, explanations, stylistic constraints, exceptions, and semi-structured rules. It can understand a phrase, compare examples, transfer meaning, explain a decision, and generalize a pattern.

That is exactly why it would be a mistake to make Ordo a language that tries to turn all human knowledge into a rigid set of opcodes.

If everything is formalized down to the smallest detail, three problems may appear.

The first problem is loss of meaning.

Some rules make sense only in the context of an explanation. For example:

```text
Do not create the final archive if the analyst has not yet confirmed the expected level of changes.
```

This rule can be formalized as a gate. But beside it there may be a long explanation of why it matters, which mistakes happened before, which examples are dangerous, and how the analyst usually phrases confirmation. That explanation does not always need to be split into dozens of tiny instructions.

The second problem is brittleness.

An over-formalized system starts breaking with every new case. If every exception becomes a separate opcode, the language quickly turns into a bulky catalog of special cases.

The third problem is poor readability.

Ordo must be understandable not only to a machine but also to the people who design the process. If a playbook author cannot read their own instruction without a separate compiler, the system becomes dangerous.

![Nebu — idea: formalization should preserve balance](../assets/mascots/64x64/Nebu_idea_64x64.png)

Ordo should therefore preserve a balance:

```text
formalize what controls execution;
keep what explains meaning in controlled description.
```

## Simple Explanation

Imagine traffic rules.

Some things must be formal:

```text
red light = stop;
green light = may proceed;
speed limit = do not exceed;
pedestrian on a crossing = yield.
```

But there are also explanations:

```text
a driver should account for road conditions;
in difficult conditions, extra attention is required;
poor visibility increases risk;
a child near the road may behave unpredictably.
```

These explanations matter. They affect behavior. But not all of them reduce to one simple if/then rule.

Ordo works similarly.

The parts that determine the following should be formal:

```text
- what the input is;
- what the output is;
- which questions must be asked;
- which states exist;
- which transitions are allowed;
- which gates are mandatory;
- where the model must stop;
- what is forbidden;
- what must be checked before handoff.
```

But not every domain explanation needs to become a formal command. Some knowledge may remain in a controlled textual layer.

The main requirement is not to let that textual layer become a “black hole” where critical rules are hidden.

## What Definitely Should Be Formalized

In Ordo, everything that affects process control should be formalized.

For example, if a rule determines whether the process may proceed to the next step, it should be a gate.

Bad:

```text
Before the final archive, it is advisable to make sure everything has been checked.
```

Good:

```yaml
GATE.DEF:
  id: G_FINAL_VALIDATION_REQUIRED
  before: final_archive
  require:
    - validation_report.status == passed
    - consistency_check.status == passed
  on_fail: stop
```

If a rule defines what the model is not allowed to do, it should be `ASSERT.NOT`.

Bad:

```text
Do not rush to conclusions.
```

Good:

```yaml
ASSERT.NOT:
  id: A_NO_UNCONFIRMED_CONTRACT
  forbidden:
    - treat_unconfirmed_field_as_confirmed
    - generate_final_package_before_approval
```

If a rule defines process state, it should be part of `STATUS.SEMANTICS`.

Bad:

```text
When everything is almost ready, you can move on.
```

Good:

```yaml
STATUS.SEMANTICS:
  ready_for_archive:
    meaning: "all mandatory approvals and validation gates have passed"
    allowed_next:
      - final_archive_generation
    forbidden_actions:
      - ask_foundational_intake_question_again
```

If a rule defines the expected result, it should be in `OUTPUT.DEF`.

Bad:

```text
Create a proper document package.
```

Good:

```yaml
OUTPUT.DEF:
  id: compact_history_event_package
  required_files:
    - README.md
    - SUMMARY.json
    - VALIDATION_REPORT.json
    - CONSISTENCY_CHECK_REPORT.json
```

Therefore, formalize everything that answers:

```text
is it allowed?
what comes next?
what is forbidden?
what counts as ready?
what must be checked?
what exact result must be created?
```

## What Does Not Necessarily Need to Be Formalized

Not everything that is an explanation, example, background, or supporting interpretation needs to be fully formalized.

For example:

```text
- the history of a rule;
- examples of previous mistakes;
- explanations for an analyst;
- long domain comments;
- descriptions of typical situations;
- educational examples;
- stylistic recommendations;
- explanations of why a rule exists;
- comparisons of correct and incorrect thinking.
```

These parts may be very important. But they do not always need to become separate formal instructions.

For example, a playbook may contain this explanation:

```text
For new History Events, type=companyProfile or sub_type=EDR must not be inferred from the business name of the event alone. First confirm that this is actually EDR factography and that the required field is really stored in the source row.
```

There are two different parts here.

The first is a formal prohibition:

```text
do not infer source type automatically from the event name
```

It should be expressed as `ASSERT.NOT`.

The second is an explanation of the reason and domain context. It may remain as controlled text bound to that assertion.

The correct solution is therefore neither “formalize everything” nor “leave everything as text.” It is to separate:

```text
critical rule → formal instruction;
explanation and examples → controlled freeform.
```

## Why This Is Especially Important for AI Models

An AI model does not work like a traditional code interpreter. It does not merely read an opcode and execute an exact machine operation. It performs semantic work: understands text, matches context, selects an option, and forms a response.

That is why a model needs two layers at the same time.

The first layer is formal.

It says:

```text
stop here;
ask a question here;
do not make an assumption here;
check consistency here;
do not create an archive here;
approval is required here.
```

The second layer is semantic.

It explains:

```text
why this rule exists;
what a typical case looks like;
which examples are risky;
how a person usually phrases an answer;
which domain nuances matter.
```

Without the first layer, the model becomes uncontrolled.

Without the second layer, the model loses meaning.

Ordo is not intended to destroy natural language. It is intended to place natural language inside a controlled execution context.

## Ordo Construct: Formalization Boundary

For this purpose, Ordo should have an explicit decision: every large instruction block should be classified.

For example:

```yaml
CONTENT.CLASSIFY:
  id: C_HISTORY_EVENT_SOURCE_RULE
  source: "original_playbook_section_04"
  classification:
    - formal_gate
    - formal_assert_not
    - controlled_freeform_explanation
```

Or, more briefly:

```yaml
FORMALIZATION.BOUNDARY:
  formalize:
    - transition_rules
    - approval_requirements
    - output_contracts
    - forbidden_actions
    - validation_gates
  keep_as_controlled_freeform:
    - rationale
    - examples
    - domain_background
    - historical_notes
```

This does not mean every Ordo program must contain such a large block. But the idea matters at the language level: Ordo should be able to show what was formalized and what remained in controlled description.

This leads to the next chapters on `FREEFORM` and `FREEFORM.COVERAGE`.

## Small Example

Consider a simple instruction:

```text
Prepare a short response to a customer about a delivery delay. The response should be polite, do not promise an exact date if none is known, explain that we are checking the information, and offer to notify the customer separately after the status is updated.
```

What should be formalized?

`Intent`:

```yaml
INTENT:
  goal: "prepare a short response to a customer about a delivery delay"
```

`ASSERT.NOT`:

```yaml
ASSERT.NOT:
  id: A_NO_FAKE_DELIVERY_DATE
  forbidden:
    - promise_exact_delivery_date_without_confirmed_date
```

`OUTPUT.DEF`:

```yaml
OUTPUT.DEF:
  id: customer_delay_reply
  format: "short_message"
  tone: "polite"
  must_include:
    - delay_acknowledgement
    - information_is_being_checked
    - follow_up_offer
```

What can remain as controlled description?

```text
The response should sound human and not excessively formal. Do not shift responsibility onto the customer. Avoid phrases that sound like an automated support template.
```

These rules matter too. But they do not all need to become separate opcodes. It is enough to bind them to output style guidance or controlled freeform.

## Typical Mistake 1: Formalizing Everything Until Meaning Is Lost

A bad Ordo program may look very “technical” while being almost unusable.

For example:

```yaml
STEP.001: detect_client
STEP.002: detect_delay
STEP.003: detect_emotion
STEP.004: detect_apology
STEP.005: detect_followup
STEP.006: generate_sentence_1
STEP.007: generate_sentence_2
STEP.008: generate_sentence_3
```

The process appears controlled. In reality, this instruction may be worse than a normal human description because it forces the author to prematurely detail work that the model already performs well as a language model.

Formalization should add control, not imitate control.

## Typical Mistake 2: Leaving a Critical Rule Inside an Explanation

![Nebu — attention: a critical rule must not be hidden in an explanation](../assets/mascots/64x64/Nebu_attention_64x64.png)

The opposite mistake is failing to formalize something that absolutely should be formal.

Bad:

```text
It would be good to check for contradictions before the final response.
```

If consistency checking is critical, this is not “would be good.” It is a gate.

Good:

```yaml
GATE.DEF:
  id: G_CONSISTENCY_REQUIRED
  before: final_answer
  require:
    - consistency_check.status == passed
  on_fail: stop_and_report
```

In Ordo, it is important not only to have rules but also to classify them correctly: explanation, recommendation, prohibition, gate, output requirement, or state transition.

## Typical Mistake 3: Using FREEFORM as a Dumping Ground

![Nebu — thinking: FREEFORM should explain a rule, not replace it](../assets/mascots/64x64/Nebu_thinking_64x64.png)

`FREEFORM` should not be a place where authors put everything they are too lazy to structure.

Bad:

```yaml
FREEFORM:
  text: "All important process rules are here. Read carefully and do it correctly."
```

This is not a controlled escape hatch. It is a return to a large prompt.

Good:

```yaml
ASSERT.NOT:
  id: A_NO_ARCHIVE_BEFORE_APPROVAL
  forbidden:
    - generate_archive_before_approval

FREEFORM:
  binding: A_NO_ARCHIVE_BEFORE_APPROVAL
  purpose: "domain_rationale"
  text: "This rule appeared because of a recurring defect: the final package was sometimes created before the analyst confirmed the expected level of changes."
```

Here, `FREEFORM` does not replace the rule. It explains the rule.

## Practical Rule for an Ordo Author

When writing an Ordo program, ask one simple question for every instruction fragment:

```text
What happens if the model ignores this fragment?
```

If the answer is:

```text
the process may follow the wrong path;
the wrong output may be created;
the model may proceed without approval;
a prohibition may be violated;
state may be lost;
handoff may become unsafe;
```

then the fragment should be formalized.

If the answer is:

```text
the response will be lower quality;
the explanation will be less complete;
the model will lose some stylistic or domain nuance;
```

then the fragment may remain as controlled freeform, style guidance, or domain explanation.

## Mini-Exercise

Take this instruction:

```text
Prepare a short Jira task. Do not add technical implementation details. Be sure to include a general problem description, acceptance criteria, and manual tests for the tester. If the second prioritization criterion has not yet been defined, explicitly state that it must be completed before the task is handed over for implementation. The wording should be at PM level, not developer level.
```

Divide it into three groups.

The first group is what should be formalized as `OUTPUT.DEF`:

```text
- general problem description;
- acceptance criteria;
- manual tests;
- configuration section, if needed;
```

The second group is what should be formalized as `ASSERT.NOT`:

```text
- do not add technical implementation details;
- do not hide that the second prioritization criterion is undefined;
```

The third group is what may remain as controlled freeform:

```text
- PM-level style;
- explanation of why the task should not be overly technical;
- examples of the desired tone;
```

Then try to write a short Ordo Source structure for this task.

## Short Summary

Ordo does not require absolutely everything to be formalized.

What controls execution should be formalized: transitions, gates, prohibitions, statuses, approvals, output contracts, validation rules, and handoff conditions.

Controlled description may retain explanations, examples, domain background, rule history, stylistic recommendations, and educational comments.

The main rule is simple:

```text
critical for execution — formalize;
important for understanding — bind as controlled freeform;
unimportant to the process — do not overload the language.
```

This is why Ordo needs `FREEFORM`: not as a way to hide chaos, but as a controlled mechanism for preserving meaning where rigid structure is not yet appropriate.
