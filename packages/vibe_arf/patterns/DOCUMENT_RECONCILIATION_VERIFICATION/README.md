# DOCUMENT_RECONCILIATION_VERIFICATION

Reusable Vibe data/execution pattern for taking a candidate **document** from an unverified state to a verified document backed by explicit reconciliation and review evidence.

## What this pattern is for

Use this pattern when a playbook must do more than validate document syntax. It is intended for processes where a document must be checked against an explicit semantic contract and, when relevant, grounded against external/domain evidence before it can be accepted.

Typical examples include requirements documents, implementation specifications, configuration specifications, API contracts, migration plans, compliance documents, operational procedures, and domain passports.

The reusable core is:

`candidate document -> findings -> evidence grounding -> reconciliation -> authority resolution -> reconciled document -> semantic acceptance -> bounded repair -> independent review -> final verification -> verified document + receipt`

The pattern deliberately does **not** define what is correct for a particular domain. Domain correctness is supplied by the host playbook through Data Layer bindings and allowed extension points.

## Core versus domain-specific responsibility

### Generic core owned by this pattern

The pattern owns the process invariants that should remain stable across domains:

- identify and freeze the document candidate being verified;
- discover explicit inconsistencies, omissions, unresolved markers, or contract violations;
- ground findings against declared evidence sources when the domain requires it;
- ensure every explicit finding receives a disposition before acceptance;
- separate evidence-resolvable findings from decisions that require authority;
- prohibit silent invention of domain rules or authority decisions;
- materialize a reconciled candidate;
- perform semantic acceptance against the same candidate identity;
- perform bounded repair and re-review when semantic defects exist;
- perform an independent review distinct from the primary reconciliation pass;
- bind review evidence to the candidate version being accepted;
- allow final verification only after resolution coverage, semantic acceptance, and independent acceptance;
- produce a verification receipt tied to the verified document and evidence.

### Domain-specific responsibility supplied by the host playbook

The host playbook must define or bind the following through project Data Layer information and allowed extensions:

1. **Verification contract** — what “correct and complete” means for this document type.
2. **Evidence context / grounding policy** — which code, systems, registries, schemas, laws, APIs, configurations, or other sources are authoritative or informative.
3. **Finding and reconciliation policy** — what kinds of inconsistencies matter and what dispositions are allowed.
4. **Authority-resolution policy** — which decisions may be resolved automatically from evidence and which require a human/domain authority.
5. **Semantic-acceptance policy** — acceptance criteria and review obligations after reconciliation.
6. **Independent-review policy** — what independence means and which evidence the second review may rely on.
7. **Bounded-repair policy** — maximum/allowed repair cycles and escalation behavior when convergence is not achieved.

Do not copy domain rules into the reusable pattern. Bind them from the project Data Layer or add them through one of the declared extension points.

## Required Data Layer bindings

A pattern instance must bind all required roles from `DATA_LAYER.template.yaml`:

| Role | Expected binding | Purpose |
|---|---|---|
| `candidate_document` | artifact | Candidate being verified |
| `document_identity` | information | Stable version/hash/revision identity |
| `verification_contract` | information | Domain definition of correctness |
| `evidence_context` | information | Allowed/required grounding sources and precedence |
| `finding_set` | information | Explicit findings/occurrences discovered during analysis |
| `resolution_ledger` | information | One disposition/evidence trail per explicit finding |
| `reconciled_document` | artifact | Candidate after accepted reconciliation/repair |
| `semantic_acceptance_evidence` | information | Primary semantic review evidence bound to candidate identity |
| `independent_review_evidence` | information | Independent review evidence bound to candidate identity |
| `convergence_status` | information | Whether bounded repair/review has converged |
| `verified_document` | artifact | Accepted document |
| `verification_receipt` | information | Final evidence/identity receipt for the verified document |

The existing project Data Layer remains canonical. The pattern must bind existing semantic objects where they already exist and instantiate missing ones only through the normal pattern Data Layer expansion mechanism.

## How Vibe should use this pattern

