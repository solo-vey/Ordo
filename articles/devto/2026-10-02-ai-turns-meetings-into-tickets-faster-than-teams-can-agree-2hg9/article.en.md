# AI Turns Meetings into Tickets Faster Than Teams Can Agree.

One of the easiest ways to make a project look healthy is to give every ticket an owner. After a difficult meeting, that feels almost like progress. The discussion was messy, people disagreed, and a few questions had no answer, but then AI turns the transcript into a backlog. There is a backend task, a frontend task, a migration task, a QA task, and a short note for Support. Each ticket has a description, acceptance criteria, and a person who can start working on it. The next morning, the project board looks calm again.

I have started to be wary of that kind of calm. A ticket owner is not necessarily the owner of the decision that made the ticket necessary. If those two things are confused, a team can distribute work very efficiently while leaving the central question to be answered accidentally by the first implementation that reaches production.

## The meeting ended. The work began.

Imagine a company changing how enterprise customers move from a monthly contract to an annual one. The customer success team wants account managers to offer the annual plan during a negotiation without interrupting the customer’s current service. Finance says that a contract change should normally take effect at the next billing period. Sales says that some deals will be lost if the customer has to wait. Engineering points out that supporting two active billing arrangements for the same customer is possible, but it changes what invoices, credits, and refunds mean.

Nobody is refusing the change. Everyone agrees that the customer needs a better path. But the important question is still open: when an account manager confirms the annual plan, does the new contract start immediately, at the next billing date, or only after a separate approval?

The meeting notes reach an AI assistant. It does what we asked. It creates a ticket for the API that stores the selected plan, another for the account-manager screen, another for the billing migration, and a set of scenarios for QA. The billing task says that the annual plan becomes active at the next billing cycle. It is a reasonable choice. It is also a choice that nobody in the meeting made.

A developer can now implement the migration correctly. The frontend developer can show the right confirmation screen. QA can test the path described in the ticket. The project may even be delivered without a technical defect. Then Sales discovers that a customer who signed today will not receive the promised annual price until next month, while Finance discovers that another customer was given an immediate credit nobody intended to authorise. Both outcomes can be consistent with parts of the original conversation. Neither is a bug in the code.

## Work ownership is not decision ownership

This distinction is easy to miss because tickets are so concrete. A ticket has an assignee, a status, an estimate, a due date, and often a very convincing acceptance criterion. It gives the team something useful to do. A decision is less comfortable. It may have competing options, incomplete evidence, and a person who is not ready to commit yet. AI naturally makes the first object easier to produce than the second.

The result is a familiar pattern. A product manager believes the unresolved point will be clarified during implementation. Developers assume the business has already chosen the default described in the ticket. A programme manager sees all work assigned and reports that the dependency is under control. The person who should decide is not ignoring the problem; they may simply not realise that a provisional sentence in a generated ticket has become the operating rule for three teams.

Before AI, this could happen too, but it took longer to make the ambiguity look complete. Somebody had to write the tickets one by one, and that work often exposed the missing answer. With AI, the useful parts of planning become fast enough that the absence of a decision no longer slows anything down. The team sees movement, and movement can be mistaken for agreement.

## The process should make the missing owner visible

I do not think the solution is to forbid AI from creating tickets. That would throw away one of the most useful ways to remove routine work from product and engineering teams. The useful change is smaller: do not let an unresolved decision be converted into assigned work without recording who owns it and what must wait for it.

For the contract-change example, that state can be very plain:

```yaml
decision:
  question: "When does an annual contract become active?"
  options:
    - immediately
    - next_billing_cycle
    - after_separate_approval
  owner: product_manager
  status: unresolved

dependent_work:
  billing_migration: blocked
  account_manager_ui: draft
  qa_scenarios: draft

completion_allowed: false
```

This does not make the product manager decide faster, and it does not prevent developers from exploring the technical options. What it prevents is a quieter failure: the billing migration being treated as finished because it implemented an answer that was only temporarily convenient.

That is the kind of boundary we are trying to make explicit in [Ordo](https://github.com/solo-vey/Ordo). A structured AI-assisted process can still create useful drafts, suggest alternatives, and prepare the work around a decision. But it should preserve the difference between "someone can start this ticket" and "someone approved the rule this ticket depends on."

A project board full of assigned work is reassuring. It is not proof that the team has made the decisions that work requires.

If you are interested in making that distinction visible in AI-assisted work, [explore Ordo on GitHub](https://github.com/solo-vey/Ordo).