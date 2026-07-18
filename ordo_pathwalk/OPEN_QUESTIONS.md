# PathWalk open questions after M60.4 adaptation

## 1. Benchmark-pinned vs compatibility-current

Recommended answer: support both.

- `benchmark-pinned`: compare models against a fixed Ordo runtime package/hash.
- `compatibility-current`: test the latest Ordo workspace/runtime protocol.

Every score must keep explicit runtime metadata so runs from different Ordo
versions are not compared blindly.

## 2. Score weights

Do not treat the current default weights as final. First gather real runs across
`enforced+json`, `enforced+ordo-code`, `enforced+mixed`, `ir_readable`, and
`fully_freeform`. Use `--weights weights.json` for experiments, but keep raw
component metrics in every score.

## 3. Direct compiled/* audit completeness

The current scorer detects common direct-read commands in transcript tool calls.
This is useful but not a perfect security boundary. It is sufficient for
benchmark protocol compliance; it is not MCP/sandbox isolation.

## 4. Restore-session semantics

PathWalk now targets native M60.4 `restore-session`, not a local fork. Any future
change to rollback semantics must remain append-only and verifiable through
`verify-session`.

## M60.5 status update

`matrix-smoke` now provides a no-API compatibility gate. It does not resolve score-weight calibration. Before changing default weights, collect real benchmark runs and decide whether PathWalk is primarily used for model comparison, Ordo release QA, or research benchmarking.


## M76.4 resolution

Primary purpose is now fixed as `ordo_release_qa`. Model comparison is secondary and requires benchmark-pinned comparability. Default weights remain provisionally locked under `calibration_profile.json` until the real-model calibration eligibility gate passes.
