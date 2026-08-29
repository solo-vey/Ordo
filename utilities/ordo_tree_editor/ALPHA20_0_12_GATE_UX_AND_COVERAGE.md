# alpha.20.0.12 — Gate UX & Coverage Recognition

- Preserve underscores in machine IDs in rendered transcript Markdown.
- Keep assistant/model responses expanded by default; collapse only long analyst messages.
- Add an inline "Other / clarification" field for human-decision gates so analysts can submit a concrete correction context together with `on_fail`.
- Extend deterministic test coverage recognition with Ukrainian negative-result markers (`негатив*`, `відсутн*`).
- Prevent false `missing declared test coverage: negative` failures when the catalog already contains Ukrainian negative scenarios.
