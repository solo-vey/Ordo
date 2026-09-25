---
title: Every Step Passed. Who Was Responsible for the Process?
published: true
description: The workflow completed every step, the validators approved every document, and the process still ended incorrectly. Where did control disappear?
tags: ai, architecture, testing, productivity
series: Making AI Processes More Explicit
---

In the second part, I wrote about a package that passed formal validation, looked complete, and still turned out to be a weak handoff. That problem was relatively easy to explain: our validators checked whether sections existed, but not whether the next person could actually do the work. The natural response was to add more checks, tighten the schema, strengthen the checklist, and assume that control had been restored. We did exactly that — and almost immediately ran into a worse case, where the problem was no longer the quality of the documents.

## Every Step Was Completed

Let’s use the same adapted domain with the `PREFERENCE_CHANNEL_CHANGED` event. The workflow completed every step in the correct order. Each local validator approved its document. A person confirmed the key decision, and the final package contained every required artifact. The original requirement was simple: when `profile.notificationChannel` changes from `email` to `sms`, the system should emit one event and record the old and new values in the audit log. The process had several stages: clarify the requirement, create the technical spec, prepare Jira, generate QA scenarios, obtain approval, and assemble the final handoff. At the orchestration level, everything looked completely correct:

```yaml
workflow:
  - define_requirement
  - generate_technical_spec
  - generate_jira
  - generate_qa
  - request_approval
  - assemble_handoff
```

The workflow skipped nothing and preserved the intended order. The technical spec passed its validator, Jira passed its own, and QA passed another. The approval was recorded as well. Then the user made a small correction: the event should no longer be emitted only for the transition `email -> sms`, but for any change where the new value equals `sms`. The technical spec was updated, passed validation again, and the process continued from where it had stopped. At the level of individual operations, everything still looked logical: the correction had been applied, the updated document was valid, an approval already existed, and every step had completed. We didn’t discover the mistake during validation. We found it only when the implementer started working from Jira and asked why the trigger in the ticket didn’t match the technical spec. At first, we looked for a defect in Jira, then in the validator, and only after several repeated checks did it become clear that the documents were individually valid but belonged to different versions of the decision. Untangling that mismatch took longer than making the correction itself. Jira and QA were still based on the old rule, while the approval referred to the previous version of the technical spec.

The local technical-spec validator saw only the current document:

```yaml
technical_spec_validator:
  required:
    - event_name
    - trigger_condition
    - audit_fields
  result: pass
```

The Jira validator saw that the ticket contained acceptance criteria, implementation notes, and test expectations:

```yaml
jira_validator:
  required_sections:
    - acceptance_criteria
    - implementation_notes
    - test_expectations
  result: pass
```

The QA validator had no obvious reason to reject its artifact either:

```yaml
qa_validator:
  every_case_has:
    - setup
    - action
    - verification
    - cleanup
  result: pass
```

Each of these results was locally correct. The technical spec really was valid. Jira really did contain the required sections. The QA scenarios really were self-contained. The problem wasn’t that one of the validators had “done its job badly.” The problem was that none of them answered a different question: did all of these artifacts belong to the same version of the decision?

## Where the State Disappeared

After the correction, the global picture should have looked roughly like this:

```yaml
process_state:
  canonical_requirement:
    version: 4
    trigger_condition: "new_value == sms"

  approvals:
    technical_spec:
      approved_version: 3
      status: stale

  artifacts:
    technical_spec:
      based_on_version: 4
      status: current
    jira:
      based_on_version: 3
      status: stale
    qa:
      based_on_version: 3
      status: stale

  completion_allowed: false
```

But in practice, the process stored only separate successful outcomes: technical spec valid, Jira valid, QA valid, approval present. It had no single place that recorded which version of the canonical requirement had produced each artifact, which version the approval applied to, and which dependencies had become invalid after the correction. As a result, the system combined correct local facts into an incorrect global conclusion:

```yaml
completion_check:
  technical_spec_valid: true
  jira_valid: true
  qa_valid: true
  approval_present: true
  result: complete
```

There’s no obvious false statement in this check. All four values can be true at the same time. They’re simply insufficient to justify `complete` because they ignore versions, causal dependencies, and invalidation. That distinction matters. Sometimes an AI process ends incorrectly not because of a hallucination, not because a step was skipped, and not even because the output was poor. It fails because the system can’t combine locally correct results into a correct process state.

## A Workflow Is Not the Same as Process Control

A workflow is good at answering, “What should run next?” It can enforce order, retries, timeouts, branches, and even returns to an earlier step. But a sequence of steps does not, by itself, prove that every dependent object remains current after a change. In our example, the workflow correctly ran `generate_jira`, then `generate_qa`, then `request_approval`. After the correction, it just as correctly ran `generate_technical_spec` again. If its model contains no rule saying, “A change to the canonical requirement invalidates Jira, QA, and the approval,” then it has no reason to rerun them. From the workflow’s perspective, that isn’t a failure. It’s a missing rule.

A minimal orchestration fragment might look like this:

