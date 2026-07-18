# English Book Source

English is the canonical source language for all future edits.

The chapter translation ledger is stored in `book_manifest.json`. During the migration bootstrap, chapter files are added only after a complete editorial translation has been produced and reviewed. Missing files are intentional and correspond to `translation_required` entries; Ukrainian text must never be copied into this directory and represented as English.

After the English baseline is complete:

1. edit and version the English chapter first;
2. update its content hash and version;
3. mark the Ukrainian chapter as `outdated` in the sync manifest;
4. synchronize only affected Ukrainian chapters;
5. confirm semantic parity before setting `sync_status: synced`.
