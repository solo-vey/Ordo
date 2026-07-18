# Ordo Language Improvement Integration Pack — M64 Prep

Generated: 2026-07-09T18:10:00+02:00  
Status: `planning-package / not-applied-to-language-runtime`  
Target: Ordo language package after APF `v0.1.0-rc.4-post-svg`  
Purpose: preserve and order language-level improvements discovered while building APF.

## What this package is

This is a **language improvement integration pack**, not an applied APF runtime release.

It captures improvements that should be considered for the Ordo language package itself:

```text
program-level metadata
interaction semantics
process rail policy
hybrid execution model
runtime/package profile gates
derived artifact synchronization
SVG/graph artifact conventions
delta backlog preservation
future flow join / shared tail semantics
real-module testcase generation support
```

## Why it exists

During APF creation, several patterns became stable enough to preserve outside the current APF package. Some are still APF-local. Some are candidates for language-level schema conventions, lint checks, package standards, or future IR constructs.

This pack prevents those ideas from being lost while APF implementation continues.

## Read order

1. `SUMMARY.json`
2. `LANGUAGE_IMPROVEMENT_BACKLOG.md`
3. `APF_TO_LANGUAGE_PATTERN_MAPPING.md`
4. `PROPOSED_LANGUAGE_PATCH_SEQUENCE.md`
5. `PROGRAM_LEVEL_CONTRACT_LANGUAGE_NOTE.md`
6. `VALIDATION_REQUIREMENTS.md`
7. `reports/VALIDATION_REPORT.json`

## Key boundary

Do **not** promote every APF pattern directly into runtime opcodes.

Promotion ladder:

```text
observed APF need
→ documented APF pattern
→ reusable APF subflow / state convention
→ used by more than one package
→ lint/check candidate
→ formal language construct
→ IR/runtime object only when necessary
```

## Next APF step remains separate

The next APF implementation step can still be:

```text
FUTURE-PROGRAM-CONTRACT-01 — program-level metadata, interaction semantics and approval gates
```

This language pack simply gives the broader Ordo language line a clean backlog to absorb the same discoveries later.
