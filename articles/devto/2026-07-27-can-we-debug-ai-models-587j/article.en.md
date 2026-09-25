We are not really working with AI models yet — we are playing with them like children who have been allowed to press buttons on a supercomputer. We already know a few commands. We can produce an impressive result and repeat a sequence that sometimes works. But we do not understand what happens inside, why the model chose this particular answer, or what will break after the next edit.

Until we learn, at least well enough, how a model moves through an instruction and reaches a decision, we will use only the small fraction of its capabilities that we happened to notice from the outside. We will keep pressing buttons instead of controlling the process. We will obtain isolated results instead of using the system to its full potential.

In the first three parts of this series, a long instruction became a hidden program, a correct output stopped being proof of a correct process, and local validators proved unable to guarantee global control. One final question remains: can we step through a model’s execution like a program in a debugger and see exactly where it took the wrong turn?

## We Are Still Changing AI Instructions Like a Black Box

In a conventional program, a bug may not be fixed on the first attempt, but a debugger radically narrows the search space. We set a breakpoint, run the program, inspect variable values, step through transitions, and see which condition fired. With an AI process, we often work differently: we add a rule about approval, run the process, see the same failure, repeat the rule in the correction section, get a pass — and then discover that another branch has broken. From the outside, this looks like debugging. In practice, it is black-box testing by trial and error.

The worst part is not that one change can cause a regression. The real problem is that we often do not know why the second run passed. Did the model actually start applying the new rule? Did it happen to choose another branch? Did the new wording outweigh another part of the context? Or did the old failure simply not appear in this run? When all we can see is `input → output`, a positive result explains the mechanism of improvement no better than a negative result localises the mechanism of failure.

## One Wrong Result Can Have Several Different Causes

Let us return to the running example with the `PREFERENCE_CHANNEL_CHANGED` event. After a correction, the technical specification moved to version 4, but Jira, QA, and approval remained on version 3. In the final package, the result looked the same regardless of where the failure actually occurred:

```yaml
expected:
  technical_spec_version: 4
  jira_version: 4
  qa_version: 4
  approval_version: 4

actual:
  technical_spec_version: 4
  jira_version: 3
  qa_version: 3
  approval_version: 3
```

From that output alone, we can form at least five different hypotheses:

- the model did not notice the correction;
- the correction was noticed but classified as non-material;
- the invalidation rule was not selected;
- dependent steps were not rerun;
- the completion check ignored the `stale` status.

All of them can produce almost the same final package, but they require different fixes. If the model failed to notice the correction, we need to change the change-detection mechanism. If it saw the change but classified it as insignificant, we need to refine the materiality rules. If the classification was correct but the invalidation rule was not applied, the problem lies between decision and action. If invalidation happened but the workflow reused cached artifacts, rewriting the prompt may be the wrong layer of intervention altogether. And if everything was updated correctly but the completion check ignored `stale`, then the final invariant is wrong.

Without a debugger, we see one failure and five possible places to patch. So we add a rule where it seems most logical and hope we guessed correctly.

## What Should a Debugger for an AI Process Show?

In a conventional debugger, we care about more than the final exception. We want to know which data entered a function, what values the variables held, which condition returned `true`, which branch was selected, and what state existed after the step. For an AI process, the questions are remarkably similar:

- which node was executing;
- what data the model received;
- what answer the human provided;
- what state the model believed was current;
- what change it detected;
- how it classified that change;
- which rules it considered;
- which rule it applied;
- which path it selected;
- which alternatives it rejected;
- what state existed after the decision.

That record already looks much closer to step-by-step debugging:

```yaml
debug_step:
  node: classify_correction

  input:
    old_trigger: "old_value == email and new_value == sms"
    new_trigger: "new_value == sms"

  state_before:
    technical_spec_version: 3
    jira_version: 3
    qa_version: 3
    approval_version: 3

  detected_change:
    field: trigger_condition
    detected: true

  decision:
    classification: non_material
    selected_rule: non_material_change_keeps_approval

  state_after:
    technical_spec_version: 4
    jira_status: current
    qa_status: current
    approval_status: current
```

Now we can see a specific breakpoint. The model did not miss the correction. It noticed the change in the correct field, classified it as `non_material`, and then applied a rule that kept dependent artifacts current. That is a completely different quality of diagnosis. Instead of the vague “the model updated the approval incorrectly,” we get a specific place to change: explicitly define every change to `trigger_condition` as a material correction.

## But State and Transition Still Do Not Explain Why the Model Chose That Path

