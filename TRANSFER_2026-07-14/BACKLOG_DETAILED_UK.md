# Детальний backlog ORDO / ARF — transfer snapshot 2026-07-14

## Як читати статуси

Цей файл не переписує історичні canonical records. Він додає transfer-level оцінку:
- `DONE` — у доступних artifacts є closure/current-state evidence;
- `OPEN` — явно відкрито;
- `PARTIAL` — робота була, але scope не закрито;
- `REVALIDATE` — старий backlog може суперечити пізнішому maturity evidence;
- `RECOVERED-CLOSURE` — closure evidence є, exact final source tree не відновлено.

## Найважливіше зараз

### BL-ORDO-032 — RECOVERED-CLOSURE
Hermetic and Non-Destructive Delivery Gate.

У діалозі закрито з evidence 477/477 nodes, 4/4 lints, blocking=0. Після втрати workspace exact source delta і checkpoint не відновлено. **Не переробляти концепцію з нуля; відновити source implementation за closure evidence/history і повторити full gate.**

Related files:
- `closure_evidence/DELIVERY_GATE_REPORT.json`
- `closure_evidence/BL_ORDO_032_CLOSURE_REPORT.json`
- `closure_evidence/BL_ORDO_032_CLOSURE_REPORT.md`
- `recovery_evidence/RECOVERY_STATUS_UK.md`
- `recovery_evidence/RECOVERY_GAPS.json`

### BL-ORDO-029 — OPEN / NEXT
Inbound Transition Provenance Gate.

Потрібно:
1. canonical inbound predecessor field/contract;
2. schema;
3. runtime entry gate;
4. direct-edge bidirectional validator;
5. mismatch taxonomy: outbound-only, inbound-only, missing node, illegal predecessor;
6. root/resume/retry/recovery/migration policy;
7. state/trace evidence for predecessor provenance;
8. negative fixtures;
9. regression suite;
10. APF compatibility migration;
11. docs/book sync;
12. closure gate.

### BL-ORDO-028 — STATUS UNCERTAIN / RECONCILE
Node-Local Deterministic Execution and Self-Contained Context Model.

У package backlog він `open`. У діалозі перед BL-ORDO-032 була велика послідовність робіт: runtime enforcement, explicit transition protocol, context-size isolation, disk state, independent validation, regression suite, ARF node-local audit, APF compatibility migration, book sync, closure/full partitioned run. Через втрату точного workspace не можна автоматично підняти статус до DONE. Потрібен evidence reconciliation.

## Canonical recovered backlog snapshot

| ID | Recovered canonical status | Title |
|---|---|---|
| BL-ORDO-001 | in-progress-evidence-reconciliation | CSG production recommendation closure |
| BL-ORDO-002 | open | APF graph cycles and dead-end paths |
| BL-ORDO-003 | closed | Safe runtime execution of generated real-module testcases |
| BL-ORDO-004 | open | Backlog and maturity-state synchronization |
| BL-ORDO-005 | open | Cross-model and repeated-run CSG benchmark |
| BL-ORDO-006 | open | PathWalk score calibration and benchmark purpose |
| BL-ORDO-007 | future-design | First-class flow reuse semantics |
| BL-ORDO-008 | deferred-owner-decision | APF real-case replay and analyst-experience validation |
| BL-ORDO-009 | deferred-owner-decision | APF internal mini-prompt applicability review |
| BL-ORDO-010 | active-paused-for-apf-improvement | Translation completion and synchronization |
| BL-ORDO-011 | needs-revalidation | Prompt Registry follow-up reconciliation |
| BL-ORDO-012 | needs-revalidation | Startup/package profile and derived-artifact hardening reconciliation |
| BL-ORDO-013 | future-candidate | Generic template and review tooling |
| BL-ORDO-014 | in-progress | APF post-generation defect review for critical artifacts |
| BL-ORDO-015 | open | Release and CI Closure |
| BL-ORDO-016 | closed-M85.5 | Current-tree packaging self-check |
| BL-ORDO-017 | closed-M86.5 | Benchmark Evidence Hardening |
| BL-ORDO-018 | closed-qualified | CLOSED at M87.6 |
| BL-ORDO-020 | closed | CLOSED at M88.5 |
| BL-ORDO-021 | closed | CLOSED at M89.5 |
| BL-ORDO-022 | blocked | GitHub CI Closure for BL-ORDO-015 |
| BL-ORDO-023 | open | Strict-Zero A/B Benchmark Revalidation |
| BL-ORDO-024 | open | Process Pattern Engineering |
| BL-ORDO-025 | open | APF Linter Memory and Performance Hardening |
| BL-ORDO-026 | open | Independent Full Delivery-Gate CI Verification |
| BL-ORDO-027 | closed_recovered_baseline | ARF Deterministic Process Control Model |
| BL-ORDO-028 | open | Node-Local Deterministic Execution and Self-Contained Context Model |
| BL-ORDO-029 | open | Inbound Transition Provenance Gate |
| BL-ORDO-032 | closed_with_recovered_evidence | Hermetic and Non-Destructive Delivery Gate |

## Transfer-level уточнення по ключових пунктах

- BL-ORDO-001: canonical JSON каже `in-progress-evidence-reconciliation`, але maturity docs мають пізніше CSG production-ready evidence. `REVALIDATE`.
- BL-ORDO-002: canonical backlog каже open, але CURRENT_MATURITY_STATE каже APF graph cycle/dead-end validation complete. `REVALIDATE`.
- BL-ORDO-004: canonical backlog каже open, але CURRENT_MATURITY_STATE каже backlog/maturity synchronization complete; у BL-ORDO-032 також був sync fix. `REVALIDATE`.
- BL-ORDO-005: canonical backlog каже open, але current maturity каже repeated cross-model benchmark complete. `REVALIDATE`.
- BL-ORDO-006: open; PathWalk calibration.
- BL-ORDO-007: future-design; first-class flow reuse semantics.
- BL-ORDO-008/009: deferred owner decision.
- BL-ORDO-010: paused/partial translation synchronization; later BL-ORDO-027 book sync may cover part, must reconcile.
- BL-ORDO-011/012: needs revalidation.
- BL-ORDO-013: future candidate.
- BL-ORDO-014: in-progress; critical artifact post-generation defect review.
- BL-ORDO-015: open, dependent on CI evidence.
- BL-ORDO-016: DONE M85.5.
- BL-ORDO-017: DONE M86.5.
- BL-ORDO-018: DONE qualified M87.6.
- BL-ORDO-020: DONE M88.5. Its reference anti-pattern corpus is preserved in `antipattern_reference_pack/`.
- BL-ORDO-021: DONE M89.5.
- BL-ORDO-022: blocked; GitHub CI closure dependency.
- BL-ORDO-023: open; Strict-Zero A/B benchmark revalidation.
- BL-ORDO-024: open; Process Pattern Engineering.
- BL-ORDO-025: open; APF linter memory/performance hardening.
- BL-ORDO-026: open; independent full delivery-gate CI verification.
- BL-ORDO-027: DONE as recovered baseline; deterministic process control and book sync.
- BL-ORDO-028: evidence reconciliation required.
- BL-ORDO-029: OPEN and next planned task.
- BL-ORDO-032: RECOVERED-CLOSURE; exact source restoration required before claiming new canonical baseline.

## Backlog governance warning

`CONSOLIDATED_BACKLOG.md`, `manifests/CONSOLIDATED_BACKLOG.json` і `CURRENT_MATURITY_STATE.*` мають відомі status drifts. Не брати один файл ізольовано. Перед новим closure потрібно виконати backlog reconciliation і supersession update.
