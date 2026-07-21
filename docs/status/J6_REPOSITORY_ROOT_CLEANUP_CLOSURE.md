# J.6 repository-root cleanup closure

Status: `closed`

J.6 reduced the repository root to the public front door, legal and community documents, the checksum index, and two root-level policy configurations required by tooling.

The contour completed:

- read-only root inventory and classification;
- APF documentation and evidence relocation;
- delivery, self-check, pre-release, release-manifest, and release-note relocation;
- policy, backlog, status, and handoff consolidation;
- active-link, builder, manifest, checksum, and relocation-contract validation;
- exact 15-file root allowlist enforcement;
- full local delivery and isolated release-tree validation.

Historical and immutable contours were preserved without present-tense rewrites. Exact phase, pull-request, commit, CI, and root-layout evidence is recorded in [`../../manifests/J6_ROOT_CLEANUP_CLOSURE.json`](../../manifests/J6_ROOT_CLEANUP_CLOSURE.json).

The next documentation work is L.1, a read-only documentation quality-gate audit, followed by L.2, chat-first onboarding and a first-playbook quickstart.
