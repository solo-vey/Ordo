When we first decided to bring AI into analysts’ work, the task seemed fairly down-to-earth. The company has several development teams and roughly fifteen analysts. They collect requirements, prepare tasks, describe changes in Confluence, think through testing, and help align future implementation with both business and development. A lot of this work is repetitive, so giving analysts a tool that could prepare first drafts felt like an obvious idea.

The problem is that a document in this kind of process almost never stands on its own. The same change exists in Jira, in Confluence, in mockups, in test scenarios, and in technical notes. Sometimes there are also separate instructions for making changes in the codebase. Each artifact has its own purpose, but all of them describe the same future system behavior. If the wording drifts apart, that can go unnoticed for several days, until different people begin working from different versions.

A typical case looked roughly like this (the details and names are changed, but the mechanism is real). Jira said that a `status` field could have three values: `draft`, `active`, and `archived`. Confluence still contained an older table with only two values, while the test scenario also checked for `disabled`, which had been discussed early on and later rejected. The developer implemented what was written in Jira. The tester opened the scenario and filed a defect because `disabled` was missing. Only after that did the analyst compare the documents and realize that each of them preserved a different version of the decision.

Nothing catastrophic happened. We simply had to go through the documentation again, update the tests, clarify the task, explain to the developer that the code did not need to change, and send the package through review one more time. It’s exactly these “nothing serious” moments that add up to delays, when the same task travels two or three times between an analyst, a developer, and a tester. At some point, it becomes difficult even to say where the original mistake was, because everyone is already working on the consequences.

So our original goal was practical: help analysts assemble a consistent package of materials more quickly and reduce the number of such returns. We didn’t begin with a theory about formal languages or AI process architecture. We simply wrote prompts and tried to make them good enough for real work.

This is the first article in a four-part series. The second will look at situations where the final result appears correct even though the process was carried out incorrectly. In the third, I want to examine what workflows, validators, and evaluators actually control, and where a gap remains between them. The last part will review existing approaches. Here, I will focus on how a simple instruction gradually turns into something much more complicated.

## At First, the Model Only Helped with Drafts

The first scenarios were small. The model asked clarifying questions, helped structure the information, prepared a Jira draft, suggested text for Confluence, and produced several test scenarios. The analyst reviewed the result, added what was missing, and asked the model to correct inaccuracies.

AI still works well in that format. A short conversation, one or two documents, and a quick human review are enough for many tasks. Building a separate mechanism around every such interaction would simply create unnecessary work.

Technically, these were ordinary chats with sets of files that we passed to the model together with the instructions. Later, we moved such processes into a controlled environment without direct access to production Jira or Confluence.

The complexity grew gradually. Even a relatively small change could involve forty or fifty analytical steps. First we collected the input information, then clarified data structures and parameters, prepared several related drafts, sent them for review, collected comments, made corrections, and checked the documents against one another again. At the end, we had to add real links to the pages and tasks that had been created. Technical operations were happening in parallel: values were copied between files, required fields were checked, dependent artifacts were updated, and validation was run again.

In the end, the model had to follow a long route and prepare around seven artifacts. Each individual result could look acceptable, but that was not enough. We also had to make sure that names, parameters, rules, and constraints did not drift apart across documents after several rounds of edits.

We still called it a prompt because, technically, we were running one large textual instruction. At the same time, it already contained a sequence of actions, dependencies between steps, transition conditions, returns to previous stages, repeated checks, and rules for handling errors. I didn’t see the significance right away. For quite a while, I thought it was simply a very large prompt that needed better organization.

## Maintenance Turned Out to Be Harder Than the First Version

It’s almost impossible to write a process like this correctly on the first attempt. Even when the business logic is well understood, there is still the question of how the model will interpret each phrase in a particular context.

We ran the instruction and looked for where it failed. If the model skipped a check, we added a clarification. If it filled a field incorrectly, we added an example. When two documents started contradicting one another, another validation step appeared in the process. The next run exposed a new problem, and the instruction grew by several more paragraphs.

Every change had a specific reason, so for a long time it didn’t feel as though we were doing anything dangerous. The text was simply becoming more detailed. After dozens of iterations, however, it contained both the description of the work and traces of all the failures we had encountered before. In one of the larger experiments, the total instruction set grew to almost one megabyte. It was spread across several files and included many sections, examples, and checks that had accumulated over a long period.

That was when local changes stopped staying local. A rule added for one document could alter behavior in another. A new check could affect how the model interpreted a step that appeared much earlier. After fixing one problem, a new one sometimes appeared in a place that had previously been stable.

Splitting the instructions into files helped people: the material became easier to read and edit. The model, however, did not treat those files as real boundaries. It saw one large shared context, found connections between fragments, and drew conclusions that we hadn’t intended.

