# Ukrainian Text Archive Audit

`tools/audit_ukrainian_text.py` is a read-only forensic audit. It finds
Ukrainian characters in the Git-tracked repository payload, including text
inside nested ZIP, TAR, and GZIP archives. It never extracts an archive into
the repository.

The default exclusion is only `book/**`, the intentional localized-book
contour. Historical transfers, archives, reports, legal files, and other
repository paths remain visible in the result so their Ukrainian content can
be reviewed explicitly.

Run the audit and keep its report outside the repository:

```bash
python tools/audit_ukrainian_text.py . \
  --out /tmp/ordo-ukrainian-text-audit.json
```

Useful options:

- `--filesystem` also examines untracked physical files, while ignoring
  `.git` internals;
- `--include-book` includes the Ukrainian book contour;
- `--exclude-glob PATH/**` adds an explicit, reportable scope exclusion;
- `--fail-on-findings` returns a non-zero status for automation;
- archive-depth, member-count, member-size, and total-uncompressed-size limits
  protect the audit from archive bombs.

The output records source paths, nested archive member paths, a small set of
matching-line samples, and any unreadable or limit-exceeded archive warnings.
This tool is an inventory aid, not a replacement for the migration-aware
[English-only policy](../policies/english_only_policy.yaml).
