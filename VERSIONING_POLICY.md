# Ordo Versioning and Upgrade Governance

## Version lines

Ordo maintains independent semantic-version lines:

1. **Ordo Language** — grammar, source contracts, IR constructs, compiler/runtime semantics and language-level validation.
2. **Ordo ARF/IRF Framework** — process-generation workflow, package governance, review/delivery gates, evidence, migration and release tooling.
3. **Applied packages** — each package keeps its own version and declares compatible language/framework ranges.

## Version bump rules

| Change | Language | Framework |
|---|---|---|
| Breaking grammar, IR or runtime semantics | MAJOR | — |
| Additive construct or optional semantic capability | MINOR | — |
| Compatible compiler/linter/runtime bug fix | PATCH | — |
| Breaking process, package or release contract | — | MAJOR |
| Additive gate, workflow, governance or tooling | — | MINOR |
| Compatible framework/tooling defect fix | — | PATCH |

Pre-release suffixes follow SemVer (`alpha`, `beta`, `rc`). Milestone IDs remain engineering-history identifiers and never replace release versions.

## Mandatory release records

Every release must update:

- `manifests/VERSION_STATE.json`;
- `manifests/RELEASE_LEDGER.json`;
- `manifests/UPGRADE_IMPACT_CATALOG.json`;
- root and language changelogs;
- backlog items through `target_release`, `affects`, and `completed_in`;
- package compatibility declarations when requirements change.

## Backlog rule

A new backlog item must be checked against open master tasks before a new ID is created. It must declare the expected release and affected version lines. Closing an item without `completed_in` is a blocking version-governance defect.

## Upgrade rule for an active playbook process

The process compares its recorded language/framework versions with `VERSION_STATE.json`, then resolves every intervening release in `UPGRADE_IMPACT_CATALOG.json`.

Possible decisions:

- `no_action` — documentation or unrelated scope only;
- `recommended_revalidation` — compatible change that touches constructs used by the playbook;
- `migration_required` — declared migration must be applied before continuing;
- `upgrade_blocked` — breaking or incompatible range.

The resolver must never rewrite a playbook automatically. It emits an impact report and explicit migration/revalidation actions for review.

## Canonical documentation language

English is the authoritative language for version records, changelogs, release notes, policies, schemas, manifests and technical documentation. Conversation language does not change the canonical documentation language.
