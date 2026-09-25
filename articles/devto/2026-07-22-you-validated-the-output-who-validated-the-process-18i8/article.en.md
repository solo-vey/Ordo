In the first part, I wrote about the point where a long instruction stops being just a prompt and starts behaving like an undocumented program. It develops state, transitions, recovery paths, dependencies between documents, and rules that are already difficult to change locally. But even if you accept that, an uncomfortable question remains: how do you know the model actually followed the process you needed? The easiest thing is to look at the result. There’s a Jira ticket, a technical description, acceptance criteria, and several test scenarios. The format is correct, the required sections are present, and the names match. During a quick review, the package looks complete — and that’s exactly where we went wrong more than once. A result that looks correct doesn’t prove that the model used the right sources, performed every required check, and avoided skipping a mandatory step. It also doesn’t prove that the next person won’t have to reconstruct part of the work on their own. The clearest way to see this is through a concrete handoff.

## The Package Looked Ready

The example below is adapted from a controlled run. I changed the domain, names, fields, and values completely, but kept the failure mechanism intact. Imagine a team adding an internal event called `PREFERENCE_CHANNEL_CHANGED`, which should be created when `profile.notificationChannel` changes from `email` to `sms`. At the data level, the requirement might look roughly like this:

```yaml
event:
  name: PREFERENCE_CHANNEL_CHANGED
  trigger:
    field: profile.notificationChannel
    from: email
    to: sms
  expected:
    emit_once: true
    persist_audit_record: true
```

The model follows a long process and produces a Jira ticket, a technical description, acceptance criteria, manual QA scenarios, a short rollback, and a requirement to update tests and documentation. At first glance, everything looks fine: there’s a positive scenario, a negative case, a duplicate check, and a description of the expected event. The names are consistent, the document structure is correct, and the process ends successfully. We’d accepted the package with almost no comments at first. Only when the tester started reading it as a working instruction rather than a neatly assembled document did they stop at the second scenario and ask, “What data am I supposed to prepare here, and what do I clean up afterwards?” The package didn’t answer that, and figuring out what the model had meant took longer than reading the document itself.

The first gap appeared in Jira. The requirement looked perfectly normal at first, but it was already missing the level of detail needed for implementation. It said something like this:

```yaml
technical_requirements:
  - update unit tests
  - update documentation
```

Formally, the requirement exists, but in practice it doesn’t answer several basic questions: which component needs coverage, which tests are mandatory, which fixtures should be used, where the audit record is stored, and which documentation page should be updated. QA had the same problem. The first scenario was detailed:

```json
{
  "case": "channel changes from email to sms",
  "setup": [
    "create user with notificationChannel=email",
    "clear previous audit events"
  ],
  "action": "update notificationChannel to sms",
  "verify": [
    "event PREFERENCE_CHANNEL_CHANGED exists",
    "event was emitted once",
    "audit record contains old and new values"
  ],
  "cleanup": [
    "restore notificationChannel=email",
    "remove generated audit event"
  ]
}
```

The second scenario already started with “repeat the previous steps, but change the value,” and the third referred back to the first two. The tester had to decide which data was inherited, what needed to be cleaned up between runs, and whether the duplicate check should use the same profile or a new one. There was a rollback too, but only one generic instruction: “return the notification channel to its previous value.” That wasn’t enough for real testing. If a scenario creates an event, changes a profile, and leaves an audit record behind, the rollback needs to explain what to do with each of those effects. Otherwise, the next run already starts from a different state than the one described in setup. The package didn’t look obviously wrong: it covered the right topics, contained every expected section, and even read convincingly. The problem only became visible when someone tried to use it as a handoff. That was when it became clear that the document was simply pushing part of the work onto the next person.

## A Valid Format Isn’t the Same as a Ready Handoff

In many AI processes, result checking starts with schema validation. That’s useful: a schema can confirm that required fields exist, value types are correct, the document has the expected structure, and the JSON or YAML can be parsed programmatically. For example, this check really will catch an empty `rollback` and prevent a required field from being omitted:

```json
{
  "required": ["title", "test_cases", "rollback"],
  "properties": {
    "rollback": {
      "type": "string",
      "minLength": 1
    }
  }
}
```

But it doesn’t know whether that rollback is sufficient for an independent tester. The string `"restore previous value"` will pass the check just as easily as a complete instruction that cleans up the profile, events, and audit records. The same is true for `test_cases`: an array with five elements is formally better than an empty array, but the number of elements says nothing about whether those tests are self-contained. A Jira ticket can also contain acceptance criteria while still failing to define all the technical deliverables. We wrote our first validators at exactly this superficial level: does the section exist, is the field filled in, is there a list of tests? The package passed them honestly because all the required elements were formally present. The problem was in our criteria, not just the model’s behavior. After that, we had to split what we had previously treated as one question into three separate ones:

1. Does the result have the correct form?
2. Does it contain enough information for the next person?
3. Was it produced through the right process?

