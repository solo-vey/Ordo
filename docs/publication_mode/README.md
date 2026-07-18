# M39 — License / Publication Decision

## Decision

For `v0.12.0-preview`, Ordo is published as a **source-available preview candidate**.

This means:

- the repository/workspace can be shared for review and demonstration;
- no open-source license is granted yet;
- production use, redistribution, sublicensing or derivative commercial use require explicit permission;
- the open-source license decision is deferred to a later milestone.

## Why this decision

The current package is mature enough for external review and GitHub preview publication, but the project owner has not selected a final open-source license for the language, CLI, book, reference packages and assets.

Therefore M39 closes the publication-mode ambiguity by choosing a conservative preview mode for this release candidate.

## Release status after M39

```text
Version: v0.12.0-preview
Milestone: M39
Publication mode: source-available preview candidate
Open-source status: not open-source
License blocker for preview publication: closed
License blocker for open-source release: deferred
```

## What is allowed

- Internal review.
- External reviewer handoff.
- GitHub preview repository publication with this license notice.
- Demonstration and evaluation by explicitly authorized reviewers.

## What is not allowed by default

- Treating the repository as open-source.
- Copying or redistributing the materials under an assumed OSS license.
- Production product use without permission.
- Removing or weakening the license notice.

## Next possible paths

1. Continue as source-available preview and publish the GitHub preview repository.
2. Select final open-source license(s) and convert the repository to true open-source.
3. Keep the repository private/internal until legal/product review is complete.
