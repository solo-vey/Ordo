# Repository root relocation contract

The J.6 cleanup moves non-front-door material out of the repository root without rewriting historical evidence. The machine-readable source of truth is [`../manifests/ROOT_RELOCATION_CONTRACT.json`](../manifests/ROOT_RELOCATION_CONTRACT.json).

The contract records every former root path and its canonical destination. Automated tests require that:

- every former root path stays absent;
- every canonical destination exists;
- active builders, workflows, package profiles, and manifests reference canonical paths;
- navigation links in relocation indexes resolve;
- `SHA256SUMS.txt` contains the relocated destination and its current digest, not the former root path;
- relocated report artifacts remain declared and correctly hashed in `reports/CANONICAL_REPORTS_MANIFEST.yaml`.
- the repository root contains only the public front door, legal and community files, checksum index, and root-level policy configuration.

Historical reports, transfer packages, frozen manifests, and immutable evidence may retain old path mentions as provenance. They are not rewritten merely to reflect the current repository layout.

J.6 is closed. Its final machine-readable evidence is [`../manifests/J6_ROOT_CLEANUP_CLOSURE.json`](../manifests/J6_ROOT_CLEANUP_CLOSURE.json), with the human-readable summary in [`status/J6_REPOSITORY_ROOT_CLEANUP_CLOSURE.md`](status/J6_REPOSITORY_ROOT_CLEANUP_CLOSURE.md).
