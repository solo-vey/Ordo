# Key Decisions

- Build the playbook independently; never include the confidential source instruction file.
- Use a stable playbook ID and separate playbook SemVer from run-package revision numbers.
- Keep execution manual and analyst-led.
- Generate copy-ready documents only; do not mutate external systems.
- Require explicit analyst confirmation of the draft before external publication steps.
- Capture the document-system URL first, then prepare the work-tracking document containing that URL.
- Capture the work-tracking URL second.
- Store the first URL only in the work-tracking artifact and the second URL only in README.
- Do not validate URL domains or remote accessibility.
- Cancelled runs are terminal and non-resumable.
- The model may propose human approvers but cannot approve for them.
- Move generic execution-evidence and replay requirements to the framework backlog rather than duplicating them in the domain playbook.