Recording that the model selected `non_material` is useful, but it is not always enough to make a precise change to the instruction. We also need to see which alternatives it considered, which rule it selected, which facts it relied on, and what it ignored. That is why the `debug_record` below contains `considered_rules`, `selected_rule`, `short_reason`, and `evidence_refs`: they show not only the external transition, but also the working representation of the decision at that node.

In our example, the model may have given too much weight to the fact that the event name and schema did not change, while underweighting the change to `trigger_condition`, which expanded the population of affected events. Without this layer, we fix the symptom and risk adding an overly broad rule such as “every correction invalidates approval.” That rule would close this failure, but it would also force Jira, QA, and approval to be regenerated after a cosmetic typo correction. Debugging is valuable precisely because it lets us change the classification boundary instead of merely strengthening the prohibition.

## A Debug Log Should Not Be One Large Explanation at the End

The easiest way to obtain an explanation is to ask the model after the failure: “Why did you reuse the old approval?” It will almost certainly produce a coherent answer. But that answer may have been created after the decision. The model sees the output, sees our question, and generates a plausible story that fits the result. That is useful as a hypothesis, but weak as a debugger.

A stronger approach is to record the decision while the model is passing through the critical node and to separate execution facts from the model’s own explanation immediately:

```yaml
debug_record:
  sequence: 17
  node: classify_correction
  recorded_before_transition: true

  execution:
    state_before_ref: snapshot_16
    input_refs:
      - correction_message_12
      - technical_spec_v3
    selected_transition: update_technical_spec_only
    state_after_ref: snapshot_17

  model_report:
    classification: non_material
    considered_rules:
      - material_change_invalidates_dependents
      - non_material_change_preserves_approval
    selected_rule: non_material_change_preserves_approval
    short_reason: "Event name and output schema did not change"
    evidence_refs:
      - field:event_name
      - field:event_schema
      - field:trigger_condition
```

In this record, `execution` says what the system actually did, while `model_report` says how the model described its own decision. The first layer proves which transition was selected and what state resulted. The second helps us localise the rule or criterion that may need to change. They must not be merged, because otherwise a polished explanation can silently replace the factual execution record.

## State Diff Works Like an Inspection Window

During a long process run, a full snapshot is still necessary as a recovery point, but for a human reader the diff is usually more useful. It immediately shows what changed after the node and what should have changed but did not.

```yaml
state_diff:
  from: snapshot_16
  to: snapshot_17

  changed:
    canonical.trigger_condition:
      from: "old_value == email and new_value == sms"
      to: "new_value == sms"
    canonical.version:
      from: 3
      to: 4

  unchanged:
    - artifacts.jira.status
    - artifacts.qa.status
    - approval.status

  expected_but_missing:
    - artifacts.jira.status: stale
    - artifacts.qa.status: stale
    - approval.status: stale
```

The failure is visible here almost without explanation. The canonical value changed, but the dependent statuses did not. The `debug_record` then helps explain why invalidation did not happen.

## Knowledge Trace Shows What the Model Actually Used

In a large instruction, one rule may be described in several places. In addition, the model sees chat history, user responses, examples, templates, and previous artifacts. When it makes a decision, we need to know not only the rationale it gives, but also which sources it treated as relevant.

```yaml
knowledge_trace:
  node: classify_correction

  rules_used:
    - rule: approval_required_before_completion
      source: section.approval_rules
    - rule: non_material_changes_preserve_approval
      source: section.correction_handling

  user_evidence_used:
    - correction_message_12

  artifacts_consulted:
    - technical_spec_v3

  available_but_not_used:
    - dependency_map
    - material_change_examples
```

Now the improvement can be even more precise. Perhaps the necessary rule already existed in the instruction, but the model did not use it because the dependency map was too far from the correction section or was not explicitly bound to this node. In that case, copying the rule again may be worse than restructuring the context or binding the rule explicitly to the step.

## Accumulating Knowledge by Node

One debug trace can help fix one run. The real value appears when failures accumulate not as a random bug list, but as knowledge about specific nodes, transitions, and rules.

```yaml
node_improvement_record:
  node: classify_correction

  observed_failures:
    - run_017:
        failure: trigger_change_classified_as_non_material
    - run_024:
        failure: dependency_impact_underweighted
    - run_031:
        failure: cosmetic_example_overgeneralized

  suspected_pattern:
    "Materiality is inferred mainly from schema compatibility"

  proposed_change:
    "Add explicit semantic-impact criteria before structural compatibility"

  regression_risk:
    "May over-classify wording-only edits as material"

  required_tests:
    - trigger_condition_change
    - event_name_typo
    - description_only_change
    - schema_extension
```

This is no longer just a log. It is improvement memory for one node. When we change the instruction, we can see not only one failure, but the history of how this node failed, which fixes were already tried, which regressions they caused, and which scenarios must be rerun.

