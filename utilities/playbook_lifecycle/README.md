# Playbook Lifecycle Utility

This companion utility provides explicit, non-mutating support for playbook
upgrade review and rollback checkpoints. It does not change runtime state.

## Commands

```bash
python3 utilities/playbook_lifecycle/resolve_playbook_upgrade.py ACTIVE_RELEASE.json NEW_RELEASE.json
python3 utilities/playbook_lifecycle/resolve_upgrade_impact.py PLAYBOOK.json
python3 utilities/playbook_lifecycle/manage_playbook_checkpoint.py create PACKAGE_DIR CHECKPOINT.zip
python3 utilities/playbook_lifecycle/manage_playbook_checkpoint.py verify CHECKPOINT.zip
```

`resolve_upgrade_impact.py` accepts `--root` when the Ordo repository is not
the current repository root. `manage_playbook_checkpoint.py` writes a ZIP
archive only at the explicitly supplied output path.
