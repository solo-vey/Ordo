# alpha.20.0.96-dev — Verification triage hardening

- Fixes the bundled visual graph generator Python syntax defect.
- Adds descriptor-driven runtime evidence applicability.
- Source-only verification skips state/journey checks when their required runtime evidence is absent.
- Verification runner embeds generated/updated reports as structured evidence.
- UI shows evidence summaries and expandable report contents.
- Exported verification JSON includes evidence.
- Model explanations receive generated report evidence.
- Model classification is hard-enforced to the fixed verification classification enum; unsupported values normalize to `inconclusive`.
