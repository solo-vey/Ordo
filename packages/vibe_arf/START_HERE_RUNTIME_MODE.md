# START HERE — Vibe ARF Runtime Mode

## IR ACCESS PROTOCOL — HARD RULE
`compiled/program.ir.json` is a CLI-owned runtime internal. Do not conduct guided intake by reading raw compiled IR. Use CLI runtime reports. A direct raw IR read is a protocol violation; CANARY detection and `verify-session` are the integrity check.

## Runtime loading protocol
Read this file, read `ordo.yml`, resolve `source/program.ordo.yaml`, verify `compiled/program.ir.json` freshness, initialize/load runtime state, then derive the next step through the approved Ordo CLI. In a portable package use `cli_embedded/ordo`; in this development package the approved Ordo authoring CLI is permitted.

## Source of truth
`ordo.yml → source/program.ordo.yaml → compiled/program.ir.json → run_state/runtime state → generated artifacts`.

## No memory mode
Do not conduct guided intake from memory. For a fresh run use `runtime-entry`. After a submit, use the CLI-produced `next_node` and `next-step` with the live runtime state; do not infer continuation from memory.

## CLI truthfulness
Only claim `CLI status: executed_cli_passed` when CLI commands actually ran and evidence was produced. Otherwise report the truthful non-executed state.

## Fallback mode — hard-stop fallback mode
If neither `cli_embedded/ordo` nor another approved Ordo CLI can execute, stop. Do not silently continue. Any explicitly approved nondeterministic fallback must mark outputs `DETERMINISM_NOT_ENFORCED`.

## Mechanical gate advancement
When the persisted `current_node` is a gate, first inspect it through the packaged runtime. If it is `mechanical/deterministic`, execute `advance-gate` and continue from the persisted `next_node` without asking the analyst. Never auto-decide `self_verification`, `self_consistency`, or `human` gates. For a `human/human_decision` gate, only an explicit analyst decision may be submitted with `decide-gate --decision approve|reject --evidence ...`; the adapter must persist that authority evidence and must not infer it. If direct execution permission is unavailable after ZIP extraction, invoke the packaged CLI as `python cli_embedded/ordo ...`.

## Gate discipline
Check required gates and state before advancing. Never bypass a blocked gate.

## Artifact validation discipline
Compilation alone is not final validation. Validate required verification assets, package/artifact contracts and consistency before acceptance.

## Runtime checkpoint discipline
One node at a time; one contract at a time; one decision at a time. Earliest incomplete node wins. Preserve state across answers and do not skip required checkpoints.

## One question protocol
When a human answer is actually required, ask one focused question. In Vibe ARF authoring, a user decision question is legal only through `N_HDG_QUESTION` after the Human Decision Gateway establishes a consequential user-owned blocker. Open model-owned parameters are not user questions.

## Vibe-specific behavior
The user speaks domain language; the system speaks Ordo. Model-owned engineering decisions remain autonomous. Default presentation is Business View. Semantic feedback becomes a change request and returns through Change Impact; it is not a request for the user to edit nodes or YAML.

## Session integrity
`verify-session` becomes meaningful after the CLI has created at least one M59.3/M59.4 checkpoint snapshot. Before relying on session-chain evidence, run `verify-session`; `session-chain: intact` is accepted, while a broken chain or CANARY leak invalidates the session.

## Vibe semantic resume contract
On restart/reload, reconstruct semantic state from persisted revision + ledger + session evidence. Recompute the Human Decision Gateway queue and Orchestrator next-best-action. Never re-ask a resolved question unless a later material change invalidated its upstream basis. Resume from the earliest materially incomplete semantic action, not from the beginning. If integrity is broken, fail closed to the last verified checkpoint; do not guess.

## Portable authoring support (alpha.10)
Use packaged embedded Ordo tooling and canonical support; do not depend on hidden workspace state. FAST_EDIT remains the default development contour.
## alpha.16 executable verification and inheritance protocol

Runtime/authoring behavior must follow these durable rules:

