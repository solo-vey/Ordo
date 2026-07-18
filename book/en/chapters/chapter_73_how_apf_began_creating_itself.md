# Chapter 73. How APF Began Creating Itself

> This chapter is a practical story from the development of `ordo.applied_project_factory`. It shows not only the finished result, but also how a complex Ordo process can gradually emerge through its own use.

## 1. Why this project could not simply be “written”

Applied Project Factory did not begin as a finished module or as an ordinary set of instructions. The initial task was simpler, but deeper: understand whether we could create a process that helps build other processes.

The conventional approach would be to sit down and immediately describe the complete workflow: which questions to ask the user, how to build a decision tree, how to create YAML, how to validate the result, and how to assemble the package. But this approach has a hidden problem. To describe such a process well, you already need a way of thinking about it. You need to know which branches will exist, where the terminal points are, and how results, templates, validation, and final package handoff will work. At the beginning, that knowledge did not yet exist.

APF therefore could not simply be written top-down as a finished specification. We gradually discovered its shape. At first, only one thing was clear: the future module must not merely generate text. It must guide a user through the creation of a new applied process so that the result can actually be executed and verified.

It had to be not a reference guide or advice, but a process that could be traversed:

```text
input → questions → decisions → branches → results → templates → validation → package handoff
```

But how do you build such a process while the process itself is still being created? This is where the main turning point appeared.

---

## 2. The main turning point: we created part of the process and started using it

The most important decision in APF's history was methodological rather than technical. We realized that we did not have to finish the entire Applied Project Factory before using it. We could create one viable part of the process and then use that part as a working tool to build the rest.

That part became the free-form branch — the future **branch 3: free dialogue**.

Its purpose was simple: the user did not have to provide a finished tree, YAML, or formal structure. They could explain the idea in natural language: what they wanted to create, which options they saw, which documents should be produced, and which decisions the process should make. In this mode, the model must not lose those ideas. It should extract from the dialogue:

```text
- possible questions;
- possible branches;
- possible results;
- hints for future templates;
- open questions;
- assumptions;
- a draft of the future tree.
```

Once this branch became clear enough, we used it not as a future part of a finished APF, but as a current working mechanism. We literally began creating APF through an APF-like mode: we discussed freely what needed to be added, the model extracted structure, we confirmed decisions, and those decisions then became part of the process itself.

It resembled the familiar image of “pulling yourself out of the water by your own hair.” At first, the whole mechanism does not exist. But one small working part does. It is not perfect, yet it is already sufficient to help build the next part. The next part then strengthens the first. Gradually, the process begins to stabilize itself.

At this point, APF stopped being merely an object of design. It became a tool for designing itself.

This matters for the whole book because it demonstrates one of the strongest properties of a well-organized process language: it can be useful before final release. You do not have to wait for total completion before gaining value. A stable fragment that can be executed, reviewed, refined, and used again may be enough.

---

## 3. How free dialogue became the process skeleton

At first, free dialogue could seem too soft for a strict process. If the user simply talks, what guarantees a structured result? Where is the boundary between an idea, an assumption, and an approved tree node?

We solved this not by forbidding free form, but by introducing intermediate states.

Free dialogue does not immediately become approved YAML. It passes through a sequence:

```text
free dialogue
→ structure extraction
→ structure draft
→ review
→ normalization
→ approved process fragment
```

This gave us a very practical working model. The user could think naturally without switching to YAML or formal tables. The model, in turn, was not allowed to silently convert what had been said into a final contract. It first showed the extracted structure, and we approved or corrected it.

Gradually, the complete logic of branch 3 emerged:

```text
the user speaks freely
→ the model extracts a possible structure
→ separates confirmed from unconfirmed information
→ shows a process draft
→ routes the result into the shared review path
```

This branch gave us a practical way to continue. It prevented us from getting stuck trying to describe the perfect process immediately. We could start with a vague vision, while each step transformed that vision into a more precise structure.

From that point on, APF grew not as one large document, but as a living process in which every new fragment was reviewed.

---

## 4. The other branches appeared around this core

