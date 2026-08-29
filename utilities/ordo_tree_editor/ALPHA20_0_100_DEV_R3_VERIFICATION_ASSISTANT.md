# alpha.20.0.100-dev — Verification Assistant

- Verify Playbook now uses the same two-pane architecture as Playbook Settings.
- Main workspace: verification progress and result list.
- Right auxiliary pane: Verification Assistant.
- `Explain with model` remains available as a one-shot explanation for every non-PASS result: FAIL, ERROR, and SKIPPED.
- Every non-PASS result also has `Discuss in chat`.
- Discussing a check supplies its status, skip reason, message, stdout/stderr, evidence summary, and generated evidence reports to the configured model.
- The assistant continues a focused conversation in the playbook's analyst-facing language.
- The assistant is read-only and cannot alter the playbook or verification verdict.
