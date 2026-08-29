# alpha.20.0.7 — StatePatch basis contract hardening

The runtime now tells the model that `basis` is provenance classification only and rule/action identifiers belong in `reason`. It also hardens strict response schemas at call assembly time, so plans compiled before V7.10 cannot expose an unconstrained `basis` string to a strict-schema provider. Runtime validation remains fail-closed.
