# Ordo Consolidated Backlog

Status: canonical open-work register
Created: 2026-07-11
Rule: no deferred item is considered safely recorded unless it has an ID in this file and in `manifests/CONSOLIDATED_BACKLOG.json`.

## P0 — Important open items

### BL-ORDO-001 — CSG production recommendation closure

Status: `in-progress-evidence-reconciliation`

Confirmed complete:
- production thresholds are defined in M75.4;
- fail-closed fallback is defined;
- append-only rollback to the last valid snapshot is defined;
- runtime enforcement gate is implemented.

Blocking evidence problem:
- `M75_4_VALIDATION_REPORT.json` claims `cross_model_repeated_run_gate: passed`;
- persisted `CSG_CROSS_MODEL_BENCHMARK_REPORT.json` says `G_CSG_CROSS_MODEL_BENCHMARK_READY: blocked`, with 1 model target / 1 valid run against a 3-target × 2-runs policy;
- `M75_3_1_VALIDATION_REPORT.json` records RUN-06 as `failed-explicit-protected-state-change`;
- RUN-07 was supplied in conversation and appears semantically clean, but is not persisted/scored in the current workspace.

Remaining:
- persist and canonically score RUN-07;
- rebuild the cross-model/repeated-run report from persisted evidence;
- satisfy the configured benchmark policy or explicitly approve a narrower production scope;
- rerun production readiness from reconciled evidence;
- issue `G_CSG_PRODUCTION_READY` only if rebuilt evidence passes.

Reconciliation evidence:
- `reports/BL_ORDO_001_M75_4_EVIDENCE_RECONCILIATION.json`

### BL-ORDO-002 — APF graph cycles and dead-end paths

Status: `open`

Evidence:
- M74.6 modularization preserved semantic equivalence;
- both monolithic and modular APF graphs report 4141 cycle edges and 2 dead-end paths.

Impact:
- clean terminal-path testcase generation remains blocked for APF;
- modularization did not cause the issue, but did not resolve it.

Required work:
- classify intentional review loops versus invalid execution cycles;
- add graph semantics for review/backtrack loops or exclude non-execution edges from terminal-path enumeration;
- resolve or explicitly model the two dead-end paths;
- rerun PathWalk clean/noise testcase generation.

### BL-ORDO-003 — Safe runtime execution of generated real-module testcases

Status: `closed`

Closure: M82.0–M82.4. Hardened child-process execution, watchdog, isolated sandboxes, versioned evidence, failure taxonomy, generate-and-run integration, and regression closure completed.

Evidence:
- `M82_4_REGRESSION_MATRIX_AND_BL_ORDO_003_CLOSURE_REPORT.md`
- `M82_4_VALIDATION_REPORT.json`

### BL-ORDO-004 — Backlog and maturity-state synchronization

Status: `open`

Problem:
- historical backlog and manifests contain stale statements such as CSG runtime enforcement being unimplemented;
- completed M64–M75 items remain repeated as future work in older files.

Required work:
- update canonical CSG maturity and release manifests from M75 evidence;
- mark superseded backlog entries as `closed` or `superseded` without deleting audit history;
- add a closure gate requiring every milestone to update this consolidated backlog.

## P1 — Strategic improvements

### BL-ORDO-005 — Cross-model and repeated-run CSG benchmark

Status: `open`

Required work:
- run the canonical 26-case blind dataset on at least two additional model/version targets;
- run repeated trials where nondeterminism is material;
- retain raw evidence and per-class metrics;
- define comparison rules across model and Ordo versions.

### BL-ORDO-006 — PathWalk score calibration and benchmark purpose

Status: `open`

Source: `ordo_pathwalk/OPEN_QUESTIONS.md`.

Required decisions:
- primary purpose: model comparison, Ordo release QA, or research benchmark;
- benchmark-pinned versus compatibility-current reporting;
- calibrate default weights using real runs across supported modes;
- preserve raw component metrics regardless of weights.

### BL-ORDO-007 — First-class flow reuse semantics

Status: `future-design`

Candidates:
- `FLOW.JOIN`;
- `SHARED.TAIL.REFERENCE`.

Required work:
- define source semantics;
- define namespace and state merge rules;
- define compiler/IR representation;
- define trace and test semantics;
- validate against at least two real applied modules before promotion.

### BL-ORDO-008 — APF real-case replay and analyst-experience validation

Status: `deferred-owner-decision`

Source: APF `BL-APF-001`.

