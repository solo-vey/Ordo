# M12 Output Validation

`ordo validate-output <package>` validates generated Markdown output artifacts as derived artifacts.

It checks:

- required outputs from `output_templates.yaml`;
- generated files listed in `reports/output_generation_report.json`;
- unresolved `{{ ... }}` placeholders;
- empty Markdown files;
- unclosed Markdown code fences;
- whether outputs were generated only after runtime/intake output gates allowed them.

Typical workflow:

```bash
ordo intake packages/history_event_guided_intake --answers packages/history_event_guided_intake/run_inputs/intake_success.yaml --non-interactive
ordo generate-output packages/history_event_guided_intake
ordo validate-output packages/history_event_guided_intake
ordo validate-release packages/history_event_guided_intake
```
