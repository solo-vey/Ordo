# First playbook brief

Create a playbook that turns rough weekly notes into a concise weekly status
report.

Required inputs:

- completed work;
- blockers or risks;
- next steps;
- optional decisions needed from others.

Required output sections:

1. Summary
2. Completed
3. Blockers and risks
4. Next steps
5. Decisions needed

The playbook must detect missing required inputs, distinguish an empty section
from `none`, avoid inventing facts, and ask for approval before finalizing the
report.

Example notes for the dry-run:

- completed the repository-root cleanup;
- no current blocker;
- next step is documentation onboarding;
- decision needed: approve the final onboarding wording.
