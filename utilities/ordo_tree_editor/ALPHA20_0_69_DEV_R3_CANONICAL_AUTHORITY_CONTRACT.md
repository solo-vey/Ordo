# alpha.20.0.69-dev — canonical authority contract

R3 generic authority/binding hardening.

- Adds source-declared `authority_contract` support for model derivation nodes.
- Compiler fails closed when authority-derived targets are not writable, declared sources are not inputs, clarification-only fields overlap/write from the derivation node, or open-question state is not writable.
- Runtime requires authority-derived fields to be populated when declared canonical sources are available.
- `must_include_from` selectors mechanically require selected canonical literals to survive in the derived target. Wildcard selectors over arrays are supported.
- Generic/default values that omit required canonical semantics are rejected inside the bounded model retry loop.
- Existing derived targets are reusable only when they still satisfy the current canonical-literal contract.
- Clarification-only fields may not be invented by model derivation.
- `open_questions_path` is runtime-owned and normalized from genuinely missing clarification-only fields.

The Editor does not know Risk Factor domain values. All authority relationships and selectors are declared by the playbook source.
