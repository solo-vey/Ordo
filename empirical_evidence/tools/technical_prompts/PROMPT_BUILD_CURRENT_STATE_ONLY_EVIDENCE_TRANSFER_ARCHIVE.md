# Prompt: Build a Current-State-Only Ordo Evidence Transfer Archive

You are preparing an Ordo empirical evidence archive for transfer and integration.

Your task is to create a **current-state-only evidence snapshot** from the supplied source evidence archive.

The output archive must contain only the latest accepted, approved, and currently authoritative evidence artifacts. Historical versions, superseded runs, intermediate packages, rejected variants, and duplicated version history must not be included.

## 1. Primary objective

Create a compact transfer archive that represents the **current accepted state of the evidence base**.

The archive is intended for:

- transfer to another Ordo environment;
- integration into the current language/framework package;
- current-state evaluation;
- present-day validation and audit;
- canonical release preparation.

The archive is **not** intended to preserve development history.

## 2. Core retention rule

For every logical artifact family, retain only the latest authoritative item.

Examples:

- latest approved playbook version;
- latest accepted run for each required model/scenario/condition;
- latest approved instruction package;
- latest Driver version;
- latest evaluator/scoring profile;
- latest normalized case record;
- latest accepted scorecard;
- latest current manifest;
- latest current evidence package;
- latest applicable schema and validator.

If multiple files represent the same logical artifact, select the one explicitly marked as:

1. current;
2. accepted;
3. approved;
4. canonical within the evidence source;
5. latest by semantic version or authoritative manifest.

Do not use file modification time as the only selection criterion.

## 3. Remove all historical material

Exclude:

- previous playbook versions;
- previous instruction-package versions;
- version-history directories;
- historical patch packages;
- superseded or withdrawn artifacts;
- rejected runs;
- failed runs unless the current evidence claim explicitly depends on them;
- dry runs;
- self-check runs;
- development-only runs;
- duplicate reruns that are not the current accepted run;
- obsolete scorecards;
- obsolete evaluator profiles;
- intermediate generated artifacts;
- temporary files;
- backup files;
- `.bak`, `.tmp`, `.old`, `.orig`;
- `__pycache__/`;
- `.pyc` files;
- local workspaces;
- build caches;
- transcript sandboxes;
- duplicated extracted copies of an archive when the exact archive is already retained and extraction is not required for validation.

Do not include historical files merely because they are referenced by an old README or legacy manifest.

## 4. Run selection rules

For each required test condition, scenario, model, or implementation variant:

- retain only the latest accepted run;
- retain the run's final artifacts;
- retain its final scorecard;
- retain its final audit or evaluation result;
- retain the exact playbook/instruction package identity used by that run;
- retain the model and evaluator identity;
- retain the accepted terminal state;
- retain required provenance and SHA-256 values.

Exclude:

- prior attempts;
- failed attempts;
- abandoned attempts;
- dry/self-check attempts;
- intermediate correction cycles;
- duplicate copies of the same accepted run;
- runs replaced by a later accepted run.

If a prior run is necessary to support a regression comparison that is part of the current bounded claim, retain only the minimum comparison record, not the complete historical package, and document the exception.

## 5. Playbook and instruction-package selection

For each implementation condition, retain only:

- the latest approved playbook or instruction package;
- the latest compatible Driver;
- the latest required templates and contracts;
- the latest validator set;
- the exact package used for the retained accepted runs.

Exclude all earlier full-package versions.

Do not retain seven or eight complete historical packages when one current approved package is sufficient.

If the latest accepted run used a version older than the latest available package, preserve the exact run-used package and clearly distinguish:

- `latest_available_version`;
- `accepted_run_bound_version`.

Do not silently substitute a newer package for the package actually used in evidence.

## 6. Source archive versus extracted content

Avoid storing the same evidence twice.

For each source package, choose one of these patterns:

### Pattern A — archive retained

Retain the immutable source ZIP plus:

- SHA-256;
- size;
- provenance;
- content inventory;
- current-state selection manifest.

Do not also retain a complete extracted duplicate unless validators require direct files.

### Pattern B — extracted current files retained

Retain only the required current extracted files plus:

- original source archive SHA-256;
- source package identity;
- extraction manifest;
- per-file SHA-256.

Do not also retain redundant historical archives.

### Pattern C — both required

Retain both only when:

- exact raw-package preservation is required; and
- direct extracted files are required by validators or consumers.

If both are retained, document the duplication explicitly in the archive manifest.

## 7. Immutable evidence protection

Never alter immutable raw evidence.

Do not:

- translate raw evidence;
- normalize it in place;
- rename internal files if that changes the evidence package;
- remove files from an immutable source ZIP;
- recompress an accepted source ZIP and present it as the original;
- modify timestamps or metadata inside source archives.

