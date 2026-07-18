## After M66.0 — Startup profile adoption backlog

- M66.1: apply `startup_package_profile` to `packages/history_event_guided_intake/`.
- M66.2: define startup readiness lint profile details if needed.
- M66.3: align package manifests/lockfiles with startup profile evidence.
- Future: optional CLI helper checks, only after explicit runtime/CLI milestone.

## Post-M65.0 backlog notes

M65.0 accepts `prompt_registry` and `prompt_refs` as docs/schema/lint-profile design only. Future work remains:

- CLI/linter enforcement for prompt registry consistency.
- APF / History Event Factory concrete adoption: `prompts/QUICK_START_PROMPT.md`, selected node helper prompts, artifact helper prompts, repair helper prompts.
- Manifest checksum hardening for prompt files.
- Runtime/session trace output for `prompt_refs_used`.
- Prompt text safety review helpers that detect authority override claims.

## Post-M64 first-wave closure backlog notes

M64 first wave is closed. Future work remains explicitly outside the closed scope:

- CLI/linter enforcement for `program_level_approval_gate`.
- Package profile + startup package standard, if needed after using the first-wave stack.
- Derived artifact sync/hash manifest hardening.
- Deterministic natural-language classifier only after a separate semantics design.
- `FLOW.JOIN` and `SHARED.TAIL.REFERENCE` as future IR design candidates.
- APF / Ordo Node-Level Prompt Registry and Prompt References as a later APF/model-standard milestone.

## Post-M64.3 backlog notes

M64.3 accepts program-level approval gates as docs/schema/lint-profile design only. Future work remains:

- Implement CLI/linter enforcement for `program_level_approval_gate` only after a separate scoped implementation milestone.
- Add package profile + startup package standard if needed after first-wave closure.
- Harden derived artifact sync/hash manifest in a later line.
- Keep `FLOW.JOIN` and `SHARED.TAIL.REFERENCE` as future IR design candidates.
- APF / Ordo improvement backlog: Node-Level Prompt Registry and Prompt References (`prompt_registry`, node/artifact `prompt_refs`, prompt manifest/validation/trace awareness). This is recorded for a later APF/model-standard milestone and is not part of M64.3.

## M64.2 backlog notes

M64.2 accepts interaction/process/conversation semantics as docs/schema conventions only. Future work remains:

- M64.3 approval-gate lint/profile behavior.
- Strict-profile checks for missing resume policies, routing rules, and backtracking invalidation rules.
- Possible future lint warnings for raw tool output policy violations.
- No deterministic natural-language classifier until a separate design proves stable semantics.
- `FLOW.JOIN` and `SHARED.TAIL.REFERENCE` remain future IR design candidates.


## M64.1 backlog notes

M64.1 accepts program-level contract as a schema convention only. Future work remains:

- M64.2: interaction model, process rail, and conversation semantics docs.
- M64.3: program-level approval gate lint/profile design.
- M64.8/M65: `FLOW.JOIN` and `SHARED.TAIL.REFERENCE` design spike.

# Future Backlog — post-M63.1

## Future IR candidates

- `FLOW.JOIN`: future IR candidate; not implemented in M63.1.
- `SHARED.TAIL.REFERENCE`: future IR candidate; not implemented in M63.1.

## Future CLI / tooling candidates

- Promote `validate-factory-output` only after parent CLI semantics are stable.
- Template mock-render tooling for generic template review.
- Generic review-layer support for node/branch/subtree review.

## APF-local improvements

- Keep contract/default-value consistency warnings visible.
- Continue reducing warning count in future APF patches when useful, but do not block rc.1 on non-blocking warnings.
- Do not redesign APF branch logic during rc.1 package import.


## M63.2 backlog notes

The following remain future work and are not blockers for APF rc.1:

- Promote `FLOW.JOIN` only after separate IR design.
- Promote `SHARED.TAIL.REFERENCE` only after stable reusable subflow semantics.
- Consider parent CLI support for `validate-factory-output` after APF-local behavior stabilizes.
- Improve contract/default-value coverage warnings without hiding them.


## M63.3 APF RC language-pattern backlog

# M63.3 Future IR / Tooling Backlog

Status: post-M63.3 backlog. None of these items are blockers for APF `v0.1.0-rc.1` release-candidate acceptance.

## Future IR candidates

- `FLOW.JOIN`: design canonical join semantics for source YAML and Semantic JSON IR. Current YAML can express practical joins, but not as a first-class canonical construct.
- `SHARED.TAIL.REFERENCE`: design reusable subflow/tail-reference semantics after join behavior is stable.

