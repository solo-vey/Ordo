# Ordo dependency lockfile

`ordo.lock.json` records the resolved dependencies of an Ordo package:
template sets and, later, libraries, profiles, and domain packs.

## Why this is needed

Without a lockfile, a package can generate different outputs after a registry
or template-set version changes. M10 makes package output reproducible: a
release must identify the exact templates, sources, and hashes used.

## Commands

```bash
ordo lock packages/history_event_guided_intake
ordo validate-lock packages/history_event_guided_intake
ordo validate-release packages/history_event_guided_intake
```

## Format

```json
{
  "lockfile_version": "1.0",
  "package": {
    "name": "history_event.guided_intake",
    "version": "0.1.0",
    "ordo_version": "0.12"
  },
  "dependencies": [
    {
      "kind": "output_template_set",
      "id": "history_event.guided_intake_outputs",
      "version": "0.1.0",
      "source": "package_registry",
      "hash": {
        "algorithm": "sha256-tree",
        "value": "..."
      }
    }
  ]
}
```

## Release rule

`validate-release` generates and validates the lockfile automatically. If the
resolved dependencies do not match `ordo.lock.json`, the release must be
blocked.
