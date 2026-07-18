# Accepted Scorecard — Structured Instructions

**Implementation version:** alpha_1_3_0  
**Scoring profile:** TC03-EX02-EVAL-v1.1  
**Cell dimensions:** Process / Documents / Final

Process is playbook-pure and excludes result-packaging and analyst/Driver execution errors. Document scores are unchanged.

| RUN | Process | Documents | Final | Evidence |
|---|---:|---:|---:|---|
| RUN_01 | **99** | **96** | **98** | T_COMPLETED / GO |
| RUN_02 | **99** | **N/A** | **99** | NO_CHANGE |
| RUN_03 | **100** | **100** | **100** | T_SCENARIO_EXHAUSTED / NO_GO |
| RUN_04 | **100** | **97** | **99** | T_COMPLETED / GO |
| RUN_05 | **100** | **100** | **100** | T_INPUT_BLOCKED / NO_GO |
| **Weighted value** |  |  | **99.2** | mean Final across five RUNs |

## Executor–Evaluator Provenance

All accepted results in this scorecard were executed and evaluated in different chats using the same model (`GPT-5.6 Thinking`). Status: `different_chat_same_model`; user-attested, not cryptographically verified. See `06_manifests/EXECUTOR_EVALUATOR_PROVENANCE_LEDGER.json` from the case root.
