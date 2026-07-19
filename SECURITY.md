# Security Policy

## Supported versions

Security fixes are developed on the current `main` branch.

The latest canonical packaged release is evaluated case by case. Historical release candidates, transfer packages, archived milestone artifacts, and unsupported forks do not receive guaranteed security updates.

| Version or branch | Security support |
| --- | --- |
| Current `main` | Supported |
| Latest canonical packaged release | Best effort |
| Older packaged releases and historical archives | Not supported |

## Reporting a vulnerability

Use GitHub private vulnerability reporting for this repository:

`Security` → `Advisories` → `Report a vulnerability`

Do not disclose a suspected vulnerability in a public issue, discussion, pull request, commit message, review comment, or social-media post.

Include:

- the affected component and version or commit;
- a concise impact description;
- reproducible steps or a minimal proof of concept;
- required configuration or preconditions;
- whether credentials, private evidence, personal data, or unpublished material may be exposed;
- suggested mitigations, when available.

Do not include real credentials, private keys, confidential customer data, unauthorized personal information, or raw private conversations. Use synthetic or redacted test data.

## Security scope

Relevant reports include, but are not limited to:

- execution-control, authorization, or human-authority bypass;
- validator, gate, lock, checkpoint, or policy bypass;
- raw IR, canary, prompt, credential, or private-evidence leakage;
- provenance, checksum, evidence-chain, or release-identity tampering;
- unsafe archive extraction or path traversal;
- malicious package content that escapes declared execution boundaries;
- CI, workflow, dependency, or release-builder compromise;
- command injection, arbitrary file writes, or unintended code execution;
- privacy-impacting exposure caused by Ordo tooling.

General usage questions, documentation corrections, feature requests, and non-security bugs belong in the public support routes described in [`SUPPORT.md`](SUPPORT.md).

## Response targets

These are targets, not guaranteed service-level agreements:

- acknowledgement within 7 calendar days;
- initial triage within 14 calendar days;
- status updates when the assessment materially changes;
- coordinated disclosure after a fix or mitigation is available, when practical.

Complex reports may require more time. Duplicate, unverifiable, out-of-scope, or purely theoretical reports may be closed without a security advisory.

## Disclosure and credit

Do not publish details before maintainers confirm that coordinated disclosure is appropriate.

Reporter credit may be included with consent. Credit may be withheld for reports involving coercion, public disclosure before coordination, privacy violations, malicious exploitation, or fabricated evidence.

## Safe-harbor intent

Good-faith research that avoids privacy harm, service disruption, data destruction, persistence, credential use, and unnecessary access will be evaluated constructively. This statement does not authorize access to systems, data, or accounts that the researcher does not own or have explicit permission to test.

## Security advisories and releases

A confirmed vulnerability may be handled through a private security advisory, a private remediation branch, a public patch, release notes, or a new packaged release depending on impact.

A focused security test pass does not by itself make a release canonical. Existing release-integrity and delivery gates remain mandatory.
