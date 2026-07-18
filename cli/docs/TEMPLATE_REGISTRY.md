# Template Registry

The Template Registry is the machine-readable source of truth for reusable output templates. It records the stable template ID, semantic version, lifecycle status, contract path, checksum, render mode, and declared consumers.

## Command

```bash
ordo template registry-check examples/template_tooling/template_registry.yaml
```

The consistency gate fails on duplicate `template_id + version`, missing or invalid contracts, metadata mismatch, stale checksums, path escape, invalid lifecycle status, or multiple active versions of the same template. An active template with no declared `used_by` entry produces a warning, not an error.

## Lifecycle

Supported statuses are `active`, `experimental`, `deprecated`, and `disabled`. Deprecated entries remain discoverable for migration and should declare `replaced_by` when a successor exists.