Required work:
- minimized real analyst transcripts;
- pre-change/post-change state;
- analyst-facing rendering comparison;
- no deterministic replay claim until runtime replay infrastructure is production-ready.

### BL-ORDO-009 — APF internal mini-prompt applicability review

Status: `deferred-owner-decision`

Source: APF `BL-APF-002B`.

Activation conditions:
- downstream playbook mini-prompt mechanism used on at least one real playbook;
- pilot evidence and retrospective available;
- explicit process-owner approval.

### BL-ORDO-010 — Translation completion and synchronization

Status: `active-paused-for-apf-improvement`

Canonical persisted state:
- English main chapters are present through Chapter 80;
- `appendix_d_checklists.md` and `appendix_e_anti_patterns.md` are translated and persisted under `book/en/chapters/`;
- Appendix F sections F.1–F.8 are translated in a working fragment but are not yet integrated into the canonical English book;
- Appendix F sections F.9–F.14 remain untranslated;
- previously reported Appendix A–C completion must be reconciled because corresponding canonical files are not present in the current workspace.

Remaining work:
- reconcile or recreate English Appendix A–C from the Ukrainian canonical sources;
- integrate the translated Appendix F F.1–F.8 fragment into `book/en/chapters/`;
- translate Appendix F F.9–F.14 without shortening technical content;
- synchronize English assets and internal links;
- rebuild `book/en/book_manifest.json` in the same reading order as the Ukrainian book;
- run structural, link, code-fence, terminology, and Cyrillic-residue validation;
- generate the English PDF only after all blocking checks pass.

### BL-ORDO-011 — Prompt Registry follow-up reconciliation

Status: `needs-revalidation`

Check against M65–M71 evidence:
- CLI/linter enforcement;
- manifest checksum coverage;
- runtime `prompt_refs_used` trace;
- prompt safety/authority checks;
- graph annotations and smoke-test tooling.

### BL-ORDO-012 — Startup/package profile and derived-artifact hardening reconciliation

Status: `needs-revalidation`

Check against M66–M70 evidence:
- startup profile adoption;
- package manifest/lockfile evidence;
- derived artifact sync/hash hardening;
- release hygiene and packaging checks.

### BL-ORDO-013 — Generic template and review tooling

Status: `future-candidate`

Candidates:
- `TEMPLATE.MOCK_RENDER`;
- `TEMPLATE.RECIPE`;
- generic `NODE.REVIEW`, `BRANCH.REVIEW`, `SUBTREE.REVIEW` support;
- parent CLI `validate-factory-output` after APF-local semantics stabilize.

## Closed during this audit

- CSG real-model benchmark itself: closed, 26/26 on GPT-5.6 Thinking.
- CSG runtime enforcement: closed by M75.1.
- CSG canonical multi-step integration validation: closed by M75.2.
- full CLI suite uncertainty: closed; 182/182 pass using partitioned execution.
- M74 public baseline split and APF modularization: closed.

## Backlog governance rule

Every future milestone closure must:

1. reference affected `BL-ORDO-*` IDs;
2. update status and evidence in this file and JSON manifest;
3. register every new deferred item before closure;
4. never rely only on a chat promise or a milestone report;
5. mark older contradictory records as superseded rather than silently ignoring them.

### BL-ORDO-014 — APF post-generation defect review for critical artifacts

Status: `in-progress`

Source:
- `APF_POST_GENERATION_DEFECT_REVIEW_RATIONALE_UK.md` supplied on 2026-07-12.

Problem:
- structural and internal-consistency validation can accept technically plausible but unsupported executable contracts;
- critical artifacts need evidence provenance, adversarial defect review, cross-artifact reconciliation, targeted invalidation, and mandatory post-correction review before confirmation.

Planned milestone line:
- M83.0 — improvement intake, threat model, scope, criticality model, and process-boundary contract;
- M83.1 — evidence provenance classes, review record schema, and confirmation eligibility gates;
- M83.2 — adversarial defect review and cross-artifact reconciliation semantics;
- M83.3 — targeted invalidation, correction, post-correction review, and Execution Trace events;
- M83.4 — APF integration, regression matrix, documentation, and backlog closure.

Current work:
- M83.0 started.

## P2 — Revalidation candidates from old backlog

These entries may already be partially or fully implemented by later milestones. They must be checked before reopening work.

### BL-ORDO-015 — Release and CI Closure

Status: `open`

Priority: `high`

