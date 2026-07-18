# Real Module Terminal Paths

Milestone: `M60.7.2`
Package: `sample.support_triage`
Source: `ordo_pathwalk/examples/m60_7_5_remaining_noise_testcases/source/program.ordo.yaml`
Start node: `N_ISSUE_SUMMARY`

## Counts

| Metric | Value |
|---|---:|
| terminal_paths | 3 |
| outputs_referenced | 1 |
| cycle_edges | 0 |
| dead_end_paths | 0 |

## Terminal paths

| Path | Branch signature | Terminal | Outputs |
|---|---|---|---|
| `TP_001` | `N_ISSUE_SUMMARY=* -> N_SEVERITY=high -> G_TRIAGE_COMPLETE` | `G_TRIAGE_COMPLETE` / `gate` | `OUT_TRIAGE_NOTE` |
| `TP_002` | `N_ISSUE_SUMMARY=* -> N_SEVERITY=low -> G_TRIAGE_COMPLETE` | `G_TRIAGE_COMPLETE` / `gate` | `OUT_TRIAGE_NOTE` |
| `TP_003` | `N_ISSUE_SUMMARY=* -> N_SEVERITY=medium -> G_TRIAGE_COMPLETE` | `G_TRIAGE_COMPLETE` / `gate` | `OUT_TRIAGE_NOTE` |

## Readiness

Terminal path enumeration ready: `True`
Clean path case generation ready: `True`
Noise case generation ready: `False`
Testcase generation ready: `False`
