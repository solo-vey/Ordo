# Runtime Prompt Application Order and Trace Evidence Validation

M71.4 validates the package-level runtime contract for stable prompt application.

The executable model selects the current node, gate, or artifact first. Only the selected object's `prompt_refs` may then be resolved. Same-phase refs preserve source-list order. Each ref resolves through `PROMPT_MANIFEST.json`, and the prompt file checksum must match before local use.

Recordable evidence contains `prompt_id`, `use`, `sha256`, and `ordinal`. It must not contain prompt text, hidden reasoning, or prompt-derived navigation. This is validation/readiness work; it does not introduce a prompt opcode or replace the existing CLI session-trace engine.
