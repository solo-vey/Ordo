# VIBE MODEL_RUN

Minimal Model Mode execution profile. The model executes the canonical graph semantically; CLI authority and EDIT-only authoring surfaces are absent. Start with `START_PROMPT_MODEL_MODE.md`.

## Context/runtime efficiency contract
- Do not recursively read the package or enumerate-and-read files just in case.
- Do not preload the full `source/program.ordo.yaml`; locate the exact active node/gate and read only that element, continuing only as needed to finish the same element.
- Do not preload prompts or knowledge. Resolve only references declared for the active node.
- `authoring/` and `design/` are EDIT/authoring surfaces and must not be read during normal Model Mode execution.
- Package presence is not authorization to load content into model context.
- Keep filesystem scan volume, tool output and text actually loaded into model context as separate telemetry.
