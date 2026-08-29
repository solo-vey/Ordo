# Ordo Tree Editor executor regression fixtures

These tests are deliberately **small fixtures derived from real debug runs**, not full playbook snapshots.

They exist to test executor invariants rather than individual playbook IDs.

## Real-derived cases

### `real_source_collection_decision.json`
Derived from the source-collection loop seen in a recorded run where an analyst declined the "additional source" question.

The same semantic transition is tested in two implementation variants:

1. following gate declared as `human / human_decision`;
2. following gate declared as `deterministic` with a required input.

Invariant: if the canonical gate condition explicitly declares the immediately preceding analyst branch as completion evidence, both representations must proceed by that branch evidence. Runtime must not guess a boolean by parsing the required-input field name.

### `real_attribute_confirmation.json`
Derived from the real attribute-mapping retry loop.

The fixture stores a real assistant Markdown proposal table and a one-word analyst confirmation.

Invariant: a bare confirmation must preserve the structured proposal instead of asking a model to reconstruct the table from a one-word reply.

## Generic safety cases

- Missing deterministic required input => `UNRESOLVED`, never automatic `on_fail`.
- Present boolean `false` is distinct from a missing input.
- An unrelated deterministic gate cannot inherit an analyst branch merely because it follows an enum node.

## Run

```bash
python3 utilities/ordo_tree_editor/tests/run_regression_suite.py
python3 utilities/ordo_tree_editor/tests/replay_real_debug_fragments.py
```

The second command executes minimal runtime fragments through the editor's real executor functions without any network/model call. Recorded analyst/model-facing artifacts from the debug fixtures are used as replay inputs.

### `real_completed_respond_orchestration.json`
Derived from the 0.8.6 debug where `N_TRIGGER_SOURCE_BLOCK/respond` returned **both** a valid canonical `route_key: next` and `await_analyst: true` after successfully writing the complete source block.

Invariants:

1. an allowed model route and `await_analyst=true` are contradictory; runtime graph authority wins and the respond phase advances;
2. if the model omits the route but all canonical `on_answer.update_state` targets are present and YAML defines a fixed `on_answer.next`, runtime advances by that canonical route;
3. if only part of the canonical update targets is available, runtime may still wait for clarification and must not force completion.

This protects the executor generically from model-generated extra analyst turns after an already completed response.

## Structured proposal continuity

Regression coverage now includes enter→respond proposal continuity. See `STRUCTURED_PROPOSAL_AUDIT.md` and `fixtures/real_attribute_correction_schema_loss.json`. The executor passes prior proposal + canonical proposal contract into confirmation/correction responds, preserves table schemas, and deep-merges partial structured-object corrections.

## Contract-aware retry migration

A retry/review node that already owns structured state must treat that state as the baseline. If its stored rows are older or narrower than the current canonical `draft_generation.columns` contract, the runtime first performs deterministic migration from existing row aliases and already-present source/runtime context. It must not display fabricated `null` placeholders or regenerate a fresh proposal.

If deterministic migration cannot ground every required column, the retry enters constrained `schema_repair_existing_output` mode. The model may repair schema only from supplied evidence, must preserve all existing rows/values, must not invent evidence or identifiers, and must mark genuinely unavailable fields `UNRESOLVED` for analyst review.

## Full offline E2E replay

`OFFLINE_E2E_0_8_7_RESULT.json` records the end-to-end offline regression performed against the real 0.8.7 package using recorded analyst/model evidence where available and controlled synthetic responses for uncovered steps. The final verification run used **no forced-pass overrides** and reached `N_PROCESS_COMPLETED` after 93 enter/respond steps across 62 unique elements.

The E2E run exercises generic invariants added after real failures: branch-owned state writes, canonical nested state, retry proposal continuity, contract-aware schema migration (`missing` vs `UNRESOLVED` vs `NOT_APPLICABLE`), canonical table materialization, derivation contracts, validator artifact inference, and downstream-validator-scoped structural reconciliation.
