# alpha.20.0.16 — Runtime-owned model envelope adaptation

Release 1 live-model compatibility hardening derived from KF-007.

The runtime now distinguishes semantic model output from mechanical orchestration envelope fields when a provider only guarantees JSON-object output and does not enforce the compiled JSON Schema.

Allowed runtime-owned adaptations for `NodeExecutionResult`:

- derive missing `needs_analyst` from declared analyst interaction + phase/route shape;
- derive missing descriptive `next_intent` from the already supplied route/await state;
- derive missing non-authoritative `action` when the compiled contract requires it;
- reinterpret an object shaped exactly as a StatePatch envelope (`base_revision`, `operations`, optional `semantic_summary`) when Gemma incorrectly places it in `state_updates` or at top level.

The adapter MUST NOT invent or rewrite semantic state values, state paths, route keys, gate verdicts, check results, or business content.
Every adaptation is recorded in `semantic_model_attempts[].runtime_owned_envelope_adaptations`.