The answers don’t always match. A document can be formally correct and still be a weak handoff. A handoff can be sufficient even if the model skipped some of its internal checks. The model can follow every step and still produce a badly written document. When all of that is collapsed into one score or one final gate, some classes of failure simply disappear from view.

## What Does “the Right Process” Actually Mean?

It’s easy to go too far in the other direction and demand that the model repeat every internal step word for word, but for most tasks that would be unnecessary. I’m not interested in exposing the model’s hidden chain of thought or controlling every internal operation. A practical process is what can be recorded externally: which sources were used, which mandatory checks were completed, which decisions a person approved, what happened after a correction, and why the process ended in that particular final state. If a document changes after approval, the old approval should no longer count as valid. If the model goes back to an earlier step and changes a canonical value, dependent documents should be regenerated or explicitly rechecked. If mandatory data is missing, the process should stop rather than fill the gap with a plausible assumption. You can think of this as a very simple process state. There’s nothing complicated here: a few versions, statuses for dependent artifacts, and an explicit answer to whether completion is allowed:

```yaml
state:
  canonical_value: sms
  approved_version: 3
  current_version: 4
  dependent_artifacts:
    jira: stale
    qa: stale
    technical_spec: current
  completion_allowed: false
```

This fragment doesn’t explain how the model “thought.” It only records what matters for execution: the current version, the status of dependent documents, and whether the process may finish. An ordinary prompt often doesn’t make those things explicit. They exist somewhere in the text, the chat history, and previous responses, but not necessarily as controlled state.

## One Successful Run Proves Almost Nothing

Another trap is testing a long process only on the happy path. The model receives complete input, the user answers every question, the documents are approved on the first attempt, and the package is created successfully. After a run like that, it’s easy to conclude that the instruction works. In the first part, I already named a minimum set of five scenarios, and each one catches a different class of problem. A normal successful run checks the base route. A branch-heavy scenario shows whether the model gets lost when alternatives and returns appear. An invalid-or-irrelevant-input scenario tests whether it can refuse to build a plausible but incorrect package. A correction scenario shows whether earlier documents and approvals are invalidated. A hard stop checks the most uncomfortable case: whether the model invents a mandatory fact simply because the process “has to” finish. In our case, the happy path produced a polished package, while the scenario in which an independent person had to use the document showed something else: part of the process still had to be reconstructed manually. That’s the difference between “generation completed” and “the process is usable.”

## Why the Model Could Finish the Package Successfully

In the example above, the model didn’t ignore the task. It produced every expected artifact and touched on the main topics. If the check had asked only whether there was a Jira ticket, QA, rollback, a mention of unit tests, and a full set of documents, the package would have passed without trouble. In fact, it did pass our first validators. But the criterion `rollback exists` is much weaker than a real check of rollback quality. For this case, a stronger criterion might look roughly like this:

```yaml
rollback_quality:
  applies_to_each_mutating_case: true
  restores_initial_state: true
  removes_generated_events: true
  clears_audit_records: true
  executable_by_independent_tester: true
```

The same applies to QA: having scenarios doesn’t guarantee that each one contains setup, action, verification, and cleanup. The model optimizes for what you describe. If the criterion is defined at the level of section presence, the model can satisfy it at exactly that level. This isn’t unique to AI: a person can also write a formally complete but practically weak document. The difference is scale. A model can generate a large package very quickly, and it can scale incompleteness just as quickly.

## What You Can Check Right Now

Before accepting an AI-generated package, I’d suggest asking at least a few questions. They don’t replace a full review, but they quickly reveal whether the same gaps we saw in the handoff are hiding behind a correct structure:

- Can the next person do the work without an extra explanation from the author?
- Is every test case self-contained?
- Are specific technical deliverables defined, rather than just general wishes?
- Does every state-changing action have its own rollback or cleanup?
- Is it clear which sources support the key values?
- Do earlier approvals become invalid after the document changes?
- Are dependent artifacts updated after a correction?
- Can the process still end successfully when a mandatory fact is missing?
- Are you checking not only the format, but whether the handoff is actually usable?

This checklist doesn’t require a new platform or language. It can be added to code review, QA review, or a normal document review. Sometimes that’s already enough to reveal the difference between a document that looks good and one people can actually work from.

## Where Should the Control Live?

After cases like this, the natural response is to add more validators. One checks the Jira structure, another checks QA completeness, and a third checks consistency across documents. The workflow controls the order of steps, while a person approves critical decisions. That works to a point, and for a while it can feel as though the problem is solved. Then another question appears: who is responsible for the process as a whole? A workflow knows which step comes next, a validator checks a specific document, an evaluator scores the result, and a person can stop the process. But none of those layers necessarily sees the whole picture on its own: state, sources, approvals, correction paths, final process states, and dependencies between artifacts.

What if the workflow completed every step, the validators approved every document, and the result was still wrong — who was actually in control of the process?