What made this especially unpleasant was that the model’s explanations often sounded convincing. It could find another rule, connect it to the current step, and explain why it had chosen a particular behavior. The reasoning was not random. It really did follow from the way the model had read the full text. But for our process, that connection was wrong, and it became harder and harder to notice such interactions in advance.

At some point, we couldn’t confidently predict the consequences of every new clarification. The instruction still worked, but maintaining it began to feel like editing a large system without a dependency map.

And, to be honest, I kept trying for quite a while to solve the problem with the same method that had created it: adding a few more carefully written paragraphs.

## We Tried to Explain Everything More Clearly

The most obvious response to incorrect model behavior is to describe the requirement in more detail. Early on, that works: an unclear phrase can be rewritten, a weak example can be replaced, and a missing exception can be added to the rules.

The difficulty begins when a new paragraph has to coexist with dozens of older ones. The author sees it as a local correction. The model receives one more piece of context that can be connected to every other part. This increases both the size of the text and the number of possible ways its parts can be interpreted together.

We regrouped rules, moved examples closer to the steps they belonged to, separated checks, and removed repetition. Some of those changes had a noticeable effect. The main difficulty remained: editing one fragment of a large instruction didn’t guarantee a change in only one part of the model’s behavior.

For a long time, I thought we simply needed a better way to write prompts. Eventually, I saw a different picture. The task already had state, transitions, conditions, dependencies between artifacts, and recovery after errors. We were trying to maintain all of that as ordinary prose, even though in terms of complexity it already resembled a small program.

## The Way the Model Worked with Code Changed How I Saw the Problem

By that point, I had been using language models in software development for more than two and a half years. They made plenty of mistakes there too, but the environment was very different.

When a model changes a function in a large project, it sees the signature, types, call sites, surrounding code, tests, and the rules of the language itself. Changing an interface affects concrete implementations and usage points. Type violations can be caught during compilation or static analysis. Even a poor change is attached to a specific structure, so its consequences are easier to find and inspect.

A large textual instruction offers far fewer such anchors. The same requirement can be expressed in dozens of ways, and each phrasing leaves room for interpretation. In a short conversation, that’s usually fine: a person quickly clarifies the intent. In a long process, the decision made at one step becomes context for the next, so a small ambiguity can pass through several stages and surface in a different document.

There is a temptation to draw too broad a conclusion from this, and I’d rather avoid that. Code is not a universally better way to describe every kind of work. Natural language lets us discuss unclear tasks, change direction, explore options, and avoid defining the whole structure in advance. For analytical work, that is one of its main advantages. In our case, the problem appeared where the model was expected to follow a repeatable procedure with a large number of mandatory conditions.

## What Happens as Models Become More Capable?

Modern models are increasingly good at solving underspecified tasks, and for analysis or exploration that is a major advantage. A repeatable process is different: the model may see a “better” route where the team needs the agreed one. I’ve already caught myself describing two separate modes of work — “think for yourself” and “follow this literally.” I don’t know yet whether new control mechanisms will reduce that tension.

## Where I Draw the Boundary Now

I don’t tie the boundary to a specific number of steps. Ten steps can be harder than one hundred if they contain many branches, returns, and dependencies. A long linear process can be easier to control than a short one in which every decision changes several later actions.

I now test such instructions with a few simple questions:

- Does the process need to preserve state between stages?
- Do earlier decisions affect later ones?
- Are there branches, error recovery paths, or several possible final outcomes?
- Do several documents need to change together?
- Does a correction make earlier approvals or artifacts obsolete?
- Will someone later need to retrace how the result was produced?
- Would one skipped step force another person to reconstruct a missing part of the process?

If most answers are yes, I no longer treat the text as an ordinary prompt. It is a process specification, even when it lives in a Markdown file. That doesn’t mean it must be rewritten in a formal language: sometimes it is enough to move part of the control into code, a workflow, validators, or human review. But testing it with only one successful run is certainly not enough. The minimum we now check is a normal scenario, a branch-heavy scenario, invalid input, recovery after correction, and a hard stop when mandatory facts are missing.

For now, the practical observation I want to preserve is simple: a large text containing transitions, state, exceptions, and dependencies between artifacts becomes difficult to maintain in the same way as an ordinary instruction.

Have you had a moment when a prompt stopped feeling like plain text? What caused it: the number of steps, branching, the number of documents, the cost of an error, or something else? And did you manage to keep such a process under control without additional formalization?

In the next part, I will move to another aspect of the same problem: a final document can look correct and pass formal validation even though the model didn’t follow the process that was expected of it. Later in the series, I will show which control mechanisms we tried, where they helped, and where they merely moved the problem to another layer.