# Chapter 4. Intent, Contract, Context

![Nebu — attention](../assets/mascots/64x64/Nebu_attention_64x64.png)

## 4.1. Why these three concepts matter

At the beginning of a complex process, three different questions are often mixed together:

```text
What do we want?
What counts as a correct result?
What information are we working with?
```

In Ordo, these questions belong to three different concepts:

```text
Intent
Contract
Context
```

The distinction is important because a model behaves more consistently when the goal, rules, and data are not hidden inside one paragraph.

A useful first approximation is:

```text
Intent   = why the process exists.
Contract = what the process must guarantee.
Context  = what the process works with.
```

## 4.2. Intent: purpose or goal

`Intent` describes the purpose of the process.

A simple example:

```yaml
intent:
  goal: create_summary
```

A more specific example:

```yaml
intent:
  goal: guide_user_through_history_event_intake
```

Intent answers:

```text
Why are we running this process?
```

A good intent is usually short and stable.

It should help distinguish this process from another process.

For example:

```text
create_summary
```

is different from:

```text
validate_summary
```

and both are different from:

```text
approve_summary_for_publication
```

The output may look similar, but the purpose of the process is different.

## 4.3. Typical Intent mistakes

### Mistake 1. Making intent too broad

Bad:

```yaml
intent:
  goal: help_user
```

Almost any AI process can claim to “help the user.”

Better:

```yaml
intent:
  goal: collect_requirements_for_jira_task
```

The intent should identify the process purpose.

### Mistake 2. Putting rules inside intent

Bad:

```yaml
intent:
  goal: create_summary_without_inventing_facts_and_using_three_bullets
```

The goal and the contract have been mixed together.

Better:

```yaml
intent:
  goal: create_summary

contract:
  rules:
    - do_not_invent_facts
  output:
    max_items: 3
```

### Mistake 3. Confusing intent and output

The intent explains why the process exists.

The output describes what the process produces.

For example:

```text
Intent: clarify an incident.
Output: incident triage record.
```

These concepts are related but not identical.

## 4.4. Contract: what counts as a correct result

A contract defines the conditions that the process result must satisfy.

Example:

```yaml
contract:
  output:
    format: bullet_list
    max_items: 3
  rules:
    - use_only_input_text
    - do_not_invent_facts
```

The contract answers:

```text
What is the process required to guarantee?
What is forbidden?
Which conditions define an acceptable result?
```

A contract may define:

```text
required fields;
output structure;
allowed values;
prohibitions;
quality requirements;
confirmation requirements;
preconditions;
postconditions.
```

The important point is that a contract is not merely a description of what would be nice.

It defines what the process treats as valid.

## 4.5. A Contract does not always have to be invented from scratch

In real systems, a contract may already exist.

It may come from:

```text
a schema;
an API;
a database model;
a document template;
a domain standard;
an existing approved process;
another Ordo program.
```

In that case, the Ordo process should reference or import the existing contract rather than silently reinterpret it.

For example:

```yaml
contract:
  source: jira_task_schema_v2
```

or conceptually:

```text
CONTRACT.IMPORT jira_task_schema_v2
```

This reduces duplication and contract drift.

![Nebu — thinking](../assets/mascots/64x64/Nebu_thinking_64x64.png)

## 4.6. Contract and `confirmed`

A particularly important process distinction is the difference between a proposed contract and a confirmed contract.

A model may infer or propose:

```text
field path;
event type;
output structure;
mapping;
validation rule.
```

But a proposal is not automatically confirmed.

A process may preserve status explicitly:

```yaml
contract:
  status: proposed
```

and later:

```yaml
contract:
  status: confirmed
```

This distinction protects the process from turning a plausible model assumption into an authoritative fact.

A gate may require:

```text
contract.status == confirmed
```

before the process moves to generation.

## 4.7. A Contract may contain more than output rules

It is easy to think of a contract only as an output schema.

But contracts may govern execution too.

For example:

```yaml
contract:
  input:
    required:
      - source_text

  output:
    format: bullet_list
    max_items: 3

  rules:
    - do_not_invent_facts

  confirmations:
    required:
      - user_approval

  completion:
    require:
      - self_validation_passed
```

