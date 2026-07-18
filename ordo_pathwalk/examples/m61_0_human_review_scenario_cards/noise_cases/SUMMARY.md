# Real Module Noise Testcases

Milestone: `M60.7.5`
Package: `sample.support_triage`
Source: `ordo_pathwalk/examples/m60_7_5_remaining_noise_testcases/source/program.ordo.yaml`
Start node: `N_ISSUE_SUMMARY`
Patterns: `distraction, invalid_branch, clarification_without_submit, skip_ahead`

## Counts

| Metric | Value |
|---|---:|
| noise_cases | 12 |
| ready_cases | 12 |
| terminal_paths_input | 3 |
| patterns | 4 |

## Pattern counts

| Pattern | Cases |
|---|---:|
| `distraction` | 3 |
| `invalid_branch` | 3 |
| `clarification_without_submit` | 3 |
| `skip_ahead` | 3 |

## Cases

| Case | Pattern | Path | Terminal | Ready |
|---|---|---|---|---|
| `NOISE_TP_001_DISTRACTION` | `distraction` | `TP_001` | `G_TRIAGE_COMPLETE` / `gate` | `True` |
| `NOISE_TP_001_INVALID_BRANCH` | `invalid_branch` | `TP_001` | `G_TRIAGE_COMPLETE` / `gate` | `True` |
| `NOISE_TP_001_CLARIFICATION_WITHOUT_SUBMIT` | `clarification_without_submit` | `TP_001` | `G_TRIAGE_COMPLETE` / `gate` | `True` |
| `NOISE_TP_001_SKIP_AHEAD` | `skip_ahead` | `TP_001` | `G_TRIAGE_COMPLETE` / `gate` | `True` |
| `NOISE_TP_002_DISTRACTION` | `distraction` | `TP_002` | `G_TRIAGE_COMPLETE` / `gate` | `True` |
| `NOISE_TP_002_INVALID_BRANCH` | `invalid_branch` | `TP_002` | `G_TRIAGE_COMPLETE` / `gate` | `True` |
| `NOISE_TP_002_CLARIFICATION_WITHOUT_SUBMIT` | `clarification_without_submit` | `TP_002` | `G_TRIAGE_COMPLETE` / `gate` | `True` |
| `NOISE_TP_002_SKIP_AHEAD` | `skip_ahead` | `TP_002` | `G_TRIAGE_COMPLETE` / `gate` | `True` |
| `NOISE_TP_003_DISTRACTION` | `distraction` | `TP_003` | `G_TRIAGE_COMPLETE` / `gate` | `True` |
| `NOISE_TP_003_INVALID_BRANCH` | `invalid_branch` | `TP_003` | `G_TRIAGE_COMPLETE` / `gate` | `True` |
| `NOISE_TP_003_CLARIFICATION_WITHOUT_SUBMIT` | `clarification_without_submit` | `TP_003` | `G_TRIAGE_COMPLETE` / `gate` | `True` |
| `NOISE_TP_003_SKIP_AHEAD` | `skip_ahead` | `TP_003` | `G_TRIAGE_COMPLETE` / `gate` | `True` |

## Readiness

Noise cases ready: `True`
Runtime execution ready: `False`
Scoring ready: `False`
Calibration ready: `False`
