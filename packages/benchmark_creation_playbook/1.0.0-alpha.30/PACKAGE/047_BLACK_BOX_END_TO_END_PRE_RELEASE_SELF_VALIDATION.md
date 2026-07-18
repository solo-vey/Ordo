# BL-BENCH-047 — Mandatory Black-Box End-to-End Pre-Release Self-Validation and Run Evidence

**Status:** DONE  
**Priority:** Critical  
**Type:** Process enforcement / runtime / release gate  
**Depends on:** BL-BENCH-042, BL-BENCH-044, BL-BENCH-045, BL-BENCH-046

## Problem

Development-time checks can pass while a real external executor still cannot complete a canonical RUN. The attached RUN_02 package demonstrates that integrity, pre-flight and all available versioned regressions passed, but the generated Passport failed semantic validation and the Driver remained incomplete with no receipts, approvals or terminal state.

`BL-BENCH-045` validates a completed result package. It does not by itself prove that the released Playbook can autonomously create such a package under blind, black-box execution. A mandatory full execution campaign is therefore required before release.

## Objective

Make a blind black-box campaign over `RUN_01–RUN_05` a mandatory part of the Playbook release process. A package must not be released until the campaign has been executed automatically against the sealed candidate, all expected terminal outcomes have been proven, and immutable run evidence has been preserved.

## Required implementation

### 1. Sealed-candidate execution

The harness must operate on the final candidate ZIP as an external consumer. It must not import unpublished workspace state, reuse hidden chat facts or edit generated artifacts by hand.

### 2. Full five-RUN campaign

Execute all canonical `RUN_01–RUN_05` with neutral prompts and canonical inputs. Each RUN must have an explicit expected outcome contract: successful terminal route or intentional fail-closed/hard-stop route.

### 3. Real Driver-mediated validation

Every artifact validator result must be submitted through the actual Driver contract. The harness must verify:

- validation receipts;
- invalidation receipts;
- regeneration requests and acknowledgements;
- version-specific presentation;
- version-specific approvals;
- terminal recomputation;
- package release result.

### 4. Autonomous correction loop

On a point-correctable defect, create a new artifact/package revision through the canonical correction process, rerun validators and repeat the affected RUN. Manual mutation of a generated result to manufacture PASS is prohibited.

### 5. Authoritative-fact and cross-artifact audit

Before terminal acceptance, compare literals, identifiers, collections, states, timestamps, rules and expected side effects in all generated artifacts against selected-run authoritative inputs. Local validator PASS cannot override a cross-artifact mismatch.

### 6. Final-ZIP consumer verification

After each RUN is packaged, reopen the ZIP, verify checksums and manifests, inspect actual artifacts/evidence, rerun the result-package release gate and confirm that the archive is independently usable.

### 7. Preserved pre-release evidence

Create and deliver:

- five immutable archives: `RUN_01` … `RUN_05`;
- per-RUN execution report and terminal-state proof;
- campaign manifest and checksum list;
- neutral launch prompts;
- candidate package version and SHA-256 binding;
- summary of corrections made during validation;
- explicit marker `PRE_RELEASE_SELF_VALIDATION`, not canonical/user-confirmed benchmark evidence.

### 8. Fail-closed release gate

Release is blocked when any of the following applies:

- a required RUN was not executed;
- a positive RUN does not reach its required success state;
- a negative RUN does not stop at its required hard stop;
- any artifact validator or cross-artifact gate remains failed;
- Driver receipts, approvals or presented-version bindings are incomplete;
- correction-loop evidence is missing;
- final ZIP cannot be reopened or fails integrity/parity checks;
- run evidence archives are missing or not checksum-bound;
- the harness used hidden/manual corrections;
- required owner input is missing.

## Mandatory outputs

- `tools/run_black_box_pre_release_campaign.py`;
- machine-readable campaign policy and schema;
- five per-RUN evidence ZIPs;
- `BLACK_BOX_PRE_RELEASE_CAMPAIGN_REPORT.json`;
- `BLACK_BOX_PRE_RELEASE_CAMPAIGN_SUMMARY.md`;
- `SHA256SUMS.txt` covering the campaign;
- acceptance fixtures for success, correction, expected hard stop, stale facts, missing approvals and tampered final ZIP;
- release-gate integration that blocks handoff without campaign PASS.

## Acceptance criteria

1. All five canonical RUNs are executed against the sealed candidate ZIP.
2. No generated artifact is manually edited outside the canonical correction loop.
3. Validator outputs flow through the actual Driver and produce traceable receipts.
4. Positive and negative expected terminal routes are checked separately.
5. Cross-artifact selected-run fidelity is machine-validated.
6. Every final result ZIP is reopened and revalidated.
7. Five downloadable run-evidence archives are produced and checksum-bound.
8. A failed campaign blocks package release.
9. A point correction triggers a new revision and rerun, not silent mutation.
10. The harness stops transparently when owner input is genuinely required.
11. The campaign evidence is clearly separated from canonical/user-confirmed benchmark evidence.
12. The supplied RUN_02 incident is reproduced as a negative regression fixture and cannot be misclassified as a releasable success.

## Source evidence

- `backlog_attachments/BL-BENCH-047/ORDO_RUN_02_NO_CHANGE_RETURN.zip`
- SHA-256: `4f1f9d6c7069a9626e03adac49544acd9e57c4ab2165a5005704c2ff2c4f7793`
- `backlog_attachments/BL-BENCH-047/OWNER_REQUIREMENT_AND_INCIDENT_CONTEXT.md`


## Closure
Implemented deterministic sealed-candidate external harness, five evidence archives, correction-loop regression, expected hard-stop proofs, campaign checksum binding and release gate. External LLM inference is not claimed.
