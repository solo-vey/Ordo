# M79.4 — Template version diff and breaking-change gate

`ordo template diff OLD NEW` compares two validated template contracts and emits `ordo.template.version_diff.v1` evidence.

Breaking changes include render-mode or output-format changes, new required inputs or sections, removed input properties, stricter review policy, compatibility changes, and model-contract changes. A breaking change is allowed only with a MAJOR version increase and an explicit migration block containing `required: true` and `guide_ref`.

Non-breaking additions remain allowed in MINOR/PATCH versions. The gate never rewrites contracts automatically.
