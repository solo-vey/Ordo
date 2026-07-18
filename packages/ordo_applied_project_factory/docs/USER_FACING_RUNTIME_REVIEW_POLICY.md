# User-Facing Runtime Review Policy

Status: APF v0.1.0-alpha.13 confirmed policy.

## Current node block

When reviewing a decision-tree node with a user, show the current node in this order:

```text
1. human-readable node name
2. description in the user's language
3. what the node asks/does
4. what it remembers
5. choices/branches
6. gates or outputs only when relevant
```

Technical aliases may be shown, but they are secondary.

## Free-dialogue extraction

Do not show extraction as a YAML-like alias dump by default. Use these sections:

```text
Що я почув
Що з цього випливає
Яке дерево починає вимальовуватись
Що ще неясно
```

## Process feedback loop

When the user comments on the authoring process itself:

```text
accept feedback
→ propose how the step changes
→ ask user to confirm
→ update YAML
→ reload the updated process
→ continue from the current runtime position
```

## SVG

Do not generate SVG automatically during normal review. Generate it only when the user asks.

## v0.1.0-alpha.11 — Current node review format

During node-by-node tree review, the assistant must show one current node at a time. The user-facing block must include:

1. Human description of the node in the user's language.
2. Question or action the user sees.
3. Transition options / branches.
4. What is stored in state.
5. Gates checked at this node.
6. Related artifacts, outputs, or templates.
7. Open questions, unreviewed sibling branches, and deferred return points.

Technical aliases are secondary. They may be shown only when useful or requested.

## v0.1.0-alpha.11 — Depth-first review bookkeeping

When following one branch, sibling branches are not considered approved or forgotten. Runtime must track:

- confirmed path;
- current branch;
- unreviewed sibling branches;
- deferred return points.

A tree or branch cannot be marked approved until current path and deferred return points are explicitly handled, unless the user explicitly approves skipping detailed review for a named branch.


## v0.1.0-alpha.11 — Incremental YAML patch and validation cadence

During tree review, do not fully regenerate and validate the project after every confirmed node. That is too expensive and creates noise.

Use this cadence instead:

```text
After a confirmed tree step:
1. If no YAML change is needed, keep reviewing.
2. If YAML must change, apply a small scoped YAML patch.
3. Run minimal validation only: YAML parse, CLI lint, and compile/IR refresh.
4. Continue from the updated YAML, not from memory.
```

Full validation is a separate gate. Run it when:

- a terminal branch is reached;
- the project is about to be generated or handed off;
- minimal validation or consistency review reports a finding that may affect tree integrity.

Full validation profile:

```text
lint
compile
test
coverage
validate-state
next-step
validate-factory-output
repo-check
```

If full validation fails, do not mark the project ready. Route findings back into the tree/YAML correction loop.

## v0.1.0-alpha.13 — Control-action bookkeeping

Runtime review must display and persist these as separate state buckets:

```text
unreviewed_sibling_branches
not_selected_control_actions
blocked_until_ready_actions
```

Rules:

- `unreviewed_sibling_branches` are real tree branches that must be reviewed later.
- `not_selected_control_actions` are choices the user intentionally did not take at the current control gate.
- `not_selected_control_actions` must not be silently converted into deferred return points.
- `blocked_until_ready_actions` are visible actions that are not currently allowed, such as `approve_tree` while sibling branches remain.

User-facing node blocks should show this distinction in the state section when relevant.


## v0.1.0-alpha.13 — Process-design review rendering contract

When APF is used to design or review a process tree, the assistant must not rely on conversation memory for the user-facing display format. The YAML process contract requires each current-node response to start with an explicit mode/context-shift label:

```text
- tree traversal / moving through the process tree
- tree branch selection / choosing an outgoing branch
- node-review decision / approve, correct, or defer the shown node
- execution or validation gate / running or interpreting checks
```

The current-node block must then show the node title, plain-language description, question/action, state snapshot, gates, artifacts/outputs/templates, pending sibling/deferred branches, and a mode-labeled decision prompt.
