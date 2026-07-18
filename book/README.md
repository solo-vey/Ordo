# Ordo Book Sources

The book is maintained as localized, chapter-based source trees.

- `en/` — canonical source language for all future book changes.
- `uk/` — Ukrainian translation and the preserved pre-publication baseline.
- `manifests/chapter_sync_manifest.yaml` — chapter-level version and synchronization ledger.
- `releases/frozen/` — approved rendered artifacts that must not be regenerated without an explicit instruction.

## Current migration state

The Ukrainian M72 book is preserved as the complete baseline. The English tree has been initialized as the future source of truth. Its manifest explicitly marks every chapter that still requires translation; no untranslated chapter is presented as completed English content.
