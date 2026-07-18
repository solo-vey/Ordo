# 020. Terminal Route Handling

**Backlog task:** `BL-BENCH-020`  
**Status:** implemented route/disposition contract

## 1. Purpose

Separate executor completion declarations from authoritative benchmark terminal decisions and handle every terminal consistently.

## 2. Canonical dispositions

| Disposition | Meaning | Artifact handling |
|---|---|---|
| `T_COMPLETED` | Required process and outputs completed | Seal current artifacts for evaluation |
| `T_INPUT_BLOCKED` | Required input/evidence cannot be supplied | Preserve partial artifacts as non-final; no invented completion |
| `T_SCENARIO_EXHAUSTED` | Scenario intentionally cannot yield a valid package | Seal evidence of exhaustion; expected outputs may be absent |
| `T_NOT_READY` | Work exists but mandatory readiness gate is open | Preserve draft versions and open gate list |
| `T_NO_GO` | Integrity, isolation, policy or invalid execution prevents valid benchmark use | Quarantine attempt; exclude from comparative scoring unless policy says otherwise |

`T_COMPLETED`, `T_INPUT_BLOCKED` and `T_SCENARIO_EXHAUSTED` correspond to canonical RUN routes. `T_NOT_READY` and `T_NO_GO` are operational dispositions and do not rewrite the RUN contract.

## 3. Decision authority

- executor may declare `completion_claim` only;
- Driver proposes a terminal candidate using current scenario state;
- terminal gate confirms the authoritative disposition;
- evaluator later checks route correctness but does not retroactively alter sealed execution evidence.

## 4. Mandatory terminal record

```text
attempt_id
run_id
terminal_disposition
terminal_reason_codes
state_snapshot_reference
current_artifact_versions
invalidated_artifacts
open_requirements
Driver_decision_reference
confirmed_at
```

## 5. Route-specific rules

### Completed
All required artifacts are current, approved where required, and no blocking gate remains. A premature executor completion claim is logged but rejected.

### Input blocked
The missing input is named, its necessity is evidenced, and the Driver has no authorized disclosure remaining. Partial artifacts cannot be promoted to ready.

### Scenario exhausted
The Driver confirms all relevant disclosure paths are consumed and the RUN contract expects exhaustion. The system must not fabricate a valid package to obtain completion.

### Not ready
Used for operational incompleteness such as open approval, invalidated artifact awaiting regeneration, or incomplete return package. It is retryable under the same logical RUN but requires a new attempt if execution is relaunched.

### No-go
Used for checksum failure discovered after start, isolation breach, wrong RUN/package binding, tampered log, unauthorized context or other invalidating conditions. Evidence is quarantined and contamination is explicit.

## 6. Final sealing gate

Exactly one terminal disposition must be confirmed. The log, output manifest and terminal record must agree on attempt identity and current artifact digests.
