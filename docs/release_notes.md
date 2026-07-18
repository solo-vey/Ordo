# Release notes generator

`ordo generate-release-notes` is the M16 command that turns a controlled `release_diff_report.json` into a human-readable Markdown release note.

It does not infer changes from arbitrary files. It only summarizes the release diff generated from release provenance.

## Usage

```bash
ordo validate-release packages/history_event_guided_intake
cp packages/history_event_guided_intake/reports/release_provenance.json \
  packages/history_event_guided_intake/reports/release_provenance_base.json
ordo diff-release packages/history_event_guided_intake \
  --base packages/history_event_guided_intake/reports/release_provenance_base.json
ordo generate-release-notes packages/history_event_guided_intake
```

The command writes:

```text
reports/release_notes.md
reports/release_notes_report.json
```

## What it summarizes

- package/toolchain metadata changes;
- source file changes;
- lockfile changes;
- compiled IR changes;
- runtime trace/state changes;
- generated output changes;
- report changes;
- reproducibility status against the selected base.

## Important rule

Release notes are derived artifacts. They are not a source of truth. The source of truth is the provenance/diff chain:

```text
release_provenance.json → release_diff_report.json → release_notes.md
```