Scope:
- finalize production-release closure for the current Ordo language package;
- bind release evidence to the current repository tree and build identity;
- require CI-backed validation before formal closure;
- preserve existing local closure evidence without overstating repository-level completion.

Current state:
- local packaging and validation work exists;
- formal closure is blocked by BL-ORDO-022 because no GitHub repository/CI evidence is available.

Dependency:
- BL-ORDO-022.

### BL-ORDO-016 — Current-tree packaging self-check

Status: `closed-M85.5`

Closure evidence:
- canonical `current_tree_sha256`;
- unique `build_session_id`;
- validation evidence binding;
- pre-ZIP reconciliation;
- post-validation mutation blocking;
- successful package simulation;
- independent post-unpack checksum and build-manifest verification.


#### Additional reference evidence — implementation-branch anti-patterns

- `language/improvement_intake/bl_ordo_020_references/APF_IMPLEMENTATION_PROMPT_AS_IMPLEMENTATION_ANTIPATTERNS_UK.md`
- Covers `AP-29 PROMPT_AS_IMPLEMENTATION`, `AP-30 PACKAGE_VALIDATION_WITHOUT_COMPLETENESS_VALIDATION`, `AP-31 MANDATORY_BRANCH_SHORT_CIRCUIT`, and `AP-32 FINAL_LABEL_OVERCLAIM`.
- Intake status: `registered-reference-only`; checks and gates are not activated until BL-ORDO-020 implementation.

### BL-ORDO-017 — Benchmark Evidence Hardening

Status: `closed-M86.5`

Closure evidence:
- canonical benchmark run/evidence schema;
- provider-neutral adapter and driver;
- adversarial CSG dataset v2;
- alias normalization and mismatch taxonomy;
- immutable artifact replay verification;
- reproducibility fingerprint;
- multi-run/multi-model closure gate;
- full M86 targeted regression passed.

Qualification:
- closure is based on deterministic fixture providers;
- external real-provider execution remains operational evidence, not a blocker for the framework implementation closure.


#### Additional reference evidence — scope confirmation and execution routing

- `language/improvement_intake/bl_ordo_020_references/APF_SCOPE_CONFIRMATION_EXECUTION_ROUTING_ANTIPATTERNS_UK.md`
- Covers `SCOPE_CONFIRMATION_AS_IMPLEMENTATION_AUTHORIZATION` and `COMPLEXITY_ROUTING_AND_EXECUTION_IN_ONE_NODE`.
- Proposed blocking gates: `SCOPE-NOT-AUTHORIZATION-01`, `COMPLEXITY-ASSESSMENT-REQUIRED-01`, `EXECUTION-ROUTE-SELECTION-01`, `REPOSITORY-MUTATION-AUTHORIZATION-01`, `NO-IMPLEMENTATION-BEFORE-ROUTE-01`, `PUSH-PR-SEPARATE-AUTHORIZATION-01`.
- Intake status: `registered-reference-only`; checks and gates remain inactive until BL-ORDO-020 implementation.

### BL-ORDO-018 — CLOSED at M87.6

Status: `closed-qualified`

Closure basis:
- 240 independent real OpenAI API runs;
- 120 complete paired A/B comparisons;
- 120 blind-scored pairs;
- two distinct resolved models;
- Ordo mean advantage: `+0.65625`;
- paired bootstrap 95% CI: `[-0.08333, 1.44792]`;
- practical non-inferiority margin: `-0.10` points on a 100-point scale;
- no fabrication or state-protection regression gate failure.

Qualification:
- closure uses a practical non-inferiority margin rather than the prior strict zero margin;
- result is bounded to the frozen M87 dataset, prompts, models and scorer rubric.

### BL-ORDO-020 — CLOSED at M88.5

Status: `closed`

Closure scope:
- canonical `ANTIPATTERN.DEF`;
- canonical `DETECT.RULE`;
- canonical `ANTIPATTERN.FINDING`;
- severity and enforcement policy;
- six initial runtime detectors;
- APF activation profile;
- blocking/advisory gate integration;
- recovery, remediation and evidence references;
- end-to-end regression and closure gate.

Qualification:
- closure covers the initial Anti-pattern Layer only;
- positive Process Pattern Engineering remains in BL-ORDO-024;
- adding new anti-patterns requires registry, rule, extractor, fixture and activation-profile updates.

### BL-ORDO-021 — CLOSED at M89.5

Status: `closed`

