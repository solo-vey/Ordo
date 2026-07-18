# Artifact Coverage

Artifact coverage defines where confirmed contracts must appear in generated outputs.

The canonical rule is:

```text
confirmed contract → artifact requirement → rendered artifact validation
```

A confirmed contract without artifact requirements is incomplete. A generated artifact that omits a required confirmed field is inconsistent.

## Typical analytical-package coverage

| Contract | Required artifacts |
|---|---|
| Event identity | README, Passport, Jira, Implementation Prompt, QA Package, SUMMARY, validation reports |
| Source contract | Passport, Jira, Implementation Prompt, QA Package, automation spec if applicable |
| Business fields | Passport, Jira, Implementation Prompt, QA Package |
| Trigger/no-op | Passport, Jira acceptance criteria, Implementation Prompt, QA Package |
| Normalization | Passport, Jira, Implementation Prompt, QA Package, unit/provider test matrix |
| HistoryEvent output | Passport, Jira, Implementation Prompt, QA expected result, SUMMARY, validation reports |
| Test strategy | Passport, Jira, Implementation Prompt, QA Package, validation report |