When raw evidence contains non-English or legacy content, preserve it unchanged and provide a separate English inventory or normalized record.

## 8. Required output structure

Use a compact structure similar to:

```text
CURRENT_EVIDENCE_TRANSFER/
├── README.md
├── CURRENT_STATE_MANIFEST.json
├── SELECTION_REPORT.json
├── EXCLUSION_REPORT.json
├── LANGUAGE_AUDIT.json
├── SHA256SUMS.txt
├── schemas/
├── cases/
├── accepted_runs/
├── scorecards/
├── findings/
├── claims/
├── admissions/
├── current_packages/
├── raw_evidence/
└── tools/
```

Only create directories that are actually needed.

## 9. Current-state manifest

`CURRENT_STATE_MANIFEST.json` must identify:

- dataset version;
- transfer version;
- creation date;
- source archive filename;
- source archive SHA-256;
- selection policy;
- retained test cases;
- retained implementation conditions;
- retained accepted runs;
- retained playbook/instruction versions;
- retained scoring profile;
- retained schemas;
- retained raw evidence packages;
- total retained files;
- total retained size;
- excluded historical file count;
- excluded historical size;
- known limitations.

## 10. Selection report

`SELECTION_REPORT.json` must record, for every artifact family:

- logical artifact ID;
- candidates found;
- selected current artifact;
- selection reason;
- version comparison;
- accepted/approved status;
- run binding;
- SHA-256;
- excluded alternatives.

The report must make it possible to understand why a file was retained or removed.

## 11. Exclusion report

`EXCLUSION_REPORT.json` must summarize excluded content by category:

- historical playbook versions;
- historical instruction packages;
- superseded runs;
- rejected runs;
- dry/self-check runs;
- duplicate archives;
- duplicate extracted copies;
- generated caches;
- temporary files;
- obsolete scorecards;
- obsolete manifests;
- other historical material.

For each category include:

- file count;
- total size;
- representative paths;
- exclusion rationale.

Do not include the excluded bytes in the transfer archive.

## 12. Language requirements

All newly created text documents, manifests, reports, normalized records, and instructions must be written in English.

Allowed exceptions:

- immutable raw evidence;
- source-language files whose modification would invalidate evidence identity.

Every exception must be listed in `LANGUAGE_AUDIT.json`.

## 13. Checksum requirements

Before building the final ZIP:

1. finish all file selection;
2. finish all reports and manifests;
3. validate all JSON/YAML files;
4. verify all retained source archives;
5. generate `SHA256SUMS.txt` last;
6. freeze the staging directory;
7. build the ZIP;
8. calculate the ZIP SHA-256;
9. unpack the ZIP into a clean directory;
10. verify every checksum again.

If a source package already has an authoritative SHA-256, preserve and verify it.

If any retained archive is modified, it must be treated as a new derived archive with a new SHA-256. Never reuse the original checksum.

## 14. Validation requirements

The final archive must pass:

- ZIP integrity check;
- internal checksum verification;
- JSON syntax validation;
- YAML syntax validation;
- no duplicate logical run IDs;
- no superseded run marked as current;
- no more than one current approved package per logical condition, except explicitly documented run-bound exceptions;
- no historical/version-history directories;
- no `__pycache__` or `.pyc`;
- no temporary or backup files;
- English-language audit for all newly created documents;
- accepted-run count reconciliation;
- scorecard-to-run binding;
- playbook/instruction-package-to-run binding;
- model/evaluator identity validation;
- bounded-claim validation.

## 15. Fail-closed rules

Stop and report `BLOCKED` if:

- the latest accepted artifact cannot be identified;
- two artifacts claim to be current without a documented precedence rule;
- an accepted run cannot be bound to its exact package version;
- checksums do not match;
- source provenance is missing;
- removing a historical artifact would invalidate a current claim;
- the output would silently change evidence meaning;
- current accepted runs are incomplete.

Do not guess.

## 16. Required final report

Return:

- output ZIP filename;
- output ZIP SHA-256;
- retained file count and size;
- excluded file count and size;
- retained accepted run count;
- retained current package versions;
- removed historical package count;
- validation results;
- language-audit result;
- known limitations;
- explicit statement:

```text
This archive is a current-state-only evidence snapshot.
Historical development packages and superseded runs are intentionally excluded.
```

## 17. Important interpretation rule

“Latest” does not simply mean the highest filename or newest filesystem timestamp.

The selected artifact must be the latest **authoritatively accepted or approved** artifact according to:

- current manifest;
- acceptance record;
- approval record;
- run index;
- release binding;
- semantic version;
- explicit current-state declaration.

Preserve the evidence needed to prove the current state, but do not preserve the complete path used to reach it.