- governing `PLAYBOOK_LAWS.md` is loaded and propagated verbatim to generated runnable playbooks;
- algorithmic verification is driven by revision-explicit `verification_profile.json`, not remembered command lists;
- mandatory phases are FAST → PRE_EDITOR → POST_EDITOR → RELEASE;
- missing required runner/evidence/timeout/failure blocks the corresponding phase;
- editor/live-run/dry-check outputs enter readiness only as formal machine-readable external evidence;
- before final generated graph design, every executable responsibility is classified as
  `deterministic`, `model_judgment`, or `human_authority`;
- deterministic responsibilities use Ordo state/gates, CLI helpers, or package-local Python;
- model judgment is allowed only where deterministic resolution is insufficient and must declare a semantic reason
  plus evidence contract;
- consequential human-owned content/approval decisions remain human authority;
- each generated runnable package materializes laws, verification profile, execution responsibility map,
  invariant register, and applicable package-local validators;
- `PRE_EDITOR` fails until the responsibility map is complete and valid;
- raw deterministic tool output is interpreted by the AI before user-facing explanation.


## Explicit runtime tools/templates (alpha.16)
Runtime graph visibly exposes deterministic helper boundaries via canonical `node_context.allowed_tools`.
Package-local Python remains declared/executed through `verification_profile.json` rather than an invented Python-node construct.
Concrete document templates and package assembly contracts have explicit graph nodes, and each Ordo external output is bound
to an explicit materialization/handoff node before exposure.


## Visible deterministic verification stages (alpha.16)
The runtime graph contains five explicit deterministic stages: SOURCE, STRUCTURE, ARTIFACTS, REGRESSION, RELEASE.
Each stage has canonical `node_context.allowed_tools`, concrete helper/Python references, and machine-readable evidence.
Detailed individual commands remain in `verification_profile.json` so the graph stays readable without hiding algorithmic execution.


## Full language-tool validation (alpha.17)
Before a candidate is handed off, PRE_EDITOR must include the canonical Ordo package checks that previously
were omitted: `validate-artifacts`, `consistency`, `validate-output`, `validate-lock`, `check-conflicts`,
and `repo-check`, in addition to lint/compile/tests/coverage/runtime/targets. Missing generated-output
surface or dependency lock is a blocking package defect, not something the model may ignore.


## Single responsibility architecture (alpha.18)
Each executable node owns one cohesive responsibility. A deterministic RUN node produces evidence; a following
mechanical gate decides PASS/FAIL routing. Materialization, validation and handoff are separate responsibilities.
Several commands may stay inside one RUN node only when they form one cohesive evidence report.


## Information-first authoring runtime rule (alpha.24)
For Vibe authoring sessions, the runtime must not treat the executable process graph as the primary design source. Required artifacts are decomposed into the persisted `authoring/` information model first. `validate_authoring_information_model.py` must pass before graph synthesis. After source materialization, `validate_information_projection.py --require-bound` must pass before downstream structure/release qualification. The information model is design-time Vibe state and never overrides canonical Ordo runtime semantics.

## Authority-first and simulation-first runtime rule (alpha.26)
Review bundles are derived interaction projections, not semantic truth. Model proposals remain quarantined until approved projection/canonicalization rules allow persistence. Human authority decisions are revisioned and locally verified after apply. Before analyst-ready handoff of a runnable generated candidate, execute the required scenario matrix against the exact candidate with the pinned Simulation Kit when applicable, verify fixture closure and non-vacuous runtime gate evidence, and classify defect ownership. Runtime-adapter conformance failures must be handed to the adapter owner rather than converted into playbook workarounds.

## Default debug/handoff evidence and progress visibility
On session bootstrap, initialize the working handoff evidence directory (`debug_handoff/working/`). Keep it current throughout autonomous execution. Record intermediate revisions, problems, repairs, tests, gate history, checkpoints, and artifact lineage. Emit a concise **progress event** to chat when entering a meaningful stage/node, when a gate resolves, when repair/rerouting is chosen, and when a checkpoint is persisted. Each progress event should state what is active, what just happened, and the next action. Do not require the user to ask for this mode each time. Quiet chat may suppress some messages only when explicitly requested; evidence accumulation remains enabled.
