# alpha.20.0.139-dev

Adds structured runtime diagnostics to the Editor server console.

Every diagnostic line starts with:
`[ORDO_RUNTIME_DEBUG]`

Events include provider request/response, generic runtime guard attempts,
semantic recovery raw/validation/repair/halt.

API keys, tokens, passwords, secrets and headers are redacted.
Very large strings are truncated.

For a failed run, copy all `[ORDO_RUNTIME_DEBUG]` lines for that run and provide them to the implementation chat.