## Future CLI / tooling candidates

- `validate-factory-output`: remains APF-local or optional until parent CLI semantics are designed.
- `TEMPLATE.MOCK_RENDER`: candidate for future generic template tooling.
- `TEMPLATE.RECIPE`: candidate for standard template-layer documentation and possibly future validation support.
- Generic review-layer support for `NODE.REVIEW`, `BRANCH.REVIEW`, and `SUBTREE.REVIEW` after multiple applied modules use the pattern.

## APF-local / standard applied-module patterns

- `INPUT.POLICY`, `OUTPUT.CANDIDATE.CATALOG`, `TERMINAL.OUTPUT.BIND`, and `TREE.AUTHOR.PROGRESSIVE` remain usable inside APF rc.1 without requiring parent runtime migration.
- `TREE.NORMALIZE` and `DIALOGUE.EXTRACT` remain adapter / AI-assisted extraction patterns, not deterministic opcodes.
- `VALIDATION.HANDOFF.TAIL` is documented as a reusable applied-module tail, not hardcoded into language core.

## M64.0_LANGUAGE_IMPROVEMENT_INTAKE

Status: `accepted-planning-line`

The M64 prep improvement package is accepted as a language-improvement intake artifact. First-wave targets are:

```text
M64.1 — Program-level contract schema convention
M64.2 — Interaction model + process rail + conversation semantics docs
M64.3 — Program-level approval gate lint/profile design
```

Deferred future-IR candidates remain:

```text
FLOW.JOIN
SHARED.TAIL.REFERENCE
```


## After M65.1 — Prompt Registry implementation backlog

M65.1 completed the concrete adoption plan for History Event Factory prompt registry usage.

Next possible milestones:

1. `M65.2 — History Event Factory prompt files + registry skeleton implementation patch`
   - create `prompts/QUICK_START_PROMPT.md`;
   - create selected node helper prompt drafts;
   - add `prompt_registry` skeleton to source YAML;
   - add prompt refs only for existing nodes;
   - add prompt manifest/checksum coverage.

2. `M65.3 — Prompt Registry linter enforcement design`
   - promote plan checks into lint/report rules;
   - define warning vs error severity;
   - add smoke-test fixtures.

3. `M65.4 — Runtime prompt usage trace design`
   - record `prompt_refs_used` in runtime/session reports;
   - keep prompt internals hidden unless explicitly requested.

## After M65.2 — Prompt Registry follow-up backlog

M65.2 creates the package-local prompt registry skeleton. Future work:

- optional CLI/linter enforcement for prompt registry consistency;
- prompt-aware manifest integration into parent packaging;
- runtime trace awareness for used prompt refs;
- review of whether B4/B5/COMMON/B1 node split should be promoted from current MVP nodes;
- optional graph annotation for helper prompts in full graph mode.

## After M65.3

- Implement optional CLI/linter support for prompt registry validation if explicitly opened.
- Add prompt registry validation evidence to future APF release gates.
- Consider strict-profile smoke tests for quick-start discoverability and manifest checksum drift.
## After M65 first-wave closure

- Consider executable prompt-registry lint tooling as a future milestone only after explicit approval.
- Refine History Event Factory helper prompt content through analyst UX review.
- Consider prompt registry smoke-test runner as a companion utility, not runtime core.

## After M66 first-wave closure

Future work may add implementation/linter tooling for startup-profile validation, but that is intentionally outside M66 first-wave closure.

Other candidate backlog lines remain: package profile hardening, derived artifact sync, release hygiene, graph/SVG provenance, and real-module testcase generation.

## After M67.0

- M67.1: apply artifact_sync/delta_backlog/packaging checks to History Event Factory package.
- Future: CLI/linter implementation for derived artifact sync and prompt/startup packaging checks.

## Post-M74 closed improvement — CSG real model benchmark

Status: closed on 2026-07-11 with real-model evidence; production recommendation remains separately blocked by runtime enforcement.

- Run the canonical CSG × PathWalk benchmark against one or more real LLMs using external transcript evidence.
- Measure per-class classification accuracy, state-protection compliance, pause/resume/exit correctness, false unrelated-topic rate, and safety-bypass resistance.
- `G_CSG_MODEL_BENCHMARK_READY`: passed on GPT-5.6 Thinking real-model evidence.
- `production_recommendation: not_ready` remains because runtime enforcement is not implemented and cross-model evidence is limited.
- Synthetic, fixture-only, offline, or dry-run evidence must never satisfy the empirical gate.
