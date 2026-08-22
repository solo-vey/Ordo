# Information-First / Authority-First Authoring Protocol — alpha.26

## Purpose
Vibe designs generated playbooks from required information and authority semantics first. The executable Ordo graph is a later projection of a validated authoring model.

## Canonical design-time layers
1. Outcome and artifact discovery.
2. Artifact decomposition into required information objects.
3. Information-object mini-passports.
4. Semantic information groups.
5. Typed information dependency topology.
6. Validation, authority, provenance and lifecycle rules.
7. **Review-bundle compilation** for analyst-minimal interaction.
8. **Proposal quarantine / approved projection / canonical truth** separation.
9. Progressive interaction projection.
10. Ordo graph synthesis.
11. Bidirectional AIM ↔ Ordo traceability validation.
12. Scenario/Auto Answers synthesis.
13. Pinned-runtime simulation preflight and defect ownership.
14. Analyst visibility only after required machine evidence is green.

## Information object contract
Each object should declare a stable ID, kind, value contract, requiredness/cardinality, valid value states, lifecycle, origins/producers, consumers, semantic group, provenance expectations and validation/approval responsibility where applicable.

Value state and validation state are independent. `unknown` and `not_applicable` are legitimate explicit value states when allowed by the domain; they are not synonyms for invalid data.

## Review bundles are not information groups
Semantic groups organize domain meaning. Review bundles optimize human interaction. A bundle is compiled from AIM dependencies, authority ownership, uncertainty and cognitive load. Analyst-visible review should primarily expose fields requiring authority or uncertainty resolution; already-supported/derived fields can remain silent unless needed as context.

## Proposal is not canonical truth
Model proposals are hypotheses. Keep separate roots for proposal state, approved projection and canonical state. Rejected or unconfirmed proposal fields must not materialize into canonical artifacts. Materializers consume approved/canonical projection, never a blind deep merge of proposal state.

## Approval ledger and local persistence
Human authority is persisted as append-only/revisioned evidence. A new approval must not erase prior independent approvals. After a human authority apply, an immediate local deterministic gate verifies persistence before downstream stages rely on it.

## Lifecycle
Typical validation states are `draft`, `validated`, `approved`, `stale`. Mutation of validated information invalidates affected evidence and downstream dependent evidence until the relevant gate reruns.

## Recovery locality
Recovery should be derived from causal AIM dependencies. When a gate fails, return to the nearest known remediation producer/authority point rather than restarting a broad process stage when a narrower causal repair is available.

## One topology, many projections
Information, evidence and artifacts live in one typed topology. Variable flow, artifact flow, human interaction, validation, provenance, recovery and process graph are projections of the same source model.

## Ordo boundary
AIM, review bundles, proposal quarantine and approval-ledger metadata are Vibe authoring concepts, not Ordo syntax extensions. Runtime behavior must compile to ordinary canonical Ordo constructs.

## Verification
Before graph synthesis, `validate_authoring_information_model.py` and the alpha.26 authoring validators must pass. After synthesis, `validate_information_projection.py --require-bound` must pass. Before analyst-ready handoff, the required scenario matrix and pinned runtime simulation/evidence validators must pass when applicable.
