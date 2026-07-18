# APF DELTA BACKLOG REGISTER

Baseline: `v0.1.0-rc.13-ordo-v0.12-adaptation-confirmed-closure`  
Release candidate enhancement line: `playbook-authored-mini-prompt-support`  
Scope: APF package/process only

## BL-APF-001 — Real-case replay and analyst-experience validation for playbook improvements

Status: `deferred`  
Implementation started: `false`

Purpose: validate proposed playbook improvements against minimized real analyst interaction evidence, pre-change/post-change state and analyst-facing rendering.

Current capability boundary:

- state, checkpoints, snapshots, session trace and state diff are available at mixed runtime/helper levels;
- generalized real-model replay is not production-ready;
- multi-runtime transcript replay remains blocked;
- no deterministic replay claim is allowed.

Activation requires a separate process-owner decision. This item is not part of the current mini-prompt implementation line.

---

## BL-APF-002A — Playbook-authored mini-prompt support

Status: `completed-in-rc14-release-candidate`  
Implementation started: `true`  
Current milestone: `PMP-8 completed`  
Implementation order: `first`

### Goal

Enable APF, while creating a downstream playbook, to:

1. evaluate whether a normal structured instruction is sufficient;
2. improve the deterministic object contract before considering a prompt;
3. reuse an existing approved prompt when appropriate;
4. create a structured new mini-prompt candidate only when justified;
5. submit that candidate to a human reviewer;
6. activate it only after explicit approval;
7. generate a downstream-playbook Prompt Registry, manifest and attachment map;
8. validate prompt authority, identity, checksums and test scenarios;
9. include prompt assets conditionally in the generated playbook package.

### Boundaries

- applies to playbooks authored by APF, not to APF internal nodes;
- prompts do not own navigation, gates or confirmed state;
- no automatic approval;
- no Ordo core modification;
- no dependency on production-ready transcript replay.

### Milestones

- `PMP-0`: completed;
- `PMP-1`: completed;
- `PMP-2`: completed;
- `PMP-3`: completed;
- `PMP-4`: completed;
- `PMP-5`: completed;
- `PMP-6`: completed;
- `PMP-7`: completed as technical mechanism evidence;
- `PMP-8`: completed.

Normative references:

- `improvements/playbook_authored_mini_prompts/PMP_0_ENHANCEMENT_SCOPE.md`
- `improvements/playbook_authored_mini_prompts/DD_APF_PMP_001.md`

---

## BL-APF-002B — Internal APF node mini-prompt applicability review

Status: `deferred-pending-separate-process-owner-decision`  
Implementation started: `false`  
Implementation order: `not decided`

Purpose: evaluate whether mini-prompts should later be attached to APF's own internal nodes.

Activation conditions:

1. BL-APF-002A implementation is complete;
2. at least one real playbook has been created using the new mechanism;
3. pilot evidence and retrospective are available;
4. the process owner explicitly approves an APF-internal applicability review.

No internal APF mini-prompts may be introduced under BL-APF-002A.
