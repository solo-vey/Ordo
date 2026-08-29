# alpha.20.0.138-dev

Fixes provider capability negotiation for structured outputs.

Root cause:
- provider capability probe correctly stored `capability_profile`;
- `_live_credentials()` correctly propagated it;
- `_provider_structured_output_mode()` ignored it;
- therefore custom providers in `auto` mode kept using `json_object` even after a successful strict-schema probe.

Now:
- recorded `supports_json_schema=true` for the same base URL/model/API style selects `strict_json_schema`;
- recorded `false` selects `json_object`;
- stale capability evidence for another model/endpoint is ignored;
- unprobed custom providers remain on the compatibility default;
- provider responses record structured-output resolution diagnostics.

This makes semantic-recovery enums/shape provider-enforced when the provider has demonstrated strict JSON-schema support.
