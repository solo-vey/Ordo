# alpha.20.0.48-dev — provider capability probe route fix

Fixes an R3 packaging/runtime defect where `/api/provider-capability-probe` had a valid POST handler but was omitted from the POST endpoint allowlist, causing the backend to return `Unknown API endpoint.` before dispatch.

No playbook/domain semantics changed.
