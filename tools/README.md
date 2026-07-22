# Internal tools

This directory contains deterministic build, validation, audit, release, and
maintenance tools used by repository workflows. These tools are not companion
utilities for end users; those live in [`../utilities/README.md`](../utilities/README.md).

- [`build_release_archive.py`](build_release_archive.py) — sanctioned release archive builder.
- [`check_english_only_policy.py`](check_english_only_policy.py) — repository language-policy validator.
- [`run_golden_examples.py`](run_golden_examples.py) — golden-example runner.
- [`evidence_storage/README.md`](evidence_storage/README.md) — evidence-storage validation helper.

Use [`../cli/README.md`](../cli/README.md) for supported CLI commands.
