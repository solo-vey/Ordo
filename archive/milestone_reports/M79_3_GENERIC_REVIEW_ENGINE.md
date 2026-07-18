# M79.3 — Generic Review Engine and Evidence Format

Status: implemented.

The CLI now provides `ordo template review` for deterministic review of rendered artifacts. The engine emits `ordo.template.review_evidence.v1`, preserves contract/artifact provenance, checks required sections and forbidden content, validates JSON/YAML parseability where applicable, and requires render evidence for strict profiles.

Decision policy:

- no blocking findings → `approve` / `passed`;
- one or more error findings → `reject` / `failed`;
- a model-authored “PASS” is never sufficient by itself.
