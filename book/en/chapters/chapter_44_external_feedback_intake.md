# Chapter 44. Receiving External Feedback After Review

After an Ordo package is handed over for external review, the most dangerous mistake is to start fixing everything immediately.

In the Process Rail, that is the wrong route. Feedback must first become a structured fact and only then a decision.

```text
review finding → feedback item → triage → decision → milestone
```

## Why you should not fix things immediately

An external reviewer may find a real blocker, a useful improvement, a documentation misunderstanding, or an idea outside the current release scope.

If all of this is mixed into the code immediately, the release candidate stops being stable. M49 therefore adds not new runtime logic, but a feedback-intake layer.

## Feedback item

Every comment must be recorded as a separate item:

```text
id
area
severity
evidence
recommended_action
decision
target_milestone
status
```

This separates the fact from the decision.

## Decisions

Feedback uses simple statuses:

```text
accepted
accepted_with_scope_limit
needs_more_evidence
deferred
rejected
not_applicable
```

For example, if a reviewer says the CLI crashes in CI, that may be a `blocker` and `accepted`. If the reviewer proposes rewriting the entire language, that may be `deferred` or `accepted_with_scope_limit`.

## Role of AI Ordo Developer

AI Ordo Developer must not immediately modify the package. It must first:

1. split feedback into separate findings;
2. classify each finding;
3. record evidence;
4. propose a decision;
5. name a target milestone only for accepted items.

This continues Ordo's central idea: the model may reason flexibly, but the process must remain controlled.