Closure scope:
- canonical migration intake contract;
- clause inventory and semantic classification;
- ambiguity capture;
- dependency reconstruction;
- Ordo construct mapping;
- source-to-playbook traceability matrix;
- migration completeness and silent-loss gate;
- end-to-end migration package generation;
- representative all-in-one instruction regression fixture.

Qualification:
- closure validates the migration framework and representative fixture;
- domain-specific migrations still require source-specific review of ambiguities and mappings;
- no new core Ordo language primitives were required.

### BL-ORDO-022 — GitHub CI Closure for BL-ORDO-015

Status: `blocked`

Priority: `high`

Goal:
Provide repository-backed CI evidence required to formally close BL-ORDO-015.

Scope:
- connect or identify the canonical GitHub repository;
- add or verify CI workflow for validation, tests and package integrity;
- bind CI run evidence to commit SHA and release artifact;
- produce reproducible repository-level closure evidence.

Blocker:
- no GitHub repository is currently available in this project context.

Dependency:
- blocks BL-ORDO-015.

### BL-ORDO-023 — Strict-Zero A/B Benchmark Revalidation

Status: `open`

Priority: `medium`

Goal:
Re-run or extend the Ordo vs Plain Prompt benchmark until the lower bound of the paired 95% confidence interval is at least `0.00`, without using a practical non-inferiority margin.

Acceptance criteria:
- independent third scorer model or multi-scorer adjudication;
- larger sample or additional task strata;
- lower 95% CI bound `>= 0.00`;
- no fabrication or state-protection regression;
- reproducible raw API evidence and blind-scoring package.

Origin:
Created when BL-ORDO-018 was closed using the qualified `-0.10` practical non-inferiority margin.

### BL-ORDO-024 — Process Pattern Engineering

Status: `open`

Priority: `medium`

Scope:
- `PATTERN.DEF`;
- positive reusable process patterns;
- pattern composition;
- process templates;
- recommendation and optimization;
- broader recovery and remediation orchestration;
- reusable evidence requirements for process patterns.

Dependency:
- starts only after BL-ORDO-020 Anti-pattern Layer reaches closure or a stable integration point.

Origin:
Split from BL-ORDO-020 before M88.0.


### BL-ORDO-025 — APF Linter Memory and Performance Hardening

Status: `open`

Priority: `medium`

Origin:
- M87.7 delivery-gate integration.

Problem:
- linting the approximately 5.4k-line APF YAML can exceed 4 GB RAM in constrained environments;
- delivery gate currently supports an explicitly recorded `skipped_heavy_env` mode.

Scope:
- profile peak memory and runtime;
- identify graph/linter phases with excessive materialization;
- add bounded-memory fixtures and performance thresholds;
- remove the need for `--skip-heavy` on standard CI runners.

Closure requirement:
- full APF lint passes inside the declared CI memory budget without a heavy-test skip.


### BL-ORDO-026 — Independent Full Delivery-Gate CI Verification

Status: `open`

Priority: `high`

Origin:
- M87.7 selective integration closure.

Goal:
Run the complete integrated delivery gate on an unrestricted CI runner and bind the result to the integrated archive commit/build identity.

Required evidence:
- `python3 tools/build_release_archive.py --check-only` without `--skip-heavy`;
- full integrated test count and package lint results;
- CI job URL or immutable run identifier;
- commit SHA and archive SHA-256 binding.

Qualification:
- M87.7 integration is accepted through an owner-approved evidence waiver;
- this item verifies the integrated tree independently and removes the remaining release qualification.

### BL-ORDO-027 — ARF Deterministic Process Control Model

Status: `in_progress`

Priority: `high`

Origin:
- owner-approved intake from `ARF_MODEL_PROCESS_EXECUTOR_ONLY_IMPROVEMENT_INSTRUCTIONS_UK.md`;
- only general ARF process controls are accepted; Manual QA and domain-specific requirements are explicitly excluded.

Goal:
Make ARF generate playbooks as explicitly controlled executable contracts rather than recommendation-oriented text.

Accepted scope:
- explicit mutually exclusive runtime modes: execution, design, authorized maintenance;
- closed-world execution semantics for active executable nodes;
- node-type-specific allowlists, prerequisites, outputs, gates, transitions, forbidden actions, invalidation and authorization boundaries;
- explicit instruction precedence and prohibition on implicit transitions;
- blocking ambiguity route using `blocked_missing_instruction`;
- independent validation that cannot be self-declared by the artifact being validated;
- atomic-unit validation as a general principle for composite executable artifacts;
- negative regression cases against unauthorized editorial or creative model behavior.

