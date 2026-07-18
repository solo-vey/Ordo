# Repository Language Policy

## Rule

All repository files must be written in English.

## Sole Documentation Exception

The Ukrainian edition of the Ordo book may be maintained only as a translation of the authoritative English edition.

The Ukrainian book:

- must correspond to an English source chapter or section;
- must not introduce independent normative requirements;
- must not become the source of truth for language, framework, runtime, schema, evidence, or release behavior;
- must be updated when the English source changes.

## Immutable Raw Evidence Exception

Immutable raw evidence may contain source-language material when translation would alter the evidence or invalidate its checksum.

Such material must remain in the raw-evidence area, retain its original SHA-256, and be accompanied by an English inventory, normalized record, or exception report.

## Enforcement

Non-English files outside the Ukrainian book translation and immutable raw evidence must be rejected or corrected before merge.
