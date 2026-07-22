# External historical archives

Historical material that is not required for current runtime, package, or documentation operation is stored outside the active repository tree as GitHub Release assets. This keeps ordinary clones focused on current Ordo while preserving checksum-bound provenance and recovery material.

## Historical provenance archive — 2026-07

- Release: [historical-provenance-2026-07-22](https://github.com/solo-vey/Ordo/releases/tag/historical-provenance-2026-07-22)
- Locator: [`../manifests/external_archives/HISTORICAL_PROVENANCE_2026_07_22.json`](../manifests/external_archives/HISTORICAL_PROVENANCE_2026_07_22.json)
- Archive SHA-256: `265ce7ad9bca1ca285615a7c434bc0689ee87ff37b3cb77852fd7f4b43affc0d`

It contains the 2026-07-14 transfer and recovery material, historical handoffs, legacy release/status/manifests, and pre-RC6 checkpoints. It does **not** contain `docs/apf/legacy-root/`, which remains in the repository because active documentation and tests reference it.

## Verify and restore

Download the archive and its attached `SHA256SUMS.txt`, verify the archive SHA-256, extract it, then run the checksum file from the extracted `payload/` directory:

```bash
shasum -a 256 -c ../metadata/SHA256SUMS.txt
```

The attached manifest records every archived path, byte count, source commit, and content digest. Do not replace an asset or edit historical payload in place; publish a new archive ID if a future retention decision requires a different snapshot.
