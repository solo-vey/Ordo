# ORDO Playbook & Graph Verification Toolkit

Standalone snapshot of the verification capabilities currently used by Vibe ARF alpha.9, derived from the Ordo 0.4.10 language/tooling package plus the documented alpha.9 compatibility alignments.

## Start here
Read `VERIFICATION_CATALOG.md`.

## CLI usage
From this directory:

```bash
export PYTHONPATH="$PWD/ordo_pkg"
python -m ordo.cli lint /path/to/playbook
python -m ordo.cli compile /path/to/playbook
python -m ordo.cli test /path/to/playbook
python -m ordo.cli coverage /path/to/playbook
```

For a standard safe core suite:

```bash
./run_core_verification.sh /path/to/playbook
```

The runner intentionally does not execute commands that need analyst/runtime inputs or that create release artifacts.