Out of scope:
- Manual QA test-case structure;
- fixture-specific rules;
- endpoint-specific or History Event-specific behavior;
- creation of new fundamental anti-patterns without separate owner approval.

Closure requirement:
- control model schema and runtime contract implemented;
- ARF source and runtime bindings updated;
- backward compatibility and migration behavior defined;
- positive, negative and end-to-end tests pass;
- graph/documentation updated;
- closure report confirms no implicit mode transitions or unguarded executable actions.

Implementation plan:
- see `reports/BL_ORDO_027_ARF_DETERMINISTIC_CONTROL_MODEL_PLAN.md`.

### BL-ORDO-028 — Node-Local Deterministic Execution and Self-Contained Context Model

Status: `open`

Priority: `high`

Origin:
- owner concept captured during BL-ORDO-027 implementation;
- requires separate conceptual review before implementation.

Goal:
Re-evaluate the ARF architecture and current process around a strict node-local execution model in which the model is always anchored to one active node, can leave that node only through an explicit transition, and receives all execution knowledge through the active node contract plus explicit process state.

Core principles to review:
- exactly one active node controls the current execution focus;
- free-form discussion may occur, but it must not detach runtime state from the active node;
- moving to another concern requires an explicit transition to another node;
- each node has a bounded knowledge/context envelope;
- required knowledge is loaded through the node contract or current state, not assumed from conversational memory;
- nodes should behave like stateless functions receiving explicit context and producing explicit state/output;
- large trees must remain manageable because only node-local knowledge and required state are active at a given moment;
- improvements should be applicable locally to a node without forcing global prompt growth.

Questions for future review:
- whether this becomes a core ARF architectural invariant;
- how active-node anchoring is represented and enforced in runtime state;
- how temporary off-topic discussion is allowed without losing node control;
- what minimum self-contained context every node must declare;
- how context loading, state projection, transition validation and node resumption work;
- how to audit the current ARF graph for violations of these principles.

Out of scope for now:
- immediate mutation of the current graph;
- implementation before owner discussion and approval;
- packaging changes before the concept is accepted.


### BL-ORDO-029 — Inbound Transition Provenance Gate

Status: `open`

Priority: `high`

Recovery note: reconstructed from the accepted owner discussion on 2026-07-14.

Goal:
Require every node entry to prove that the immediately previous node is an allowed direct predecessor, and require the graph validator to verify both directions of every direct edge.

Required semantics:
- each node may declare `allowed_from` / `incoming_from` direct predecessor node IDs;
- on node entry, runtime checks `previous_node_id` against the inbound allowlist before the node action runs;
- an invalid predecessor blocks normal execution and starts transition-provenance diagnosis/recovery;
- validation concerns direct one-hop edges only, not transitive reachability through intermediate nodes;
- for every outbound edge `A -> B`, validator must confirm that `B` accepts `A` as a direct predecessor;
- for every inbound declaration `B.allowed_from += A`, validator must confirm that `A` contains a direct outbound edge to `B`;
- outbound-only, inbound-only, missing-node and indirect-path false-positive cases are blocking errors;
- root, resume, retry, recovery and migration transitions require explicit semantics and dedicated tests.

Planned deliverables:
- schema convention for inbound transition declarations;
- runtime node-entry provenance gate;
- bidirectional direct-edge semantic validator;
- diagnostics identifying source node, target node, direction and defect class;
- positive, negative and migration tests;
- documentation and book synchronization.

Relationship:
- extends BL-ORDO-028 node-local deterministic execution;
- implementation must not begin from this reconstructed archive without fresh baseline verification.

### BL-ORDO-032 — Hermetic and Non-Destructive Delivery Gate

Status: `closed_with_recovered_evidence`

Priority: `P0`

Recovered closure evidence:
- `DELIVERY_GATE_REPORT.json`;
- `reports/bl_ordo_032/BL_ORDO_032_CLOSURE_REPORT.json`;
- `reports/bl_ordo_032/BL_ORDO_032_CLOSURE_REPORT.md`.

Qualification:
The closure evidence is preserved, but the exact final source-tree mutation set and durable 477-node checkpoint were not fully recoverable in the active runtime. This reconstructed package therefore retains the closure record without claiming byte-identical restoration of the final BL-ORDO-032 canonical tree.
