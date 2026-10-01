# Who Will Notice That AI Has Already Changed the Promise to the Customer?

One of the most convincing things AI can produce is an updated plan. Give it a meeting transcript, a roadmap, a few Jira exports, and the current risks, and it will return a document that looks as though someone spent a careful afternoon putting the project back in order. The milestones line up. The new priorities are explained. The risks have owners. The language is calmer than the meeting was. That last part may be the most dangerous.

I have started to think that a plan which becomes clearer after an AI update deserves a little suspicion. Not because the model is necessarily wrong, but because it is very good at turning a changed assumption into a finished-looking sentence. When that sentence is spread across a roadmap, a release plan, several tickets, and a status update, the team may not notice that it has just agreed to work under a different set of commitments.

## The change was only one sentence

Imagine a normal planning meeting near the end of a sprint. The product manager says that a customer integration, originally planned for the next release, can probably move to the release after that. At the same time, Sales says the demo date cannot move. Engineering says that the new onboarding flow still depends on the integration being available for one important customer segment. Nobody makes a final decision in the meeting. People leave with different impressions of what "can probably move" means.

An AI assistant receives the notes and updates the plan. The next version is neat. It says that the integration is now scheduled for the following release, while the demo remains on track because the initial rollout will focus on the default onboarding path. There is a revised timeline, a list of dependencies, and a short risk note. To a busy reader, it looks better than the notes ever did.

The trouble is that the document quietly chose between two possibilities. Either the demo now excludes the customer segment that depends on the integration, or the integration is still needed before the demo and the schedule is not actually safe. Those are not editorial improvements to a plan. They are different commitments.

Nobody needs to be careless for this to happen. The product manager may assume the demo scope is flexible. Sales may assume the segment remains included. A developer may read the updated ticket and infer that the integration is no longer urgent. The AI simply gives all of those assumptions one coherent shape, and once that shape is in a polished plan, it gains more authority than the unfinished discussion it came from.

## Plans do not fail only because they are inaccurate

A project plan is not just a document describing dates. It is a set of promises that different people use in different ways. A developer sees the order of technical work. A product manager sees the scope that can be shown to a customer. A program manager sees which dependency must be resolved before another team can start. Leadership sees a date and assumes that the work below it is aligned.

When one underlying assumption changes, those views do not automatically change with it. The roadmap may be updated while the implementation ticket still has the old priority. The release note may describe a smaller scope while the demo team is still preparing the original one. The risk register may say "mitigated" because the AI wrote a reasonable explanation, even though the decision that would actually mitigate the risk has not been made.

This is why I do not think the answer is simply to ask AI for more detailed plans. A longer plan can hide the problem even more effectively. The question is whether the team can see what changed, who accepted the change, and which parts of the work are no longer current because of it.

A sensible human project manager often does this instinctively. They stop at a sentence such as "move the integration to the next release" and ask: does that change the demo promise? Does it invalidate the estimate? Does the affected team know? But an AI assistant has a strong incentive to keep the plan moving. Unless the process tells it where it must stop, it will often resolve ambiguity by presenting a plausible route forward.

## A plan needs state, not only prose

For this kind of work, I find it useful to make the decision visible as a small piece of process state rather than leaving it inside a paragraph of meeting notes:

```yaml
change:
  statement: "Move customer integration to the following release"
  source: planning_meeting_2026_10_01

  decision:
    question: "Does the scheduled demo still include the affected customer segment?"
    owner: product_manager
    status: unresolved

  dependent_artifacts:
    release_plan: draft
    integration_ticket: stale
    demo_scope: stale
    risk_register: stale

  completion_allowed: false
```

There is nothing sophisticated about this fragment, and it does not decide the scope for anyone. Its value is more modest: it refuses to let the updated plan look final while the changed commitment has no owner and the documents that depend on it still describe the previous reality.

This is the kind of problem for which we are developing [Ordo](https://github.com/solo-vey/Ordo). The aim is not to replace programme management with a workflow or to force every discussion into a rigid form. It is to give structured AI-assisted processes enough explicit state, sources, checks, dependencies, and human approval points that a useful model cannot quietly convert an unresolved assumption into an apparently agreed plan.

AI can make planning faster, and it should. But when a plan changes, the useful question is not only whether the new version reads well. It is whether everyone who made a commitment under the old version can tell that the ground moved beneath them.

If you are interested in making those changes visible rather than merely well-written, [explore Ordo on GitHub](https://github.com/solo-vey/Ordo).