```yaml
on_correction:
  rerun:
    - generate_technical_spec
```

But the real process needs something stronger:

```yaml
on_correction:
  invalidate:
    - technical_spec_approval
    - jira
    - qa
  rerun:
    - generate_technical_spec
    - generate_jira
    - generate_qa
    - request_approval
```

The difference between these two blocks is not the quality of the wording, and it is not the “intelligence” of the model. In the second case, the process dependencies are explicit. In the first, they’re left as assumptions. The model may infer them, or it may not. Even if it infers them correctly nine times in a row, the tenth run still does not become deterministic.

## A Validator Is Not the Same as Process Control

A validator answers, “Does this object satisfy a specific rule?” That is a strong and necessary mechanism, but its scope is usually local. It can check a schema, business constraints, completeness, consistency within a document, and even compare two artifacts. But if it is not given the current canonical version, previous approvals, and the dependency graph, it cannot determine whether a document is current in the context of the entire process.

For example, this validator checks Jira against the technical spec:

```yaml
jira_consistency:
  compare:
    - jira.acceptance_criteria
    - technical_spec.trigger_condition
  result: pass
```

It works only if it receives the current technical spec. If the orchestration layer passes cached version 3, Jira version 3 will successfully validate against technical-spec version 3 even though the canonical requirement is already at version 4. Local consistency is preserved; global correctness is not. That is why “let’s add another validator” does not always solve the problem. First, you have to define which state the validator is supposed to see and why that state is considered current.

## An Evaluator Does Not Own the Process Either

An evaluator usually scores the quality of the result: completeness, clarity, alignment with criteria, risks, and sometimes an overall score. That is useful, especially when the rules cannot be expressed fully through a strict schema. But an evaluator works with the package it is given. If the package contains mutually consistent but stale Jira and QA artifacts, the evaluator may score them very highly. It is not required to know that a correction existed and should have invalidated them.

```yaml
evaluation:
  clarity: 0.92
  completeness: 0.88
  internal_consistency: 0.95
  handoff_quality: 0.90
```

That score can be honest and still fail to answer the main question: is this the final package for the current decision? Quality evaluation does not replace provenance, version tracking, or process invariants.

## What Does “Predictable Behavior” Mean Here?

When people talk about making an AI model deterministic, they sometimes mean getting literally the same response to the same prompt. That is not the strict meaning I’m using here. For generative models, full textual determinism is often both unrealistic and not especially useful: wording may change, arguments may appear in a different order, and the same idea may be expressed in different ways. For a long-running work process, another form of predictability matters more. We do not need identical text, but we do need consistent enforcement of process invariants: after a correction, old approvals become invalid; stale artifacts never enter the final package; missing mandatory facts stop the process; every final artifact has known provenance; and completion is allowed only when all dependencies are current.

```yaml
process_invariants:
  - correction_invalidates_dependent_artifacts
  - approval_applies_to_exact_version
  - stale_artifacts_block_completion
  - mandatory_missing_data_causes_hard_stop
  - every_final_artifact_has_provenance
```

A system like this does not make the model deterministic in the mathematical sense. It makes the boundaries of acceptable behavior predictable. The model can still propose different wording, choose another document structure, or ask an additional question. But it should not be able to complete the process with a stale approval or an unnoticed artifact version.

## Who Needs to See the Whole Picture?

In practice, you need a layer that owns not one document and not one step, but the state of the process as a whole. That layer may be called a process engine, state machine, execution controller, protocol runtime, or simply an explicit control layer. The name matters less than the responsibility. It needs to see:

- canonical values and their versions;
- the provenance of every artifact;
- the dependency graph;
- the validity of approvals;
- allowed transitions;
- invalidation rules;
- hard stops;
- completion conditions.

The workflow can use this state, validators can read it, the evaluator can score the package in its context, and the model can handle individual judgment-heavy tasks. But the conclusion “the process is truly complete” should not appear as a side effect of every local component independently returning `pass`.

This does not mean every AI process needs to become a complex engine. For a short creative task, that level of control would be excessive. But when a process is long, contains branches, approvals, corrections, several dependent documents, and a requirement for repeatability, global state already exists whether or not we describe it. If we fail to make it explicit, it remains scattered across the prompt, chat history, user memory, and the model’s assumptions.

## A Practical Check

Before calling an AI process controlled, I would check a few things:

- Does every artifact record the version of the source it was created from?
- Does a correction invalidate all dependent documents and approvals?
- Can a validator determine that it is checking the current version?
- Is there an explicit distinction between `valid`, `current`, and `approved`?
- Does a stale artifact block final completion?
- Is provenance preserved after retries and backtracking?
- Is completion a separate rule rather than merely the fact that the last step finished?
- Can one layer explain why the process is in its current state?

If those questions do not have clear answers, the process may be well orchestrated, well validated, and even produce high-quality output, but that still does not mean it is controlled.

If no layer can see the full state of the process, are we controlling the behavior of the AI model — or merely hoping that its locally correct decisions happen to add up to the right result?
