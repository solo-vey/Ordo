# M87.3 — Plain Prompt baseline runner

Status: **passed**

Implemented:

- frozen Plain Prompt template for arm A;
- canonical `pair_id`;
- deterministic A/B order assignment;
- contamination blocking before invocation;
- shared-payload SHA-256 binding;
- canonical benchmark evidence;
- immutable per-run directory;
- `ab_metadata.json` for arm-level pairing metadata.

Validation: **27/27 tests passed**.

No external provider API was invoked.
