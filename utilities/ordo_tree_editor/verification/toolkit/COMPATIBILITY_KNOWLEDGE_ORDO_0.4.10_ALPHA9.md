# Ordo 0.4.10 ↔ Vibe ARF alpha.9 compatibility knowledge record

Status: **ACTIVE KNOWLEDGE / DO NOT DISCARD**  
Purpose: preserve compatibility findings discovered while building the self-contained Vibe ARF `0.1.0-alpha.9`, so future repository integration or Ordo upgrades do not require rediscovering the same failures.

This file is descriptive evidence, not a new Ordo language specification. Where a local repair exists, it is explicitly marked as a compatibility override and must be re-evaluated against the next canonical Ordo package before removal.

## Compatibility matrix

| ID | Area | Observed symptom | Root cause | alpha.9 repair | Repository / next-version action |
|---|---|---|---|---|---|
| C01 | Gate schema | Language/schema validation could disagree with compiler/runtime about gate condition field. | The pinned package had a schema layer that required/expected `assert` while canonical examples, compiler and runtime used `condition`. User confirmed `condition` is the intended canonical field. | Use the documented `0.4.10_LOCAL_CONDITION_OVERRIDE`; gate schema requires `condition`. | Fix canonical language package so schema, compiler, runtime, examples and editor all use one field. On upgrade, compare hashes and remove local override only after a clean canonical regression. |
| C02 | Embedded language mirror | CLI/editor rejected constructs that the canonical root language registry accepted; different tools could interpret the same playbook differently. | `language/` and `cli_embedded/language/` inside the kit had drifted. The root registry included constructs missing from the embedded mirror (including constructs relevant to `playbook_laws` / `graph_contract` / `artifact_sync`). | Materialize canonical root `language/` and mirror it byte-for-byte into `cli_embedded/language/`. See `portable_overrides/ORDO_0.4.10_EMBEDDED_LANGUAGE_MIRROR_SYNC.json`. | Repository should have one generated/verified language truth, not two independently maintained copies. Add CI hash-equivalence check between root and embedded mirrors. |
| C03 | `graph_contract` registry alignment | A freshly generated Ordo package could fail its own lint/compile path because registry/opcode catalogs did not recognize what `ordo init` and compiler emitted. | `ordo init` emits `graph_contract`; compiler emits `GRAPH.CONTRACT`; pinned registry/opcode catalogs omitted alignment. | Local registry-only alignment; no new executable semantics. See `portable_overrides/ORDO_0.4.10_GRAPH_CONTRACT_REGISTRY_ALIGNMENT.json`. | Fix registry/opcode catalogs in canonical repo and add regression: `ordo init → lint → compile` must pass on a clean generated package. |
| C04 | Portable utility layout / Tree Editor | Tree Editor failed to start/import Ordo (`ModuleNotFoundError: No module named 'ordo'`) when utilities were copied under an extra wrapper directory. | Utility code derives repository root from its own relative location and assumes canonical layout. Moving executable utilities under `canonical_support/utilities/...` changed that invariant. | Keep executable utilities at canonical root-relative paths (`utilities/...`), while provenance/support copies may live separately. | Either document layout as an explicit contract or make utilities discover repo/package roots robustly via config/environment rather than fixed parent traversal. Add relocation test. |
| C05 | Tree Editor strict validation | Editor reported `STRICT_REQUIRES_TESTS` even though package-local `tests/test_cases.yaml` existed. | Editor validator passed an unconditional empty test set to strict linter instead of discovering real package tests. | Load `tests/test_cases.yaml` when present; use empty fallback only when genuinely absent. See `portable_overrides/ORDO_TREE_EDITOR_REAL_TEST_DISCOVERY.json`. | Fix upstream editor; add strict-playbook editor regression with real tests. |
| C06 | Visual graph generator | Valid external terminal transition was rendered/validated as `UNKNOWN_TARGET`; editor/graph path could fail while canonical graph validator passed. | Visual graph utility ignored `graph_contract.external_terminal_targets`. | Utility now synthesizes declared external terminal targets instead of treating them as missing. See `portable_overrides/ORDO_GRAPH_EXTERNAL_TERMINAL_ALIGNMENT.json`. | Align visualizer with canonical graph-contract semantics upstream and share graph-target resolver rather than duplicate logic. Add external-terminal fixture. |
| C07 | Static provenance test drift | A static test failed after hardened gate-provenance changes even though source behavior was intentional. | Test expected selected UX/authoring gates to remain `mechanical/deterministic`; hardened model correctly classifies model-owned judgments as `self_verification/model_judgment` to avoid determinism laundering. | Keep hardened source; update stale test expectation. | Repository tests should assert provenance semantics, not historical trust labels. Add negative test preventing model-written status from satisfying deterministic gate claims. |
| C08 | Package manifest mutability | Re-running verifier caused immutable hash drift in the same package. | Root manifest hashed mutable generated verification/report artifacts that the verifier itself rewrites. | Immutable hash domain excludes runtime/reports; those are marked mutable evidence. | Formalize immutable vs mutable package domains in repository packaging contract and test idempotent verification. |
| C09 | Workspace/source-of-truth selection | A later-by-mtime alpha.8 working copy failed provenance/grounding and even carried older metadata, risking alpha.9 being built on a semantically stale branch. | Multiple workspace copies existed; newest timestamp was not a reliable source-of-truth selector. | Rebase alpha.9 on the hardened `vibe_alpha8_latest` source proven by gate-provenance and Ordo-grounding checks, then layer newer policies explicitly. | Repository must use revision/hash/checkpoint identifiers, never directory mtime/name, to select baseline. Add a single current-baseline manifest/reference. |
| C10 | Full regression routing | Old full-suite paths could test root `Playbook/source` instead of the intended candidate revision, giving misleading failures/pass results. | Some regression tooling is root-path implicit rather than revision-explicit. | Candidate verification is package/revision-explicit; do not claim full regression from a run that targeted another root. | Make every regression invocation accept/record explicit revision/root SHA. Fail if tested source hash does not equal requested candidate hash. |
| C11 | Verification performance | `test_alpha8_authoring_verification_modes` became a major hotspot and exceeded 45 s during integration. | Test repeatedly spawned overlapping FAST/VERIFY subprocess contours. | Reduced redundant work; quick authoring preflight consolidates common compatibility checks. | Continue refactoring regression harness to reuse compiled/lint results and cache immutable checks. Track per-module duration and treat fast-contour growth as DX regression. |
| C12 | Compiled artifact portability | Re-running compile after extracting the same package to another path changed hashes under `compiled/*`, causing package-integrity failure. | Compiled artifacts are derived and may encode/materialize context that is not stable across extraction locations. | Exclude `compiled/*` from portable immutable hash domain; regenerate/verify them from immutable source during preflight. | Decide upstream whether compiled IR must be fully path-independent/reproducible. If yes, remove path/context dependence and add cross-directory reproducibility test; otherwise declare compiled output derived/mutable in package contract. |