The contract may therefore describe the boundary between input, execution, confirmation, and completion.

## 4.8. Context: what the model works with

`Context` contains the information available to the process.

Example:

```yaml
context:
  source_text: "$USER_INPUT.text"
  playbook: "history_event_playbook_ordo_v0_10"
```

Context may include:

```text
user input;
documents;
source records;
reference data;
previous decisions;
domain packs;
selected playbooks;
external evidence.
```

Context answers:

```text
What information may the process use?
```

This is different from a contract.

A document may be context.

A rule saying “do not invent facts” is a contract rule.

## 4.9. Why context should be bounded

A common mistake in AI systems is to give the model everything that might possibly be useful.

More context is not always better.

Large uncontrolled context may contain:

```text
obsolete instructions;
conflicting versions;
irrelevant examples;
unconfirmed assumptions;
documents from another scope.
```

A governed process should know which context belongs to the current execution.

For example:

```yaml
context:
  primary_source: incident_report_17
  supporting_sources:
    - service_log_excerpt
  excluded_sources:
    - deprecated_runbook_v1
```

The purpose is not to starve the model of information. The purpose is to make information provenance visible.

![Nebu — idea](../assets/mascots/64x64/Nebu_idea_64x64.png)

## 4.10. Intent, Contract, and Context in one example

Suppose the user asks the model to summarize an incident report.

### Intent

```yaml
intent:
  goal: create_incident_summary
```

The process exists to create an incident summary.

### Contract

```yaml
contract:
  output:
    format: bullet_list
    max_items: 5
  rules:
    - do_not_invent_facts
    - preserve_severity
    - mention_unresolved_blockers
```

This defines an acceptable result.

### Context

```yaml
context:
  incident_report: "$INPUT.report"
  service_name: "$INPUT.service"
```

This defines the information available to the process.

The three concepts now have distinct roles:

```text
Intent   → purpose
Contract → validity
Context  → information
```

## 4.11. How these concepts relate to gates

Gates often validate contracts using state and context.

For example:

```text
GATE.CHECK incident_report_present
GATE.CHECK severity_preserved
GATE.CHECK unresolved_blockers_reported
```

The gate is the execution mechanism that prevents the process from continuing when a required condition is not satisfied.

Intent says why.

Contract says what must be true.

Context provides information.

State records what has happened.

Gate checks whether execution may continue.

## 4.12. A small template for starting any Ordo program

A useful starting template is:

```yaml
intent:
  goal: <process_goal>

contract:
  status: <proposed|confirmed>
  input:
    required: []
  output:
    required: []
  rules: []

context:
  sources: []
  references: []
```

This is not a complete Ordo program.

It is a disciplined starting point.

Before designing nodes and paths, you should be able to explain the process purpose, validity conditions, and working information.

## 4.13. Typical mistakes

### Mistake 1. Starting with output without intent

If you begin with a template before understanding the process goal, the process may optimize the wrong result.

### Mistake 2. Writing rules in context

Bad:

```yaml
context:
  do_not_invent_facts: true
```

This is a rule, not source information.

Put it in the contract or policy layer.

### Mistake 3. Putting a data source in the contract

Bad:

```yaml
contract:
  incident_report: report_17
```

The report is context.

The contract may require a report to be present, but the concrete report belongs to execution context.

### Mistake 4. Not recording contract status

If a model proposes a contract and the process immediately treats it as confirmed, assumptions become invisible.

Use explicit statuses where confirmation matters.

## 4.14. Short chapter summary

`Intent`, `Contract`, and `Context` answer three different questions.

```text
Intent   — why does the process exist?
Contract — what must the process guarantee?
Context  — what information does the process work with?
```

Keeping them separate makes the process easier to review, validate, and change.

Intent should be focused.

Contract should define validity and boundaries.

Context should expose the information available to execution.

## Mini-exercise

Take any AI task and write:

```text
Intent:
Contract:
Context:
```

Then inspect every sentence.

If a rule is in Context, move it to Contract.

If output structure is hidden in Intent, separate it.

If the process goal is still “help the user,” make it more specific.
