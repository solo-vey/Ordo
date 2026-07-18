# Generic Template Review Engine

M79.3 adds a deterministic review layer for rendered template artifacts.

```bash
ordo template review CONTRACT \
  --artifact OUTPUT.md \
  --render-evidence render_evidence.json \
  --out template_review_evidence.json
```

The engine validates artifact existence and format, required sections, size limits, forbidden content, parseability for JSON/YAML outputs, and render provenance. A `strict` review profile requires render evidence. The output uses `ordo.template.review_evidence.v1` and records each check, finding severity, location, reviewer identity, checksums, and the final `approve` or `reject` decision.

The engine does not treat a free-form model statement such as “PASS” as sufficient review evidence. Semantic review may add findings, but structural and provenance gates remain deterministic and fail closed.
