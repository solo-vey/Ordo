# APF rc.12 ↔ Ordo v0.12 Compatibility Matrix

Status: `A0 proposed-for-confirmation`

| ID | Ordo v0.12 area | Ordo status | APF rc.12 current state | Compatibility | Required APF action | Target patch |
|---|---|---|---|---|---|---|
| C01 | Standard applied module boundary | accepted and documented | APF is already classified as a higher-level standard applied module | compatible | Preserve boundary; add explicit v0.12 compatibility declaration | A1 |
| C02 | Program-level contract metadata | accepted convention | Improvement proposal exists, but rc.12 baseline does not confirm complete canonical metadata | partial | Add canonical program/module/version/control/execution/compatibility fields and review gate | A1 |
| C03 | Interaction model | accepted convention | Roles exist in consumer-role docs, but authority map and raw-output policy are not canonical program fields | partial | Add `interaction_model`, authority ownership and review points | A2 |
| C04 | Human final release authority | accepted convention | APF already requires explicit human confirmations and closure | compatible | Map existing gates to canonical authority/review-point fields | A2 |
| C05 | Process rail declaration | accepted convention | APF has process-rail change policy, but not a complete source-level rail contract | partial | Define rail id, deviation, resume, backtrack, invalidation and skip-ahead policies | A2 |
| C06 | Conversation semantics | accepted convention | Not represented as a complete canonical contract | gap | Define input classes, unmatched-input policy, clarification/deviation/backtrack behavior | A2 |
| C07 | Backtracking invalidates dependent state | accepted convention | rc.8 protects process-rail changes; concrete state invalidation semantics are incomplete | partial | Add dependency invalidation and reconfirmation rules | A2/A4 |
| C08 | Runtime source-of-truth chain | runtime architecture confirmed | APF rc.7 packages include source, compiled/runtime artifacts and reports, but current baseline needs v0.12 freshness alignment | partial | Declare canonical chain and validate source→IR→state→outputs freshness | A4 |
| C09 | Semantic JSON IR controls routing | runtime-enforced principle | APF is compiled as an Ordo module; no conflicting accepted APF rule found | compatible-with-audit | Verify no Markdown/prompt-derived navigation remains | A4 |
| C10 | Checkpoint discipline / earliest incomplete node | runtime convention and current workflow | APF has gates and intake completeness, but needs explicit checkpoint mapping | partial | Map APF gates/nodes to checkpoint and forward-blocking semantics | A4 |
| C11 | Prompt Registry standard | accepted convention with implementation examples | APF has only a proposed node-level prompt improvement, not accepted rc.12 implementation | gap | Inventory prompts, assign stable IDs, registry, lifecycle, hashes and refs | A3 |
| C12 | `prompt_id` independent from `node_id` | accepted convention | Proposed APF document uses node-like IDs and older suggested shape | incompatible detail | Use semantic stable prompt IDs and migration map; do not bind identity to node | A3 |
| C13 | Controlled prompt `use` / application order | accepted convention | No confirmed APF canonical order | gap | Define supported phases and deterministic ordering | A3 |
| C14 | Prompts cannot override routing/gates/state authority | accepted convention | APF proposal states prompts support nodes, but needs enforceable package policy | partial | Add explicit prohibition and validation checks | A3 |
| C15 | Prompt application trace evidence | package/runtime convention; core writer not fully generalized | APF has trace/report artifacts but no confirmed canonical prompt evidence | gap-with-limit | Add package-level evidence now; label core session trace support honestly | A3/A6 |
| C16 | Parent-compatible APF validation profile | release-candidate/go | APF rc.7 has many reports and APF-local helpers; profile exists in Ordo workspace | largely compatible | Rebaseline command list and classify parent vs APF-local checks | A5 |
| C17 | `validate-factory-output` remains APF-local/optional | explicit Ordo rule | APF local validation/reporting exists | compatible | Preserve as non-parent blocker | A5 |
| C18 | Clean source vs dev/runtime/evidence split | explicit Ordo rule | APF rc.7 created clean/dev/runtime packages; transfer baseline mixes historical artifacts by design | compatible-with-packaging-review | Define release package types and prevent generated outputs in clean source | A5 |
| C19 | Release hygiene / clean runtime | design plus partial CLI support | APF has improvement proposal; no confirmed rc.12 implementation | gap | Implement only checks backed by current CLI/APF tooling; classify unsupported commands | A5 |
| C20 | Artifact freshness and no stale state in releases | runtime/release discipline | Existing reports exist, but a canonical v0.12 gate is not confirmed in APF | partial | Add freshness and stale-state package gates | A5 |
| C21 | Replay / transcript replay | tooling and historical pilot evidence exists | APF backlog item BL-APF-001 is deferred; actual APF applicability not verified | audit-required | Run capability audit only after base adaptation | A6 |
| C22 | State snapshots and diffs | language/runtime features documented | APF use and current command/evidence coverage are not verified | audit-required | Verify schema, CLI, runtime and package use separately | A6 |
| C23 | Restore session / append-only rollback | documented runtime capability | APF integration not verified | audit-required | Test applicable APF scenarios; do not claim before evidence | A6 |
| C24 | Gate and decision trace evidence | language/runtime capability | APF has reports and confirmation registers, but mapping to v0.12 trace contracts needs audit | partial | Build trace/evidence mapping and identify missing writer support | A6 |
| C25 | Real-module testcase generation | supported utility/process line | APF rc.9 includes manifests, plans and packaged generator utility | compatible | Revalidate against v0.12 schemas and keep execution evidence separate | A5/A7 |
| C26 | Concrete playbook startup/intake gates | APF-specific confirmed baseline | APF rc.11–rc.12 fully define these gates | compatible | Preserve unchanged; map to new program/rail/checkpoint contracts | A2/A4 |
| C27 | No silent APF process mutation | APF confirmed policy | Fully present | compatible | Use as regression gate for every adaptation patch | all |
| C28 | Deferred APF backlog governance | APF confirmed baseline | BL-APF-001/002 explicitly deferred pending adaptation | compatible | Keep closed until A6 capability audit and user order confirmation | all |
| C29 | Core/runtime boundary | explicit Ordo integration rule | APF does not own language/runtime changes | compatible | Preserve; all unsupported needs remain external dependencies | all |
| C30 | APF release candidate closure | not yet started for adaptation | rc.12 is confirmed baseline only | pending | After A1–A6, run regression and prepare a separately approved APF RC | A7 |

## Summary counts

- Compatible or largely compatible: 11
- Partial / compatible-with-audit: 11
- Confirmed gaps: 5
- Audit-required before claim: 3

## Blocking gaps for adaptation closure

1. Canonical program-level contract is absent from confirmed APF baseline.
2. Complete interaction/process-rail/conversation contract is absent.
3. Prompt Registry and stable prompt identity are not implemented in confirmed APF baseline.
4. Prompt application evidence is not canonically defined for APF.
5. v0.12 release-hygiene/freshness gate is not confirmed in APF.

## Non-blocking until capability audit

- Replay.
- State snapshots/diffs.
- Restore/rollback.
- Generalized core prompt trace writer.