Once it became clear that free dialogue could be a working entry into the process, we also saw that one entry was not enough. Real users arrive with different levels of readiness.

Some have only an idea. Some already have an approximate scheme. Some want to build a tree from scratch. Others are not creating a new process at all, but correcting an existing one. APF therefore gained four starting branches:

```text
1. Domain model + decision tree
2. Manual decision tree
3. Free dialogue
4. Correction of an existing process
```

Importantly, these were not four independent processes. We gradually arrived at an architecture where branches have different entry paths but converge into shared parts.

Branch 1 became the main path for gradually creating a process: the model helps build the domain model, questions, nodes, branches, and terminal paths.

Branch 2 became an adapter for a manual tree: if the user already has a tree in any human-readable form, APF does not force them to rewrite everything in YAML. The tree is first normalized and then reviewed.

Branch 3 remained free form, but no longer as chaotic brainstorming. It became a controlled path for extracting structure.

Branch 4 became the path for improving an existing process. This was necessary because, as soon as APF itself began to exist, we could see that the real life of a module is not only creation. It also includes correction, targeted changes, adaptation, and compatibility checks.

Together, these branches gave APF flexibility. But stability appeared only when shared logic was extracted into shared blocks.

---

## 5. A terminal point stopped being merely an ending

One of the next major steps concerned terminal points.

At an early stage, it is easy to think of a terminal point as simply the end of a tree path. The user answered the questions, we reached the final node, so the branch is complete. For APF, that was not enough.

A process that creates an applied module or working instruction cannot end with “we reached the end.” It must answer:

```text
- what is created on this terminal path?
- is it an existing result, a new artifact, no result, or a deferred decision?
- is there a template?
- is it clear which state fields are required?
- can a filled example be shown?
- has the user confirmed the binding between the result and this path?
```

This is how the shared subprocess for results and templates appeared.

We did not implement result logic separately in every starting branch. That would have been quick, but poor for long-term stability. Instead, after their branch-specific steps, all branches enter one shared mechanism:

```text
terminal point detected
→ choose result policy
→ check template state
→ review a filled example
→ user confirmation or correction
→ bind result to terminal point
→ check terminal-path readiness
```

This decision greatly improved process quality. Before it, a terminal path could be half-finished: the tree appeared complete, but nobody knew which document should come out. After it, the terminal path became a real contract: the path is not ready until its result is understood.

The distinction between “no result is needed” and “the result decision is deferred” became especially important. If no result is needed, that is an explicit decision. If the decision is deferred, it does not disappear. It becomes an incomplete item and returns during final review.

This removed one of the most dangerous forms of ambiguity: when “not decided yet” accidentally starts looking like “nothing is needed.”

---

## 6. Template review reduced late-stage findings

Another difficulty involved templates. We could agree that a document is created on a terminal path, but without a template different executors would create different documents. For APF, that was unacceptable.

We therefore established a rule: an active artifact to be created must have a template or an explicitly recorded temporary limitation. But even that was not enough. A template must not only exist; it must be seen in use.

This led to the idea of a filled example. The model does not merely show the template structure. It generates an example of the future document using test or placeholder values. The user therefore sees not an abstract scheme, but something close to a real result.

For large documents, we moved toward file-based review: it is better to give the user a file or review package than to force them to assess a large document directly in chat. This made review closer to real work with a book, documentation, or package files.

After this, findings decreased not because we reviewed less, but because errors appeared earlier. If a template is incomplete, that is visible before package handoff. If a required section has no data source, that is visible before package generation. If an artifact is unnecessary, it can be removed before final binding.

At this point, APF became much more practical. It stopped relying on the promise that “we will generate the document later” and began requiring: show the document form now, review it now, approve it now, or explicitly record that it is not yet complete.

---

## 7. Final package handoff became a separate discipline

After the starting branches and the result/template path stabilized, one more danger remained: each branch could have its own final path. That would quickly cause the rules to diverge.

We therefore extracted the final part into a shared validation and package-handoff path:

```text
approve source YAML creation
→ create source YAML
→ minimal validation
→ decide on full validation
→ review validation result
→ correction cycle
→ final review of incomplete items
→ assemble handoff package
→ final handoff
```

