# Governance

## Project model

Ordo currently uses a maintainer-led governance model.

The repository owner is the final decision authority for repository scope, language semantics, framework contracts, release identity, security advisories, licensing, contributor access, and merges to protected branches.

This model does not use community voting, binding polls, or automatic acceptance based on popularity.

## Decision principles

Decisions should preserve:

- explicit human authority;
- deterministic behavior where required;
- evidence provenance and bounded claims;
- compatibility and migration clarity;
- repository and release integrity;
- security and privacy;
- narrow, reviewable changes;
- authoritative English normative documentation.

## Change classes

### Routine changes

Documentation corrections, focused tests, and low-risk tooling improvements may use normal pull-request review.

### Elevated-review changes

The following require explicit maintainer approval and complete impact analysis:

- language or schema changes;
- runtime or human-authority boundary changes;
- validator, gate, lock, provenance, or evidence-policy changes;
- release identity or canonical archive changes;
- security policy or disclosure changes;
- license or commercial-use changes;
- governance changes;
- deletion or rewriting of immutable evidence.

### Emergency security changes

Confirmed vulnerabilities may be developed privately. Normal public review may be deferred until coordinated disclosure, but testing, provenance, release-integrity, and rollback requirements still apply.

## Pull requests and merges

Contributors propose changes through pull requests. Maintainers may request changes, narrow scope, split work, defer work, or close proposals.

Passing tests is necessary but not sufficient for merge. Maintainers also evaluate design fit, evidence quality, privacy, compatibility, maintenance cost, licensing, and release impact.

Only maintainers with repository write authority may merge.

## Conflicts and appeals

Technical disagreements should be resolved through evidence, reproducible examples, explicit assumptions, and documented tradeoffs.

The repository owner makes the final decision when consensus is not reached. A contributor may request reconsideration once with new evidence or a materially revised proposal.

## Maintainer responsibilities

Maintainers should:

- avoid presenting candidates as canonical without required evidence;
- disclose relevant conflicts;
- protect private reports and personal information;
- document material decisions;
- keep release identity and checksums consistent;
- enforce the Code of Conduct without retaliation;
- avoid promising support or timelines that cannot be maintained.

## Governance changes

Changes to this document require a dedicated pull request that explains:

- the problem being solved;
- the authority or responsibility being changed;
- migration and transition effects;
- security, licensing, and release implications.

Governance changes take effect only after merge to `main`. Historical governance text remains available through Git history.