1. During **Data Layer authoring**, detect that the requirement contains a document reconciliation/verification responsibility.
2. Select this pattern before tree authoring. Do not wait until the graph/tree stage.
3. Create the pattern instance and bind its required roles to existing project information/artifact objects where possible.
4. Add the host playbook’s domain-specific policies as project Data Layer information and bind them through `verification_contract` and `evidence_context`; use only declared extension points for further specialization.
5. Materialize/merge the pattern Data Layer expansion into the canonical project Data Layer.
6. Derive the execution projection from `EXECUTION.template.yaml` mechanically. Tree authoring must not reselect or independently redesign the reusable responsibility.
7. Adapt prompts/validators/knowledge for contract-classified execution components using the bound domain information. The generic gates and process invariants must remain intact.
8. Run pattern-instance validation and generated-playbook regressions to prove that required roles, provenance, graph realization, and verification invariants remain satisfied.

## Execution-template interpretation

`EXECUTION.template.yaml` defines the reusable execution responsibilities and their order. As with the existing Vibe reusable patterns, the execution projection is intentionally structural: concrete pass/fail routing, retry routing, interaction details, and executor implementation are resolved by the host playbook while preserving the declared component responsibilities and gates.

The semantic and independent repair segments are intentionally explicit so the generated playbook cannot silently collapse “review found defects” into acceptance.

If Vibe chooses to reuse `VALIDATE_REPAIR_CONVERGENCE` internally for one of the bounded repair segments, that reuse is allowed only when the resulting host Data Layer and execution graph preserve all responsibilities and gates declared by this pattern. Do not create a second semantic truth or bypass this pattern’s acceptance requirements.

## Allowed extension points

The authoritative list is in `PATTERN.yaml`. Important extension points are:

- `domain_bindings`
- `verification_contract_identity`
- `evidence_source_identity`
- `reconciliation_policy`
- `authority_resolution_policy`
- `semantic_acceptance_policy`
- `independent_review_policy`
- `bounded_repair_policy`

Extensions may specialize domain behavior. They may not remove required roles or bypass coverage/acceptance/final-verification gates.

## What must not be carried into the reusable template

When this pattern is derived from an existing domain playbook, do **not** carry over:

- domain field names or domain-specific document sections;
- domain-specific pending markers or terminology;
- concrete legal/regulatory/API/code rules;
- concrete repository/module/template architecture knowledge;
- particular analyst answer options;
- fixed authority decisions;
- concrete node/gate IDs from the source playbook;
- domain-specific artifact filenames.

Those belong to the host playbook’s Data Layer, knowledge, prompts, validators, and bindings.

## Minimum invariants for generated playbooks

A generated playbook using this pattern should have regressions proving at least:

1. every required Data Layer role is bound;
2. no concrete execution node/gate IDs enter canonical Data Layer pattern instances;
3. every explicit finding is represented in the resolution ledger before acceptance;
4. authority-required findings cannot be silently auto-resolved;
5. semantic acceptance evidence is stale if the reconciled document identity changes;
6. independent review cannot be treated as passed without evidence bound to the accepted candidate;
7. repair/review cannot loop indefinitely without the host bounded-repair/escalation policy;
8. final verification cannot pass when resolution coverage, semantic acceptance, independent acceptance, or identity integrity is missing;
9. the verification receipt identifies the exact verified document and its supporting evidence;
10. domain-specific rules are supplied by bindings/extensions rather than hardcoded into the reusable pattern.

## Origin and intended reuse

This pattern was generalized from the document-reconciliation and verification lifecycle proven in `PASSPORT_CHANGE_PLAYBOOK_0.3.7`. The source playbook is provenance only; it is not a runtime dependency and no passport-specific semantics are required by this template.


## v1.1 execution-contract clarifications

v1.1 was produced by dogfooding the pattern against a passport↔code-module verification task. It closes three process gaps that a host must no longer invent:

1. **Every gate has explicit outcomes and destinations.** PASS/FAIL (or named outcomes) are part of the template contract, not host-authored process design.
2. **Authority interaction is split explicitly.** No-authority cases bypass the user; authority-required cases must ask for explicit authority and apply the answer deterministically before document materialization.
3. **Repairs invalidate stale acceptance evidence.** Any document mutation creates a successor identity, invalidates semantic and independent acceptance evidence for the old identity, and re-enters semantic acceptance before independent review.

The host still supplies domain facts through bindings. In particular, `evidence_acquisition_adapter` tells the generic `gather_domain_evidence` responsibility which code/module/repository or other evidence sources are legitimate for the domain.

## v1.2 compiler-hardening note

This revision preserves the prior process semantics and adds a mandatory compiler-valid lowering/preflight contract. See `COMPILATION_CONTRACT.md`.