## Canonical evidence and local repair files

The alpha.9 package keeps explicit machine-readable repair records:

- `canonical_support/provenance/LOCAL_OVERRIDE_PROVENANCE.json` — user-authorized `gate.condition` alignment provenance.
- `portable_overrides/ORDO_0.4.10_EMBEDDED_LANGUAGE_MIRROR_SYNC.json` — root vs embedded language mirror synchronization.
- `portable_overrides/ORDO_0.4.10_GRAPH_CONTRACT_REGISTRY_ALIGNMENT.json` — `graph_contract` / `GRAPH.CONTRACT` registry alignment.
- `portable_overrides/ORDO_TREE_EDITOR_REAL_TEST_DISCOVERY.json` — real strict test discovery in editor.
- `portable_overrides/ORDO_GRAPH_EXTERNAL_TERMINAL_ALIGNMENT.json` — visualizer external-terminal support.

## Required checks when integrating into the main repository

Do not simply copy the alpha.9 patches upstream. For each compatibility item:

1. Check the current canonical Ordo version first.
2. Reproduce the original failure against unmodified canonical sources.
3. If already fixed upstream, remove the corresponding local override and run the same regression.
4. If still present, fix the canonical source/tooling layer rather than maintaining a Vibe-only fork where possible.
5. Run at minimum:
   - root vs embedded language mirror equality;
   - clean `ordo init → lint → compile`;
   - strict Tree Editor validation with package-local tests;
   - graph render with `external_terminal_targets`;
   - gate-provenance audit;
   - package verification twice to prove idempotence;
   - revision/hash-explicit regression routing.
6. Record canonical version, source hashes and removal/retention decision for every override.

## Upgrade rule

A newer Ordo package must **not** be assumed compatible merely because its version is higher. Compare these compatibility items one by one. Local overrides may be deleted only when the newer canonical package independently passes the regression that originally justified the override.
