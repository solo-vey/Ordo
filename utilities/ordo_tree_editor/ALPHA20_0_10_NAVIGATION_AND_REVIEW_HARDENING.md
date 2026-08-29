# alpha.20.0.10 — Navigation & Review Hardening

- Live `Current: ...` status remains sticky below the inspector tab bar while the transcript scrolls.
- The graph workspace automatically centers the newly-current live node once per node change; manual scrolling is not continuously overridden.
- Recovery evidence reads `debug.alpha20.gate_failure` first, preserving deterministic gate failure detail.
- Semantic retry validation rejects `needs_analyst=true` for elements whose plan does not declare analyst interaction.
- Deterministic StatePatch execution validates collection values using `value_schema_by_path`.
- Runtime consumes `validation.blocking_issue_codes` from the semantic plan.
- Strict-schema fallback diagnostics are stored in `api_response._ordo_debug`; the original request payload is no longer mutated for debug display.
