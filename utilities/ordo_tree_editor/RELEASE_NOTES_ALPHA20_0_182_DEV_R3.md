# Ordo Tree Editor 0.2.0-alpha.20.0.182-dev

- Fixed Data Flow data-class propagation for the canonical Data Layer contract used by current playbooks.
- `Show Data Flow` now reads canonical `state_path_annotations.<path>.data_class` and falls back to `editor_projection.state_path_data_classes` when the canonical annotation is absent.
- Legacy `.181` `program_model.state.variable_metadata` declarations remain supported as a compatibility fallback.
- Canonical annotation has precedence over Editor projection; the Editor never guesses a missing class.
- Verified against `PASSPORT_CHANGE_PLAYBOOK_0.3.5_CANDIDATE_37_MODEL_RUN`: referenced graph variables now split into Business / Technical / Control / Metadata; only genuinely undeclared referenced paths remain Unclassified.
- No canonical Ordo runtime/compiler semantics changed.
