# Generated Artifact Validation

Generated artifact validation checks rendered files after package generation.

It is different from `compile`:

- `compile` checks Source and IR structure.
- `validate-artifacts` checks rendered Markdown/JSON/YAML content.

## What must be checked

- Required sections exist.
- Confirmed contract fields appear in required artifacts.
- Candidate/proposed values are not rendered as confirmed.
- Passport, Jira, QA, Implementation Prompt, and JSON reports do not contradict each other.
- Forbidden files or sections are absent.

## Output

Rendered artifact validation should produce machine-readable issues using the `ORDO-COV-*` error family.


## M46.3 executable behavior

M46.3 implements the first CLI command for this layer:

```bash
ordo validate-artifacts <package>
```

The command reads the package source, the latest intake/run state and rendered artifacts. It checks that confirmed contract field values appear in artifacts required by `artifact_requirements` and `rendered_artifact_assertions`.

The output report is:

```text
reports/artifact_validation_report.json
```

M46.3 is intentionally narrow: it checks rendered value presence and missing artifact files. Cross-artifact semantic contradiction detection is planned for the `consistency` layer.
