# English-only Repository Policy Gate

This is an internal fail-closed repository-hygiene validator. It is not a separate workflow.

It runs in the existing Ordo checks workflow, the existing full delivery gate, and directly inside `tools/build_release_archive.py`.

```bash
python tools/check_english_only_policy.py . --out reports/english_only_policy_report.json
```

The executable policy is `policies/english_only_policy.yaml`. Unknown Ukrainian occurrences block validation. The tool never modifies source files.
