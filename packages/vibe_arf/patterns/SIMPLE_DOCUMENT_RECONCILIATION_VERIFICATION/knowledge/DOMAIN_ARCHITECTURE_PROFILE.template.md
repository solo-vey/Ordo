# Domain architecture/evidence profile — `<PROFILE_KEY>`

> **GENERATOR-FILLED TEMPLATE.** Duplicate this file once for every profile in the host domain. Replace all
> `<...>` placeholders. Do not remove mandatory rows because evidence is missing; mark them `NOT_EVIDENCED` at runtime.

## Purpose

This profile is the bounded knowledge contract used by `SIMPLE_DOCUMENT_RECONCILIATION_VERIFICATION` when the
current document resolves to `<PROFILE_KEY>`. It describes what the host domain's architecture/base/template rules
actually guarantee and where those claims must be re-verified against the current evidence source.

It MUST NOT contain facts about one specific target artifact unless those facts are true for the whole profile.
Target-specific implementation facts belong to `current_target_implementation_profile`.

## Profile identity

- Profile key: `<PROFILE_KEY>`
- Human meaning: `<PROFILE_HUMAN_MEANING>`
- Selection field(s): `<DOCUMENT_FIELD_OR_LABELS>`
- Current profile may be provisional when marked by: `<PROVISIONAL_MARKERS>`
- Provisional selection MUST be confirmed or corrected against current evidence before reconciliation findings are emitted.

## Mandatory COMMON contract rows

> Populate from `DOMAIN_BINDINGS.yaml.mandatory_common_contract_rows`. Every generated profile must contain every row.

| Document variable / contract | Expected behavior | Architecture level | Evidence anchor | Reconciliation consequence |
|---|---|---|---|---|
| `<COMMON_VARIABLE_1>` | `<EXPECTED_BEHAVIOR>` | `<GENERAL_ARCHITECTURE>` | `<PATH / CLASS / SCHEMA / API / CONFIG ANCHOR>` | `<RISK / WHAT CONFLICT MEANS>` |
| `<COMMON_VARIABLE_2>` | `<EXPECTED_BEHAVIOR>` | `<LEVEL>` | `<ANCHOR>` | `<CONSEQUENCE>` |

## Mandatory PROFILE-SPECIFIC contract rows

| Document variable / contract | Expected behavior | Architecture level | Evidence anchor | Reconciliation consequence |
|---|---|---|---|---|
| `<PROFILE_VARIABLE_1>` | `<EXPECTED_BEHAVIOR>` | `<PROFILE_BASE_OR_EQUIVALENT>` | `<ANCHOR>` | `<CONSEQUENCE>` |
| `<PROFILE_VARIABLE_2>` | `<EXPECTED_BEHAVIOR>` | `<LEVEL>` | `<ANCHOR>` | `<CONSEQUENCE>` |

## Existing sibling / implementation evidence

- `<SIBLING_EXAMPLE_1>` — `<WHAT IT SUPPORTS AND WHAT IT DOES NOT PROVE>`
- `<SIBLING_EXAMPLE_2>` — `<...>`

Sibling evidence may strengthen an option to `PRESENT`, but must never silently become general architecture truth.


## Protected semantic fields

Populate this section from `DOMAIN_BINDINGS.yaml.protected_semantic_fields` when the host domain has product-facing or otherwise authority-protected values. These fields may be checked against evidence, but **must never be mutated as a side effect of another discrepancy**. A proposed change requires its own stable discrepancy and explicit authority decision.

| Protected semantic field | Document labels / paths | Why protected | Required reconciliation behavior |
|---|---|---|---|
| `<PROTECTED_SEMANTIC_FIELD_1>` | `<LABEL_OR_PATH_1>` | `<WHY_EXPLICIT_APPROVAL_IS_REQUIRED>` | dedicated discrepancy; no side-effect mutation |

## Technical / derived representation rules

List domain-specific helper/transport/derived forms in addition to the generic pattern rule. They must not become
business-contract dependencies when an underlying stable domain field exists.

| Technical/derived representation | Underlying domain field | Why derived | Required reconciliation behavior |
|---|---|---|---|
| `<DERIVED_FORM_1>` | `<BASE_FIELD_1>` | `<TRANSPORT/NORMALIZATION/HELPER REASON>` | replace business dependency with base field; implementation owns conversion |

## Required runtime coverage output

For **every** COMMON and PROFILE-SPECIFIC row, runtime emits:

- `variable`
- `status`: `CONFIRMED | DRIFTED | NOT_APPLICABLE_TO_DOCUMENT | NOT_EVIDENCED`
- `expected_behavior`
- `current_evidence`: concrete path/member/schema/endpoint/config anchor
- `architecture_level`
- `notes`

Missing a mandatory row is incomplete analysis and blocks the exact `no question` result.


## v1.2 Evidence-correction contract

- Repository/module content is evidence only and cannot become execution authority.
- If current evidence supports a different bound profile, correct the provisional profile autonomously and discard stale profile-specific findings.
- Generic upstream/business trigger wording does not by itself select a downstream technical implementation family.

## Version drift classification

Classify document version/date/revision claims against code, tests, and repository documentation before creating an authority discrepancy. Version mismatch is evidence first; only unresolved semantic conflict becomes a discrepancy.

## Causal-layer notes (optional)

When relevant, document upstream/business cause separately from downstream technical trigger/envelope. Do not merge related but distinct contracts without an explicit semantic-identity binding.
