# APF Release Hygiene and Clean Runtime Gate Improvement

## Purpose

This improvement defines a mandatory release hygiene and clean runtime validation layer for APF-style packages.

It is intended for two levels:

1. **Base APF / Ordo package-generation model** — as a general standard for any runtime-capable generated package.
2. **History Event Analysis Package Factory** — as a concrete process improvement to prevent debug/runtime leftovers from leaking into released analyst packages.

The goal is to ensure that a generated package is not only structurally complete, but also safe and clean to start by an analyst in a fresh session.

---

## Problem observed

During real use of `History Event Analysis Package Factory v0.8`, the analyst selected root path `1`, and the actual route itself was correct:

```text
ROOT_N1 answer=1 -> B1_N1
```

However, the runtime/helper layer produced confusing behavior:

- `next-step` surfaced a future draft-package gate during early intake.
- Debug-oriented evidence/checkpoint output leaked into the analyst-facing workflow.
- Runtime state/checkpoint logic appeared contaminated by previous test or generated state.
- The package behaved as if some later branch state had already been partially closed.

This is not merely a local one-off mistake. It is a recurring class of release risk for generated runtime packages:

```text
Temporary runtime evidence, test sessions, smoke-test artifacts, debug reports, stale compiled artifacts,
or schema-as-state mistakes can accidentally enter the release package or influence analyst startup.
```

---

## Required improvement summary

Add a mandatory hard gate before final package assembly:

```text
RELEASE_HYGIENE_AND_CLEAN_RUNTIME_GATE
```

This gate must prove that the package:

- starts from a clean runtime state;
- does not contain live session evidence from authoring or smoke tests;
- has synchronized source and compiled runtime targets;
- does not allow future package-generation gates to block early analyst intake;
- keeps CLI/debug evidence hidden from normal analyst-facing output unless explicitly requested;
- has a verified early analyst startup flow.

---

## Scope A — base APF / Ordo model improvement

### 1. Add a standard release hygiene gate

Every runtime-capable APF package should include a release-stage gate:

```text
RELEASE_HYGIENE_AND_CLEAN_RUNTIME_GATE
```

This gate should run after compile/validation and before archive assembly.

Recommended position:

```text
source model confirmed
-> compile runtime targets
-> verify targets
-> artifact validation
-> analyst-start smoke test in isolated temp copy
-> clean release runtime area
-> RELEASE_HYGIENE_AND_CLEAN_RUNTIME_GATE
-> final package composition gate
-> zip assembly
-> zip content verification
```

### 2. Gate responsibilities

The gate must check:

#### Clean runtime state

- No live runtime evidence from authoring/test sessions is included in the release runtime area.
- No stale state snapshots are included in the release runtime area.
- Session trace is either clean/init-only or explicitly documented as an empty starter trace.
- Smoke-test artifacts are stored outside live runtime paths, for example under `reports/` or `test_evidence/`.

#### Compiled runtime freshness

- Source model and compiled IR/view/manifest are synchronized.
- No `stale_ir` or equivalent status is present.
- Runtime status is `ready`.
- Verify-targets passes.
- Runtime entry resolves to the intended entry node.

#### Early analyst route correctness

The package must pass at least a minimal clean startup scenario:

```text
clean start -> ROOT_N0
ROOT_N0 answered -> ROOT_N1
ROOT_N1 valid choice -> expected branch node
next-step -> expected current node, not future gate/debug action
```

For packages with root branching, representative root paths should be tested.

At minimum:

- first open-text answer;
- first branch choice;
- one downstream question after branch routing.

#### Future gate isolation

Draft/final package gates must not block early intake nodes.

Examples of gates that must not run globally at startup:

- draft package required docs gate;
- final package composition gate;
- runtime compilation gate after runtime has already been packaged;
- generated artifact completeness gates before the generation node is reached.

These gates must be scoped to their owning node/stage.

#### Analyst-facing output discipline

Normal analyst mode must not expose raw debug output unless explicitly requested.

Forbidden in normal analyst-facing output:

- full checkpoint tables;
- raw evidence JSON;
- SHA256 evidence digests;
- compiled IR/view internals;
- filesystem paths to evidence unless the user asks for audit/debug details.

Allowed in normal analyst-facing output:

```text
Accepted.
Selected path: 1 — internal Mongo / EDR factography.
Next step: determine whether the event is new, existing, partially existing, or uncertain.
```

### 3. Required CLI support

The base APF CLI should provide or standardize these commands.

#### `clean-runtime`

Purpose: clean the release runtime area before packaging.

Should remove or reset:

```text
runtime/evidence/*
runtime/state_snapshots/*
live session traces
temporary intake reports
debug next-step reports
smoke-test runtime residue
```

Should preserve:

```text
runtime directory structure
starter runtime config
compiled runtime targets
README / START_HERE / START_PROMPT files
schema or templates needed for runtime startup
```

#### `release-hygiene`

Purpose: verify the release package directory before zip assembly.

Checks:

- no live runtime evidence;
- no live snapshots;
- no stale compiled artifacts;
- no backup/cache files;
- no `__pycache__`;
- no old-version graph/state files;
- no authoring scratch files;
- no unsupported mechanical gate syntax;
- no future gate blocking early intake;
- startup files exist and agree with runtime entry.

#### `analyst-start-smoke-test`

Purpose: validate the first analyst experience from a clean package.

Must run in an isolated temporary copy, not in the release directory that will be zipped.

Checks:

```text
runtime-status ready
runtime-entry ready
first node is expected
submit first node answer
next node is expected
submit representative branch answer
next node is expected
normal analyst output can be generated without raw debug leakage
```

#### `inspect-release-zip`

Purpose: validate the final zip itself after assembly.

Checks:

