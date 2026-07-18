# M61 Companion Utilities Line Closure

Status: **stable utility line closed**.

M61 establishes the companion utility layer that travels with Ordo but stays outside the runtime core. This line is now closed at M61.3 plus this closure note.

## Stable tools

| Utility | Role | Stable use | Not responsible for |
|---|---|---|---|
| PathWalk | Testcase/review artifact utility | graph summary, terminal paths, clean cases, bounded noise cases, review cards | runtime execution, scoring, calibration |
| Visual Graph Generator | Read-only visual renderer | Mermaid/SVG/PNG graph views and annotation overlays | runtime execution, semantic validation, scoring |
| Ordo runtime CLI | Runtime core | session/runtime semantics | utility-only visualization or review-card generation |

## Stable workflow

```text
source/program.ordo.yaml
  → inspect visually with Visual Graph Generator
  → summarize and enumerate with PathWalk
  → generate clean/noise cases with PathWalk
  → generate human review cards with PathWalk
  → optionally annotate/highlight graph elements visually
```

## Stop rule

Do not keep extending M61 with small utility variants. Put new utility ideas into backlog unless they define a new coherent milestone.

## Future backlog

- M62.0: runtime execution of generated testcases.
- Backtrack/correction-backtrack conversational patterns.
- Scoring/calibration for executed generated cases.
- Process-boundary/watchdog hardening before broad execution matrices.
- Possible future utility unification only after both tools have stable independent usage.
