# CLI Validation Summary

Package: history_event.guided_intake
Version: 0.1.1
Validation date: 2026-07-07T07:44:30.892944+00:00
CLI status: executed_cli_passed

## Commands

| Command | Result | Notes |
|---|---|---|
| lint | passed | reports/lint_report.json |
| compile | passed | reports/compile_report.json |
| test | passed | reports/test_report.json |
| coverage | passed | reports/coverage_report.json |
| run | passed | reports/run_report.json |
| intake | passed | reports/intake_report.json |
| generate-output | passed | reports/output_generation_report.json |
| validate-output | passed | reports/output_validation_report.json |
| lock | passed | reports/lock_report.json |
| validate-lock | passed | reports/lock_validation_report.json |
| check-conflicts | passed | reports/dependency_conflict_report.json |
| package | created | release/history_event.guided_intake-0.1.1.zip |
| build-provenance | passed | reports/release_provenance.json |
| validate-provenance | passed | reports/release_provenance_validation_report.json |

## IR status

- source YAML: source/program.ordo.yaml
- compiled IR: compiled/program.ir.json
- IR freshness: checked during runtime-status / compile step

## Output validation

- generated outputs: see output_generation_report.json
- validate-output: see output_validation_report.json
- validate-release: reports/release_validation_report.json

## Known limitations

- This summary records CLI helper execution. It does not claim live AI/model execution.
