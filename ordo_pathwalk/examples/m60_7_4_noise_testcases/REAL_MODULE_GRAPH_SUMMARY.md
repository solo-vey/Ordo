# Real Module Graph Summary

Milestone: `M60.7.2`
Package: `sample.support_triage`
Source: `ordo_pathwalk/examples/m60_7_3_clean_path_testcases/source/program.ordo.yaml`
Start node: `N_ISSUE_SUMMARY`

## Counts

| Metric | Value |
|---|---:|
| nodes | 2 |
| edges | 4 |
| branching_nodes | 1 |
| linear_nodes | 1 |
| dead_end_nodes | 0 |
| gates | 1 |
| assertions | 0 |
| outputs | 1 |
| unmatched_handlers | 2 |

## Branching nodes

| Node | Answer type | Branch answers |
|---|---|---|
| `N_SEVERITY` | `enum` | low, medium, high |

## Terminal / gate targets

| From | Answer | To | Target type |
|---|---|---|---|
| `N_SEVERITY` | `low` | `G_TRIAGE_COMPLETE` | `gate` |
| `N_SEVERITY` | `medium` | `G_TRIAGE_COMPLETE` | `gate` |
| `N_SEVERITY` | `high` | `G_TRIAGE_COMPLETE` | `gate` |

## Readiness

Graph summary ready: `True`
Path enumeration ready: `True`
Testcase generation ready: `False`
