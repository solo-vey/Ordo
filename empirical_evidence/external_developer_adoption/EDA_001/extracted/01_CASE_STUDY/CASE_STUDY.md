# Case Study: Independent Adoption of Ordo/ARF to Create a New Playbook

## Objective

Provide the Ordo Language and ARF framework maintainers with empirical evidence that an independent developer can use a verified Ordo/ARF release to create a new executable playbook from a confidential process description without embedding, redistributing, or exposing that source description.

## Roles

- **Framework provider:** the Ordo/ARF maintainers who supplied the canonical language and framework release.
- **Independent developer:** the submitting team that created the new playbook.
- **Pilot executor:** a separate model/chat used to execute the created playbook and produce artifacts for review.

## Method

1. Verify the framework archive and create a pre-task rollback checkpoint.
2. Treat the confidential process description only as requirements evidence.
3. Derive an independent playbook contract, runtime states, nodes, transitions, gates, artifacts, and tests.
4. Package the first alpha and run clean post-unpack validation.
5. Clarify external-system and human-approval boundaries.
6. Introduce a draft-review and manual publication lifecycle.
7. Execute the playbook in a cross-model pilot using a controlled answer script.
8. Review generated outputs, identify defects, and regenerate corrected drafts.
9. Complete a linked-package run and export available execution evidence.
10. Separate framework-level improvements from domain-playbook improvements.
11. Remove unnecessary local over-engineering.
12. Promote the playbook to release candidate after full validation and rollback verification.

## Main findings for the framework maintainers

- A confidential process specification can guide implementation without becoming package source.
- External lifecycle fields often require explicit ordered nodes rather than a single readiness flag.
- Exact identity fields need consistency checks across state and artifacts.
- The model must not create unsupported open questions or infer human approval.
- Playbook SemVer and individual run-package revisions are different version dimensions.
- Evidence/replay capabilities are primarily framework concerns and should be inherited by playbooks.
- A separate model can execute the produced playbook, exposing defects that static package validation alone does not reveal.

## Outcome

The independent developer produced a release candidate with a manual analyst workflow, copy-ready business documents, ordered external publication steps, strict link-placement rules, checksums, tests, rollback metadata, and clean post-unpack verification.

This outcome is submitted to the Ordo/ARF maintainers as external adoption evidence, not as a framework-authored example.
