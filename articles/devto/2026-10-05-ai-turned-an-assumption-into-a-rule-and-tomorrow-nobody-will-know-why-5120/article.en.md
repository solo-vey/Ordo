# AI Turned an Assumption into a Rule, and Tomorrow Nobody Will Know Why.

A pull request can be completely reasonable and still leave a problem behind. The tests pass. The incident no longer reproduces. The diff is small enough to review. An AI coding agent may even have explained the change more clearly than many humans do when they are trying to finish a hotfix before lunch. The uncomfortable part arrives later, usually when another person has to change the same area of the system and asks a question that the code cannot answer: why is this rule here at all?

I used to treat that as a documentation problem. Somebody should have written a better comment, or the PR description should have been more detailed. That is sometimes true, but AI changes the scale of the problem. A model can read an incident, a ticket, several old discussions, and a large part of the codebase, then make a useful local decision in minutes. Six months later, the code remains. The context it used may be scattered across an expired chat, an edited ticket, a customer thread, and a conversation that nobody thought was important enough to record.

## The fix was right, until somebody needed to touch it again

Imagine an internal approval flow where account managers can override a failed document check for an enterprise customer. A customer is waiting, Support escalates the case, and the original implementation blocks every override if the document has expired. The coding agent is given the incident, the relevant service, and a short note from Compliance saying that an override is acceptable for customers in one migration programme, but only if their previous verification was completed recently.

The agent makes a narrow change. It allows the override for that programme, adds a date check, records an audit event, and writes tests for the allowed and rejected paths. The PR is good. The reviewer sees that it solves the incident without opening a general bypass. The change is merged.

A few months later, another developer is asked to support a second migration programme. They find the condition, see a special case, and naturally ask whether it should be generalised. The code tells them that the first programme is allowed when verification is recent. It does not tell them whether that threshold came from a legal requirement, a temporary operational agreement, a risk decision made by Compliance, or simply the smallest change the first developer could safely make that day.

At that point, asking an AI assistant to explain the condition is tempting. It can read the code and generate a very plausible answer. But a plausible explanation written after the fact is not the same as the reason that justified the decision at the time. The model may infer a sensible policy from the implementation and still miss the customer commitment, the exception, or the person who was allowed to accept the risk.

## Code records the result, not always the reason

This is not unique to AI. Old code has always contained decisions with missing history. But when a person makes a difficult trade-off slowly, the surrounding trail often becomes visible by accident: there are comments in a ticket, a long review thread, a meeting invitation, or a colleague who remembers arguing about it. AI can compress much of that work into one clean result. That is useful, but it also means the route from evidence to implementation can disappear more completely.

The problem is not that every AI-assisted PR needs a full decision diary. Most changes do not. It matters when a change depends on a constraint that the code itself cannot prove: why one customer segment is treated differently, why a threshold is set to a particular value, why a temporary exception is allowed, or why an apparently simpler implementation was rejected. Those are exactly the details the next team needs when a new requirement arrives and the old workaround starts looking inconvenient.

For a change like the approval override, a small external record is often enough:

```yaml
change:
  purpose: "Allow a narrow approval override for programme A"
  sources:
    - incident_4812
    - compliance_note_2026_09_18
    - migration_programme_a_policy

  constraints:
    - previous_verification_must_be_recent
    - audit_event_required
    - applies_only_to_programme_a

  decision:
    owner: compliance_lead
    status: approved
    review_when: second_migration_programme_is_added
```

This does not replace code review, and it does not make a rule correct by writing it in YAML. It does something less dramatic but more useful: it gives the next person a place to start before they turn a local exception into a general policy.

## The handoff starts when the code is merged

For teams using AI heavily, I think this is becoming part of the real definition of done. The implementation is not fully handed over merely because CI is green and the ticket is closed. If the change represents a decision that another team will need to revisit, the source, constraint, owner, and review condition should survive the chat that helped create the code.

That is one of the reasons we are developing [Ordo](https://github.com/solo-vey/Ordo): to describe structured AI-assisted processes in which inputs, checks, state changes, and human approvals are explicit enough to be reviewed and carried forward. It is not an attempt to explain every token a model generated. It is a way to preserve the parts of a decision that matter when the implementation becomes somebody else’s problem.

AI can fix the bug. The team still needs to preserve why this particular fix was safe.

If you are interested in making that handoff more reliable, [explore Ordo on GitHub](https://github.com/solo-vey/Ordo).