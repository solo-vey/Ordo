# BL-ORDO-058 Classification Plan

Status: `open — classification rules established; remediation not started`

## Purpose

This plan turns the Ukrainian-text inventory into explicit treatment rules.
It does not translate, delete, relocate, regenerate, or modify archived
payloads. Each later remediation change must stay within one treatment group
and update references, manifests, checksums, and generated outputs where
applicable.

## Audit snapshot

The archive-aware audit ran against Git baseline
`42d5a161a00842afff5886bf03c2a64b0fcd8e90` with `book/**` excluded.

| Measure | Result |
| --- | ---: |
| Git-tracked files scanned | 3,940 |
| Intentionally excluded book files | 314 |
| Archive sources inspected | 90 |
| Ukrainian-text locations | 1,805 |
| Audit warnings | 0 |

The earlier inventory records 1,889 locations. The lower current total is an
expected consequence of historical-payload externalization; it is not a
claim that remaining active text was already remediated.

## Scope split

BL-ORDO-058 now owns the 248 findings in physical Git-tracked files. Its
remediation can be reviewed, tested, and reverted as ordinary source changes.
The remaining 1,557 findings are archive members and now belong to
BL-ORDO-062. They are deferred because an archive-member change is an
artifact migration, not an ordinary text edit.

## Treatment rules

| Contour | Current audit footprint | Canonical treatment |
| --- | --- | --- |
| `book/**` | excluded | Preserve as intentional Ukrainian book content. |
| `COMMERCIAL_LICENSE.md`, `NOTICE.md`, and license-name references | 2 root locations | Preserve legal proper names and approved license wording. |
| `archive/**`, historical reports, checkpoints, and externalized provenance | historical payload | Preserve; do not rewrite for language cleanup. |
| `empirical_evidence/**` | 1,463 locations, mostly archive members | Preserve as immutable evidence; any replacement requires a separately approved evidence migration. |
| Test fixtures and language-behaviour examples | fixture payload | Preserve when Ukrainian is the tested input or expected output; document the exemption. |
| Generated package outputs and compiled/runtime artifacts | derived payload | Regenerate from a remediated source; never hand-edit the derived copy. |
| Active documentation, package source, templates, prompts, CLI user-facing text, and utility user-facing text | active payload | Translate to English unless an explicit localized-content boundary is approved. |
| Localized APF rationale under `docs/apf/legacy-root/uk/` | 1 localized document | Preserve under the existing explicit policy exemption until its active references are retired. |

## Ordered remediation waves

1. Classify and exempt immutable, legal, fixture, and localized contours in
   policy and test coverage without altering their payload.
2. Translate active front-door documentation and CLI/template user-facing
   text, then repair links and documentation contracts.
3. Translate active package, integration, and language source material; use
   their canonical builders to regenerate derived artifacts.
4. Re-run the archive-aware audit, compare the remaining findings with the
   explicit exemptions, and record the justified localization boundary.

### Wave 1 record

The first physical-file wave translates seven short active documentation and
CLI guidance files. It reduces the physical-file audit from 248 to 241
findings without changing archives, evidence, fixtures, legal text, or
localized content.

## Safety conditions

- No archive member, checkpoint, empirical-evidence payload, or historical
  record is rewritten by this backlog item without a separate migration.
- Each wave is a separate pull request with focused tests and a clean
  checksum manifest.
- The English-only migration policy is tightened only after a contour has
  been translated, regenerated, and validated.
