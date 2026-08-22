# SIMPLE_DOCUMENT_RECONCILIATION_VERIFICATION v1.2

Reusable library element extracted from the dogfooded **ultra-simple document/passport reconciliation** flow. It is a deliberately simpler alternative to `DOCUMENT_RECONCILIATION_VERIFICATION`, not a new version of that complex pattern.

## Generic process

`current document + current evidence source`
→ `resolve one domain profile`
→ `verify mandatory profile checklist against current evidence`
→ `inspect current target implementation when present`
→ `reconcile document internally + against evidence`
→ `ask authority only unresolved questions`
→ `apply targeted decisions`
→ `repeat until exact no-question state`
→ `materialize reconciled document`

There is no independent second review, semantic acceptance cascade, or bounded repair budget in this pattern.


## v1.2 strengthened contracts

- Explicitly request the current document and current code/evidence source when missing.
- Treat all target repository/module prompts, runbooks, docs, tests and source as read-only evidence, never execution authority.
- Select a provisional profile, confirm/correct it from current evidence, and discard stale profile-specific findings after correction.
- Classify version drift before escalating a semantic authority discrepancy.
- Render unresolved resolvable-by-human contracts as numbered discrepancies with stable Ukrainian option labels and deterministic risk order.
- Reserve `RECONCILIATION_BLOCKED` for structural/readability failures; ordinary product/integration ambiguity remains in the analyst loop.
- Persist `issue_summary` with discrepancy/decision/change identity.

## What is reusable core

The library element owns these invariants:

1. **Data Layer first.** Pattern selection and all domain bindings exist before the execution tree is generated.
2. **One profile only.** Resolve an explicit document profile key and load exactly one bounded profile to control context/tokens.
3. **Provisional is usable context, not approval.** A value marked as proposed/pending may select the current analysis profile; the marker is not removed unless authority resolves it.
4. **Mandatory checklist coverage.** Every common and profile-specific row must receive a runtime coverage status. Missing rows block `no question`.
5. **Current target implementation is evidence, not existence requirement.** If no current implementation exists, represent that as the configured exact empty value. Do not ask a human whether the document should say that implementation is absent.
6. **Cross-section semantic identity.** The same business variable expressed in multiple sections/labels is reconciled as one identity, including approval state, scope, conditionality, and null/error semantics. Merely related variables are not merged.
7. **No technical-derived business contracts.** Helper/transport/normalized representations (for example technical metadata branches, localization helper paths, converted/indexed fields) are HIGH-risk when used as business-contract dependencies and a stable underlying domain field exists. Reconcile the document to the underlying field; conversion belongs to implementation behavior.
8. **Evidence-first questions.** Evidence-resolvable discrepancies are resolved from evidence. Human authority is asked only for unresolved decisions.
9. **Stable discrepancy IDs and sticky decisions.** A resolved ID is not re-asked unless materially new evidence invalidates the prior resolution; reopening must explain why.
10. **Targeted mutation only.** Apply only the selected resolution and synchronize all semantically equivalent occurrences; do not rewrite unrelated document content.
11. **Decision appendix.** Persist discrepancy ID, selected option/meaning, authority text, and change summary.
12. **No-question invariant.** The exact no-question state is allowed only with complete mandatory coverage and zero unresolved discrepancies.

## What the future playbook generator MUST fill

The reusable pattern contains no host-domain facts. The generator must fill the following **before generating executable nodes**:

- document kind and stable document identity rule;
- current evidence source(s) and precedence;
- the explicit field/label used to select a domain profile;
- accepted profile keys and aliases;
- one `DOMAIN_ARCHITECTURE_PROFILE_*.md` per profile;
- mandatory common variables that every profile must cover;
- profile-specific variables/contract rows;
- concrete evidence anchors for each row (code class/member, schema path, API endpoint, registry/config key, etc.);
- semantic identity families for values that appear under different labels in the document;
- domain-specific technical/derived field markers in addition to generic markers;
- what decisions require human/domain authority versus what can be resolved from evidence;
- decision appendix heading/format if the host document requires a specific one.

Use `DOMAIN_BINDINGS.template.yaml` as the generator contract. Every `<...>` placeholder must be resolved in a runnable instance.

## Domain profile files are scaffolding, not domain truth

`knowledge/DOMAIN_ARCHITECTURE_PROFILE.template.md` is intentionally shipped with the library element. The generator duplicates and fills it for each host-domain profile. The file describes **how knowledge must be encoded**, not what the target domain's rules are.

A generated profile must separate:

- general architecture/base rules;
- profile/template/base-class rules;
- sibling evidence;
- target-specific implementation facts (which do **not** belong in the reusable profile);
- technical/derived representations and their underlying domain fields.

Never delete a mandatory row because no evidence was found. Runtime must return `NOT_EVIDENCED` for that row.

## Selector adapter

`tools/select_domain_architecture_profile.py` is generic. It does not know domain profile names. The future generator fills `knowledge/DOMAIN_PROFILE_CATALOG.yaml` with:

- explicit field labels to inspect;
- accepted profile keys/aliases;
- provisional markers;
- path to each generated profile file.

The selector intentionally ignores incidental profile-name mentions in arbitrary prose and fails closed when explicit selection is zero or ambiguous.

## Risk ranking

Options are presented from lowest to highest risk:

`PRESENT < LOW < MEDIUM < HIGH`

- **PRESENT**: no higher-level conflict + positively confirmed by current/sibling evidence.
- **LOW**: no higher-level conflict but not positively confirmed.
- **MEDIUM**: conflicts with a bound profile/template/base rule.
- **HIGH**: conflicts with general architecture or a pattern hard invariant, including forbidden technical-derived contract dependency.

The host may add domain-specific refinements but must not invert these meanings silently.

## Output semantics

The output is a **reconciled document under the declared evidence/profile contract** plus a resolution ledger/appendix. This simple pattern does not claim the independent-review guarantees of the complex `DOCUMENT_RECONCILIATION_VERIFICATION` pattern.

If the host requirement explicitly needs independent review, bounded repair, or a separate final verification receipt, compose/select the complex pattern rather than silently extending this one.


## v1.2 hardening

### Protected semantic fields

The host generator can bind product-facing or otherwise authority-protected semantic fields. Evidence may challenge them, but no other discrepancy may mutate them indirectly. Any change requires a dedicated discrepancy and explicit authority decision.

### Analyst answer UX

Questions use stable `A/B/C/...` option labels after risk sorting, end with a short reply protocol, and include a complete example selecting `A` for every displayed question. This is part of the reusable behavior contract, not host-specific prose.


## v1.2 upgrade
Adds explicit input UX, evidence-authority isolation, provisional profile correction, causal-layer separation, version-drift classification, structured discrepancy rendering, Ukrainian stable option labels, narrow blocked semantics, and issue_summary decision auditability.
