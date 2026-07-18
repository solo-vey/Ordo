# External Workflow Preparation — Release Candidate 1

Independent Ordo playbook for preparing one monitoring event as an approved business contract and downstream handoff. The package is authored from scratch; the user-provided process description was design input only and is not included.

## Operating model

The analyst executes the playbook manually. The playbook generates documents but never writes to work-tracking system or external documentation system.

1. Generate the complete draft package.
2. The analyst downloads, reviews, and explicitly approves the draft.
3. The analyst manually creates the external process record and returns its URL.
4. The playbook inserts the external documentation system URL into the work-tracking record document.
5. The analyst manually creates the Workflow Preparation work-tracking system entity and returns its URL.
6. The playbook writes the Workflow Preparation work-tracking system URL into this README, increments the package revision, and validates the linked package.
7. No second approval is required after link synchronization when business content is unchanged.

## External lifecycle links

- Workflow Preparation work-tracking system URL: `{{work_tracking_url}}`

The external process record URL is intentionally stored in the generated work-tracking record document, not duplicated here or across other business artifacts.

Only the external process record URL and Workflow Preparation work-tracking system URL are mandatory lifecycle links. URL host allowlists and remote accessibility are not checked.

Release status: **release candidate**, not canonical.