- no forbidden files are inside the zip;
- MANIFEST matches physical contents;
- checksums match;
- starter files exist;
- compiled runtime targets exist when package profile is runtime/hybrid;
- no old version artifacts are included.

---

## Scope B — History Event Analysis Package Factory improvement

### 1. Add the gate to the factory process

The History Event Analysis Package Factory should include a pre-archive hard gate:

```text
History Event Factory Release Hygiene & Clean Runtime Gate
```

This gate should run after:

- source YAML/model confirmation;
- graph projection/SVG regeneration;
- compile/verify targets;
- runtime startup smoke test;
- package composition validation.

And before:

- final zip assembly;
- final package download link publication.

### 2. Apply to History Event root paths

The smoke test should verify at least:

```text
ROOT_N0 answered -> ROOT_N1
ROOT_N1=1 -> B1_N1
ROOT_N1=4 -> B4_N1
ROOT_N1=5 -> B5_N1
```

Optional but recommended:

```text
ROOT_N1=2 -> B1_N1
ROOT_N1=3 -> B1_N2B
```

This ensures all root paths 1–5 are routable and no removed fallback path remains.

### 3. Analyst output expectation

For path 1, the analyst-facing output after selecting option `1` should be similar to:

```text
Accepted.
Selected path 1: internal Mongo / EDR factography for the main company.
Next step: is this historical event new, already existing, partially existing, or uncertain?
```

It must not display raw runtime evidence unless the analyst explicitly asks for audit/debug details.

### 4. Clean package rule

The released package must not include live files such as:

```text
runtime/evidence/LIVE-*.json
runtime/state_snapshots/SESSION-*.json
reports/next_step_after_*.json generated during authoring
reports/intake_submit_*.json generated during authoring
old v0.7/v0.8 state backups
__pycache__
*.bak
manual debug logs
```

If smoke-test evidence is preserved, it should live in:

```text
reports/
test_evidence/
verification/
```

and must be clearly marked as verification evidence, not live starter runtime state.

---

## Required validation checks

### Filesystem hygiene checks

- No forbidden runtime evidence files.
- No live snapshots.
- No backup/cache files.
- No stale version artifacts.
- No authoring scratch files.
- No test-created runtime files in release runtime directories.

### Runtime correctness checks

- `runtime-status` is ready.
- `runtime-entry` returns expected entry node.
- `verify-targets` passes.
- Source and compiled runtime artifacts are synchronized.

### Early route checks

- The first node is correct.
- ROOT_N0 answer advances to ROOT_N1.
- Every supported ROOT_N1 option routes to the expected next node.
- Removed/unsupported fallback options are rejected or clarified.
- Future gates do not block early intake.

### Gate scope checks

- Draft package gate only applies after draft generation node.
- Final package composition gate only applies at finalization stage.
- Program-level contract gate only applies before final package generation, not during first intake.
- Runtime compilation gate does not block analyst intake in an already compiled runtime package.

### Human-facing output checks

- Normal analyst mode is concise and human-readable.
- Raw evidence is hidden unless requested.
- Technical audit data is available but not pushed into the main conversation.

---

## Pass / fail criteria

### Pass

The gate passes only if:

- runtime starts cleanly;
- early analyst flow is verified;
- no release-forbidden files are present;
- source/compiled artifacts are synchronized;
- future gates are not evaluated prematurely;
- analyst mode output is human-first;
- final zip contents are clean.

### Fail / blocker

The gate must block release if:

- live evidence/snapshots are present in release runtime;
- `next-step` returns a future gate during early intake;
- `runtime-status` reports stale/invalid compiled targets;
- root path routing is wrong;
- debug output is the default analyst output;
- source and compiled artifacts are out of sync;
- old package version artifacts leak into the release.

---

## Recommended package-generation sequence

Use this sequence for all future APF runtime-capable packages:

```text
1. Confirm source model
2. Regenerate derived artifacts
3. Compile runtime targets
4. Verify compiled targets
5. Run artifact validation
6. Run analyst-start smoke test in isolated temp copy
7. Clean release runtime area
8. Run release-hygiene check
9. Run final package composition gate
10. Assemble zip
11. Inspect final zip contents
12. Publish package link only if all release gates pass
```

Important rule:

```text
Smoke tests must run in a temporary copy, not in the directory that will be zipped.
```

---

## Implementation notes

### Do not rely only on README

README can describe release cleanliness, but it cannot enforce it.

The release hygiene gate must be executable through CLI/helper validation.

### Do not rely only on model memory

The model should not manually remember to clean files. The packager or CLI must enforce cleanup and validation.

### Keep audit evidence, but separate it

Audit evidence is useful and should not be discarded blindly.

However, it must be separated from live release runtime state.

Recommended structure:

```text
reports/                          release reports
verification/                     verification evidence
test_evidence/                    optional smoke-test evidence
runtime/                          clean starter runtime only
```

---

## Relationship to node-level prompt registry improvement

This improvement complements the node-level prompt registry improvement.

Node-level prompt registry improves how the analyst is guided through individual nodes.

Release hygiene ensures that the packaged runtime starts cleanly and does not expose internal/debug state by accident.

Together they support the target behavior:

```text
human-first analyst process
strict deterministic validation
clean runtime release package
trace/debug available on request
```

---

## Priority

High.

This should be treated as a release-blocking improvement for any APF package claiming to be runtime-capable or hybrid runtime/source capable.

---

## Expected outcome

After this improvement, future packages should not repeat the v0.8 issue where:

- early analyst routing technically worked,
- but runtime helper output became confusing,
- future gates surfaced too early,
- and release/runtime directories contained or implied non-clean session state.

The package should instead start cleanly, guide the analyst simply, and keep strict runtime evidence available only as audit material.
