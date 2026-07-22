# Historical Payload Externalization Audit

Status: `open — disposition planning only`

The current repository should prioritize current-state entry points and active
implementation. Historical material may remain available through Git history,
but need not remain inline in every current checkout when immutable external
storage can preserve identity and retrieval.

## Candidate contours

| Contour | Current classification | Default disposition to evaluate |
| --- | --- | --- |
| `TRANSFER_2026-07-14/` | checksum-bound transfer provenance; 94 files, about 944 KB | external immutable archive with a retained locator manifest |
| `recovery/2026-07-14/` | recovery evidence; 5 files, about 26 KB | external immutable archive or compact retained recovery manifest |
| `archive/handoffs/` | localized/historical handoffs | external immutable archive after current documentation routes are verified |
| `docs/handoff/legacy-root/`, `docs/releases/legacy-root/`, `docs/status/legacy-root/`, `manifests/releases/legacy-root/` | labelled historical records relocated during J.6 | external immutable archive or consolidated provenance index |
| `checkpoints/playbooks/` | verified pre-RC6 rollback evidence | handled by `BL-ORDO-059` |
| `docs/apf/legacy-root/` | legacy documentation with active references | retain until an approved reference migration makes it non-active |

## Guardrails

- No in-place edits of immutable evidence or archive payloads.
- Before externalization, create a current in-repository English locator
  manifest with SHA-256, size, media type, immutable storage URL, provenance,
  retention rule, and retrieval status.
- Verify a clean retrieval and, where applicable, archive integrity or restore
  round trip before removing inline bytes.
- Update all documentation, tests, manifests, builders, and root checksums in
  the same approved migration.
- Do not rewrite Git history as part of ordinary cleanup.
- Keep current front doors free of historical material unless it is still an
  active dependency.