## Replay Turns Debugging into a Controlled Experiment

In a conventional debugger, after a patch we repeat the same execution path. With an AI process, that is harder because a new run may receive different wording, a different context, or reach a different decision before the problematic node. If we simply restart the entire playbook, we are not always testing the change we intended to test.

We need replay with fixed inputs and the state captured immediately before the failure:

```yaml
replay:
  source_run: run_017
  start_from:
    node: classify_correction
    state_ref: snapshot_16

  fixed_inputs:
    correction_message: correction_message_12
    technical_spec: technical_spec_v3
    dependency_map: dependency_map_v2

  changed_instruction:
    material_change_rules_version:
      from: 5
      to: 6

  expected:
    classification: material
    transition: invalidate_dependents
```

The improvement loop now begins to resemble real debugging: locate the node, inspect state and decision, change one rule, replay from the same snapshot, and only then run the regression suite.

Without replay, we change a rule and restart the entire process, but we do not know whether the new result was caused by that change.

## Does Such a Trace Show the Model’s Real Thinking?

This is the hardest question in the article — and it is where the analogy with a conventional debugger begins to break down.

In a traditional program, a variable really does hold a concrete value at a concrete moment. A condition either returned `true` or it did not. A function received certain arguments and selected a particular branch. A debugger does not ask the program to explain itself; it reads the actual state of the mechanism.

With a model, the situation is not so simple. When it writes `short_reason`, `considered_rules`, or `factors_used`, we are not necessarily revealing a hidden variable that existed inside all along. We are obtaining a structured reconstruction of how its behaviour can be described in the language of our playbook. That reconstruction may be useful, accurate, and sufficient to localise a problem. But it does not become a fact merely because the model wrote it into a debug log.

That is why `debug_record` must separate two layers rigidly:

- `execution` — what the system actually received, did, and changed;
- `model_report` — how the model described the cause of its decision.

The first layer can serve as the foundation of control. The second must be treated as a hypothesis.

Suppose the model claims that its decision depended on `correction_material: false`. We change only that factor and rerun the node:

```yaml
causal_probe:
  baseline:
    correction_material: false
    selected_action: reuse_approval

  intervention:
    correction_material: true

  expected:
    selected_action: invalidate_approval

  observed:
    selected_action: reuse_approval
```

If the action does not change, the claimed factor was not a sufficient cause. The behaviour may have been determined by another part of the context, cached state, or a combination of signals that does not fit a discrete scheme such as “the model chose rule A instead of rule B.”

That distinction matters. Sometimes the problem is not that the real decision is hidden from us. The problem may be that no clear decision existed in the form assumed by a traditional debugger. In that case, `model_report` is not an exposed internal mechanism. It is our best behavioural model.

A good AI debugger should therefore not promise full internal transparency. Its job is more modest and more practical: turn the model’s explanation into a testable hypothesis, and prevent that hypothesis from replacing the facts of execution.

## What Do We Actually Get?

Such a debugger does not turn us into “the adult who finally understands the supercomputer.” It does not guarantee full access to the model’s internal mechanism, and it does not prove that each decision existed as a clean sequence of rules, alternatives, and causes.

It gives us something else — and for engineering, that is more important: an instrument panel around a system that may remain partly opaque.

We can reliably record:

- which inputs arrived;
- which node executed;
- what state existed before and after the step;
- which transition was selected;
- which artifacts changed;
- which gates passed;
- which path can be reproduced through replay.

Separately, we can ask the model to describe the rules, factors, and alternatives it supposedly relied on. But that description is not the foundation of control. It is a diagnostic hypothesis that must be compared with the execution record, state diff, and causal probes.

The real transition from play to engineering does not happen when the black box finally explains itself completely. It happens when the process remains controllable even when the model’s explanation is incomplete, simplified, or wrong.

At that point, improving a long instruction stops being an endless cycle of “rewrite the prompt and see what happens.” It becomes a process of accumulating evidence: this node fails under this combination of inputs; here is the rule it selected; here is the factor that, according to its own report, influenced the decision; here is the causal probe; here is the patch; here is the replay; here is the regression suite; here is the new improvement record.

## The Boundary of the First Series

At the beginning of this series, we had a large prompt that behaved like a hidden program. Then we learned to distinguish a polished output from a correct process. Next, we made global state explicit and saw that local `pass` results do not guarantee correct completion. The final step is to make the execution path visible enough that the process can be debugged and deliberately improved, not merely tested.

If, after every failure, all we can see is the prompt at the beginning and the document at the end, are we really debugging an AI model — or merely asking the black box for another attempt?
