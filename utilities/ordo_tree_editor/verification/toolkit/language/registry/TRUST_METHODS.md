# Trust Methods Registry

| method | trust_class | Description |
|---|---|---|
| `mechanical` | `deterministic` | Code/runtime/script performs deterministic check. |
| `self_verification` | `model_judgment` | Model verifies with explicit evidence protocol. |
| `self_consistency` | `repeated_model_judgment` | Multiple independent model passes, aggregated by rule. |
| `human` | `human_decision` | Authorized human decision. |

## Compatibility rule

```text
mechanical → deterministic
self_verification → model_judgment
self_consistency → repeated_model_judgment
human → human_decision
```

Other combinations require explicit schema extension.
