# DD-ORDO-M32-001 — Public MVP package

Status: accepted

## Decision

M32 packages the Process Rail based Ordo workspace as the first public MVP candidate.

The MVP is positioned as a review/demo-ready workspace, not as a final open-source release. The license gap remains explicit through `LICENSE.md` and the publication/license policy documents.

## Reason

After M26–M31, Ordo has a coherent conceptual and toolchain line:

- Process Rail as the core model;
- AI Ordo Developer for authoring;
- AI Ordo Executor for hybrid execution;
- Semantic JSON IR as machine-readable rail;
- CLI as deterministic helper layer;
- registry/publication evidence.

M32 freezes this into a shareable MVP package before further implementation expansion.

## Impact

- README, changelog and release evidence identify M32 as public MVP candidate.
- Future work can branch into runtime implementation, tutorials, provider integration or license/publication decisions.
