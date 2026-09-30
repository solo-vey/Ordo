# Your AI Finished the Ticket. Why Is the Feature Still Wrong?

There is an odd feeling that has started to appear more and more often. You open a pull request, look through the code, and everything seems fine: the logic is readable, there are tests, the method names do not immediately make you want to rename anything, and the AI agent has even left a sensible explanation of what changed and why. Then, a few minutes later, someone on the team asks a simple question: "Wait. Did we actually agree that the system should behave this way?" And suddenly it becomes clear that there is nowhere to find the answer. Not because the developer ignored something, and not because the model wrote bad code. Quite the opposite: the code often does exactly what the ticket said. The problem is that the ticket looked clear enough to implement, but not clear enough to count as a decision.

## One seemingly small ticket

Imagine a situation that I think many teams will recognize. A user starts onboarding, gets halfway through it, and closes the app. A product manager says, "It would be good if people did not have to start from scratch when they come back. We should show them the next step." It sounds simple, even pleasantly simple. AI quickly turns that into a proper ticket: a field for the last completed step, storage on the profile, an API, frontend behaviour, analytics events, and acceptance criteria. A developer takes that description, adds a little context, and by the end of the day there is a pull request with a migration, an API, tests, and a check that the user really is returned to the next incomplete step.

The code may be good. But the phrase "show them the next step" already contains a product decision that nobody explicitly made. What happens if the user comes back two weeks later and the onboarding rules have changed in the meantime? Perhaps they changed their country, a new compliance requirement appeared, or they skipped a step earlier not because they did not want to answer, but because they did not yet have the necessary information. Should the old state be restored, should a new path be suggested, or should they be asked to start again? These are not missing edge cases in the implementation. They are decisions about how the product should behave. The code did not invent them in any literal sense; it honestly implemented the most natural interpretation of the ticket. But for a product, "the most natural interpretation" and "the right decision" are not the same thing.

## Faster implementation changes where the risk appears

Before AI, an unclear ticket could also be implemented incorrectly, so there is no reason to romanticise the old process. But it had more friction. A developer spent longer understanding the data model, asked in the comments whether the state should be stored indefinitely, someone in QA might have asked what exactly should be tested after the rules changed, and the product manager had a chance to see those questions and remember that the business had never agreed on resuming an outdated flow. AI removes much of that pause. It works well precisely where people used to spend time: collecting context, proposing structure, writing code, adding tests, and explaining changes. That is genuinely useful, and I have no desire to return to the time when half a day went into mechanical work that can now be done in an hour.

But with that speed, some of the warning signals disappear. When there is a finished PR in a few hours, it is difficult to say, "No, let us not merge this yet, because we have not answered one product question." Technically, everything is ready. That is the trap: finished code looks like proof that the team is moving forward, even when it may only be proof that the team moved very quickly in one of several possible directions. Acceptance criteria can reinforce the same impression. For this ticket, AI will almost certainly produce a reasonable scenario:

```text
Given a user has completed step 3 of onboarding
When they return to the application
Then they see step 4
```

This is a good test, but it checks only what was already decided to implement. It does not answer whether the person should see step 4 at all, or whether, after a rules change, they need a different path, an update to their information, or an additional check before they can continue. A test cannot answer that question because it is not a technical one.

## The model can help, but the process needs to be able to stop

The useful question for a developer is now not only "How should this be implemented?" or "Can AI implement this?" Increasingly, there is another one: "Which decision are we quietly putting into the code right now?" That does not mean every developer should replace the product manager. But the process needs a way to reveal the points where the system would otherwise choose product behaviour on its own. Sometimes one comment in the ticket is enough: "If onboarding rules changed after an interrupted session, do we resume the old flow or create a new one?" That is not bureaucracy. It is a way of not presenting an assumption as an agreed requirement.

You can put rules like this into a prompt: "Do not make assumptions," "ask clarifying questions," or "do not begin implementation without complete requirements." They are good rules, but after several iterations they get lost between examples, additions, previous answers, and new requests to "just show a version already." That is why, for important changes, asking a model to be careful is not enough. The process needs the right to stop at a specific point:

```yaml
decision:
  question: "Can a user resume onboarding after the rules changed?"
  owner: product_manager
  status: unresolved

implementation:
  status: blocked
```

There is no magic here. This description will not answer for the product manager or make a choice instead of the team, but it will not let code look like a finished feature while an important decision does not even have an owner yet. That is exactly the kind of moment for which we are developing [Ordo](https://github.com/solo-vey/Ordo): not to let a system decide product questions for people, but to make sure an important question does not disappear somewhere between a ticket, a prompt, and a finished pull request. If the decision has not been made, the process should show that; if implementation depends on it, the process should not let it be called complete too early.

AI can close the ticket. But that does not mean the team has decided what it is building.

If the idea of making AI processes more explicit — with recorded decisions, checks, and human approval points — resonates with you, [explore Ordo on GitHub](https://github.com/solo-vey/Ordo).