# Ordo Tree Editor 0.2.0-alpha.20.0.183-dev

- Fixed Data Flow Assistant compatibility parsing for providers that fall back from strict schema to JSON-object mode.
- Data Flow explanations returned under common textual aliases such as `analysis`, `message`, or `content` are normalized to `answer_markdown`.
- Added regression coverage for the observed custom/chat_completions `{\"analysis\": ...}` response shape.
- No canonical Ordo, compiler, or runtime execution semantics changed.
