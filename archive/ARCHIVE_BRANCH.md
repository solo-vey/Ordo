# `archive/legacy` branch contract

`archive/legacy` is the single archival branch for retired Ordo payloads other
than historical books, which remain on `archive/books`.

It preserves:

- `archive/legacy_packages/` — compatibility and release-provenance snapshots;
- `archive/legacy_utilities/` — retired standalone utilities;
- `archive/milestone_reports/` — immutable historical validation and closure
  reports; and
- `archive/backlog_history/` — retired Markdown planning and maturity records.

The active repository must not add runtime, release, or validation dependencies
on this branch. Use the GitHub Issues tracker for current work.
