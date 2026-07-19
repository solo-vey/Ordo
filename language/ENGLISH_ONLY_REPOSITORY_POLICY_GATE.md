# English-only Repository Policy Gate

The repository currently uses migration mode. Violations recorded against baseline commit `41ed7b773a3e592aa79dceeb0833e05920ec9f95` may only decrease. Any new Ukrainian occurrence blocks CI. Once the baseline reaches zero, policy mode must be changed to strict and the migration baseline removed.

```bash
python tools/check_english_only_policy.py . --out reports/english_only_policy_report.json
```
