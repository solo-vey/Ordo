# Playbook Versioning and Runtime Upgrade Handoff

Every canonical playbook owns an independent SemVer version and a `playbook_release.json`. Each release records the language/framework versions used to build it, previous version, concise changed surfaces, completed backlog items, migration and rollback instructions. A running process must compare its active release record with the supplied release through `utilities/playbook_lifecycle/resolve_playbook_upgrade.py`. The resolver returns `no_action`, `recommended_revalidation`, `migration_required`, or `upgrade_blocked`. It never mutates active runtime state automatically.

## Mandatory rollback checkpoint lifecycle

Before every playbook version bump, create and verify an immutable checkpoint of the previous package and active runtime state. The new release record must reference a checkpoint conforming to `ordo.playbook.rollback_checkpoint.v1`. A disposable restore round-trip is blocking.
