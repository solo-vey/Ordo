# Structured proposal continuity audit

This audit records the general enter→respond failure class found in real Ordo debug runs.

## Runtime invariant

For any node whose analyst interaction is confirmation/correction of a proposal:

1. enter may create an analyst-facing proposal;
2. respond must receive that exact proposal plus the canonical proposal contract;
3. analyst corrections are applied to the proposal, not reconstructed from scratch;
4. a richer reviewed schema may not be replaced by a narrower runtime schema;
5. partial object corrections merge over existing structured state instead of deleting unchanged fields.

## Real regression case

`N_TRIGGER_ATTRIBUTE_CANDIDATE_ANALYSIS` displayed the canonical columns:

- module
- data_type
- field_path
- field_type
- field_role
- calculation_relevance
- source_evidence
- analyst_status

The recorded analyst correction supplied concrete API fields and types. The model understood the correction, but emitted compact rows containing only `field`, `purpose`, `confirmed`, `type`, and optional `logic`. The following gate therefore rejected the rows because the reviewed canonical columns had disappeared.

The regression fixture `real_attribute_correction_schema_loss.json` reproduces this without network calls.

## Analogous canonical YAML patterns

### N_TRIGGER_ATTRIBUTE_CANDIDATE_ANALYSIS

`answer_type: table_confirmation_or_correction` with explicit `draft_generation.columns`. Requires schema-preserving table reconciliation.

### N_TRIGGER_CLIENT_VALUE_MAPPING

`answer_type: table_confirmation_or_correction` with canonical columns:

- source_field
- target_field
- transformation
- basic_fallback

The same table-schema preservation rule applies generically.

### N_TRIGGER_ALGORITHM_DRAFT

`answer_type: text_confirmation_or_correction` with `draft_generation.required_coverage`. A partial correction must not destructively replace an existing structured `trigger_logic` object. Runtime therefore supplies the prior proposal/contract and deep-merges object corrections over existing structured state.

### Identity/business-meaning proposal nodes

These also use enter→respond proposal semantics, but current examples usually provide full analyst corrections. Runtime now passes prior proposal context where the record declares confirmation/correction semantics; unrelated free-text nodes are not altered.

## Regression guarantees

- bare table confirmation preserves full proposal schema;
- confirmation plus corrections preserves canonical columns;
- canonical `draft_generation.columns` is authoritative even if Markdown rendering is incomplete;
- structured object partial correction preserves unspecified existing fields;
- unrelated free-text nodes are not schema-reconciled;
- previous route-authority, deterministic-gate, and source-collection regressions remain green.
