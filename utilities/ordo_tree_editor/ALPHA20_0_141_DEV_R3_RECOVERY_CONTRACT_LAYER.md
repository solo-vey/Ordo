# alpha.20.0.141-dev

Closes a whole class of semantic-recovery structural variants.

## Generic recovery envelope
Equivalent outcome wrappers are normalized before validation:
- `{"resolved": {...}}`
- `{"needs_analyst": {...}}`
- `{"unsupported": {...}}`

The normalization is structural only and does not know domain fields.

## Capability evidence lifecycle
Provider JSON-schema probe evidence is cached by:
`provider + base_url + model + api_style`

This evidence survives new browser/run sessions for the same exact provider profile,
but never crosses to another model or endpoint.

The probe no longer rewrites the session's `auto` mode. `auto` resolves dynamically
from recorded capability evidence.

No playbook/domain source changed.