This final path made process completion the same for all starting branches.

The honest separation of validation states was especially important. Minimal validation means the structure is not broken at a basic level. It does not mean the module is release-ready. Full validation looks much wider: tests, coverage, state, results, artifacts, consistency, and the decision whether the module may proceed.

We explicitly established the principle:

```text
skipped full validation = limitation, not a successful pass
```

This short rule protects the process from a false green status. If validation was not run, that is neither success nor failure. It is a visible limitation.

Likewise, incomplete artifacts, deferred result decisions, open corrections, or failed validation cannot silently pass into final handoff. They are corrected, removed from active scope, or explicitly block handoff.

---

## 8. How the process matured through iterations

APF evolved not in one large leap, but through a series of iterations. At each iteration, we closed not an abstract “quality” concern, but a concrete problem that appeared while creating the process itself.

First, we stabilized the individual starting branches. Then we discovered that result and template logic should not be duplicated, so we extracted it into a shared subprocess. We did the same for validation and final package handoff. After that, we reviewed the whole tree to check whether all branches converged correctly and whether orphan nodes, dead ends, or duplicated logic remained.

The key stages looked like this:

```text
- create the basic APF logic;
- add correction mode for an existing process;
- stabilize gradual tree creation;
- formalize the manual-tree adapter;
- stabilize structure extraction from free dialogue;
- extract the result/template path into a shared block;
- extract validation and package handoff into a shared final path;
- verify the integrity of the entire tree;
- perform full validation;
- adapt the module to release-candidate state.
```

At first, findings were conceptual: the process could still be unclear, branches could duplicate logic, and terminal points could be insufficiently defined. Toward the end, findings became mostly technical: service data, reports, validation profiles, package consistency, and version references.

This is an important sign of stabilization. When the main logic is still unstable, every improvement may change the shape of the entire process. As the process matures, improvements become targeted. We were no longer redesigning APF; we were bringing it to release-candidate quality as a stable module.

---

## 9. Why almost no substantive findings remained at the end

The most interesting part of this work is not that we created many files or passed validation. It is how the nature of errors changed.

At the beginning, we repeatedly clarified the nature of the process itself:

```text
- what is a terminal point?
- when is a result considered approved?
- can a branch exist without a template?
- how does free dialogue become structure?
- what should happen to an incomplete decision?
- where does a starting branch end and a shared path begin?
```

These were architectural questions.

After introducing the shared result/template subprocess and the shared final validation path, most of these questions disappeared. The process gained clear “rails.” New branches could no longer end arbitrarily because all of them had to pass through the same checks. A result could not get lost because binding it to a terminal point required an explicit decision. A template could not remain implicit because the review package had to show it. Validation could not be decorative because final handoff inspected real blockers.

By the end, we were no longer asking “what should APF be?” We were asking “is everything in the package synchronized with the APF we have already approved?”

That is the normal transition from design to release-candidate state.

---

## 10. The main lesson for this book

The APF story matters not only as the story of one module. It demonstrates a way to create complex processes within the language package.

The most valuable thing was not the final archive or a specific set of nodes. It was the way we reached a stable result:

```text
1. do not try to write the whole process perfectly at once;
2. create one viable branch;
3. start using it to create the process itself;
4. turn free-form ideas into a structure draft;
5. approve each fragment;
6. extract repeated logic into shared subprocesses;
7. distinguish incomplete from approved;
8. do not call handoff ready without validation;
9. mature the process through targeted iterations rather than constant redesign.
```

The free-dialogue branch became more than one APF mode. It became the starting engine that allowed APF to grow. We first created a mechanism for turning an unclear conversation into structure, and then used that mechanism to structure APF itself.

It is like building a bridge where the first small section already lets you carry materials for the next one. The bridge is not finished, but it is already helping to build itself.

That is why APF emerged not as a static instruction, but as a living, executable process. It was born through its own application. And this may be the most important knowledge to preserve in the book: sometimes a complex process does not need to be fully invented in advance. It is enough to create the first working fragment, begin using it, and allow it to build the rest in a disciplined way.
