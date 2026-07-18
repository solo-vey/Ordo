# Runtime artifacts

This directory contains generated runtime contracts. Execution-trace artifacts are created only when `execution_trace.supported: true`.

Required set:
- `execution_trace_config.yaml`
- `execution_trace_schema.yaml`
- `trace_event_mapping.yaml`
- `trace_redaction_policy.yaml`
- `trace_replay_policy.yaml`

`trace_adapter_contract.yaml` is additionally required for `runtime_mode: runtime_enforced`.
Actual traces are runtime outputs and are not authored here.
## Execution Trace adapter

When `execution_trace.runtime_mode` is `runtime_enforced`, this package must include `trace_adapter_contract.yaml` and a passing `trace_adapter_conformance_report.yaml`. APF defines the contract; the target runtime emits actual traces.
