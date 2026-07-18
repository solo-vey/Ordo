# External Developer Evidence Submission Instructions

Status: draft instructions for external developers submitting an Ordo/ARF playbook adoption case.

## Purpose

These instructions define the minimum information that an external developer or team must include when submitting evidence that a playbook was created independently using a public Ordo/ARF release.

The submission must be complete enough to support a bounded independence claim without exposing confidential business data.

## 1. Required submission information

The submission package must include:

### Team and relationship declaration

- Anonymous or public team identifier.
- Statement that the team is external to the Ordo/ARF authors.
- Statement whether any Ordo/ARF author participated in the work.
- Statement whether the team had access to:
  - internal repositories;
  - unpublished documentation;
  - private development discussions;
  - unreleased language or framework versions.
- Description of any assistance received from Ordo/ARF authors.

### Consumed Ordo/ARF release

- Exact release ID.
- Archive filename.
- Archive SHA-256.
- Date the release was obtained.
- Distribution channel.
- Confirmation that the work used the public package rather than an internal working tree.

### Development timeline

- Start date or evidence-bounded start interval.
- End date or evidence-bounded end interval.
- Approximate active working time.
- Major iteration milestones.
- Dates of testing and final packaging.

Unknown timestamps must be marked `not_recorded`. They must not be inferred or fabricated.

### Source package identity

Before anonymization or translation, calculate and record:

- original package filename;
- SHA-256 of the original package;
- date the hash was calculated;
- responsible submitter identifier.

The confidential original package must not be included in the publication-safe evidence package unless explicitly authorized.

### Development and testing evidence

- Description of how the playbook was created.
- Tools and models used.
- Model/provider/version, when available.
- Tests executed.
- Test totals and results.
- Validation reports.
- Problems found and fixes applied.
- Final package SHA-256.
- Post-unpack verification result.

### Author-assistance declaration

Use one of these values:

- `none_recorded`
- `general_public_documentation_only`
- `limited_clarification`
- `direct_author_assistance`
- `joint_development`

The evidence claim must reflect the selected value.

## 2. Independence evidence levels

The submitter must select only the strongest level supported by the evidence.

### Level 0 — self_declared_independence_unverified

Required:

- completed declarations;
- public release identity;
- source package SHA-256;
- development and testing evidence.

This level is acceptable for repository inclusion, but must not be described as independently verified.

### Level 1 — timestamp_verified

In addition to Level 0:

- the original pre-anonymization package hash is anchored by a trusted timestamp service.

Acceptable examples include:

- RFC 3161 timestamp authority;
- OpenTimestamps;
- another independently verifiable timestamp service.

The timestamp proof file or verification reference must be included.

### Level 2 — public_release_bound_verified

In addition to Level 1 or equivalent evidence:

- the exact public Ordo/ARF release is cryptographically identified;
- the submission confirms no internal or unpublished package was used;
- the development start occurred after the consumed public release became available.

### Level 3 — organizationally_separated

In addition to previous evidence:

- signed declaration from a separate organization, team, or cryptographic identity;
- explicit statement of no internal repository access;
- explicit statement of no direct author participation during the task window.

Identity may remain pseudonymous if the signature is stable and independently verifiable.

### Level 4 — third_party_verified

In addition to previous evidence:

- an independent third party verifies the timeline, package identity, team separation, or development process.

## 3. Use of external services

External services are recommended but not mandatory for the base submission.

Use them when a stronger independence claim is required.

Recommended uses:

- trusted timestamping of the original package hash;
- independent source-control timestamp;
- cryptographic signing by the external team;
- third-party attestation.

Do not upload confidential source material to a public service. Submit only hashes, signatures, or privacy-safe verification records.

The chosen service must allow later independent verification.

## 4. Publication-safe transformation

When the original package contains confidential, local-language, personal, or domain-specific information:

1. Preserve the original package privately.
2. Record its SHA-256.
3. Translate and anonymize a derived copy.
4. Replace personal, organizational, platform, URL, and domain-specific identifiers.
5. Recalculate all internal checksums.
6. Record every transformation in a provenance manifest.
7. State clearly that the publication package is derived evidence.
8. Do not claim byte identity between the original and publication-safe package.

## 5. Mandatory files

A submission should contain:

- `SUBMISSION_MANIFEST.json`
- `INDEPENDENCE_DECLARATION.json`
- `CONSUMED_RELEASE.json`
- `SOURCE_PACKAGE_IDENTITY.json`
- `DEVELOPMENT_TIMELINE.json`
- `TEST_AND_VALIDATION_SUMMARY.json`
- `TRANSFORMATION_PROVENANCE.json`, when transformed
- `INDEPENDENCE_EVIDENCE/`, when timestamp, signature, or third-party proof exists
- `SHA256SUMS.txt`
- `SUBMISSION_VALIDATION_REPORT.json`

## 6. Claim restrictions

The submission must not claim:

- verified independence without supporting evidence;
- absence of author assistance when assistance occurred;
- use of a public release without release identity evidence;
- deterministic or independent reproducibility without supporting runs;
- stronger evidence levels than the attached proof supports.

Use bounded language such as:

> This case documents one externally submitted playbook-development process. Independence is declared at the recorded verification level and is not generalized beyond the attached evidence.

## 7. Minimum acceptance gate

A submission is structurally acceptable when:

- all required files are present;
- required declarations are complete;
- consumed release identity is valid;
- package hashes are present;
- author assistance is declared;
- independence level matches the available proof;
- confidential original materials are excluded from the public package;
- checksums and post-unpack verification pass.
