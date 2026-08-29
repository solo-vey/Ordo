# Execution Modes Registry

| execution_mode | Meaning | Guarantee |
|---|---|---|
| `full_runtime` | External runner enforces state/gate transitions | highest |
| `chat_internal` | Model uses session-local code/files, but invocation remains model-driven | medium |
| `freeform_only` | Model follows instructions without enforced runtime | lowest |
