# Scoring contract

**Scoring profile:** TC03-EX02 Process Scoring v1.1

Final run score:

- 50% playbook-pure process-execution quality;
- 50% generated-document quality.

## Process-score boundary

Process evaluates only behavior owned by the playbook definition. It excludes:

- result-packaging and evidence-export defects;
- analyst/Driver errors that are external to the playbook definition.

These excluded dimensions may be reported diagnostically but do not reduce Process or Final.

For terminal routes where canonical documents must not be generated, document quality is scored against the required noncanonical result and correct absence of canonical artifacts.

Principal document criteria:

- Passport;
- Jira task;
- Manual QA package;
- QA automation specification.

A correct terminal state does not compensate for shallow or materially incomplete principal documents.
