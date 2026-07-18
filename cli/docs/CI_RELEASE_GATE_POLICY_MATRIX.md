# CI / Release Gate Policy Matrix

Status: `M69.0 accepted matrix`

| Scenario | Trigger | Profile | fail-on-warning | Required evidence | Expected blocker |
|---|---|---|---:|---|---|
| PR validation | pull request | standard | false | JSON repo hygiene report | `blocked` required root |
| Main branch validation | push to main | standard | true | JSON repo hygiene report | warning or blocked required root |
| Release candidate | manual/tag candidate | strict | true | report + revision provenance | warning or blocked release root |
| Final release | release/tag | strict | true | immutable report reference | any non-passed release root |
| Manual audit | manual | selected | selected | report optional | policy dependent |

## Root treatment matrix

| Root treatment | PR | Main | Release candidate | Release |
|---|---|---|---|---|
| required + release_blocking | check | check | check | check |
| required + non-blocking | check/report | check/report | check/report | check/report |
| optional | check if present | check if present | policy-selected | policy-selected |
| delegated | report only | report only | report only | report only |
| ignored | omit | omit | omit | omit |
| not_applicable | report as N/A | report as N/A | report as N/A | report as N/A |

## Status-to-gate mapping

| CLI status | fail-on-warning | Gate result |
|---|---:|---|
| passed | false/true | pass |
| passed_with_warnings | false | pass with evidence warning |
| passed_with_warnings | true | block |
| blocked | false/true | block |
| not_applicable | false/true | pass only when policy permits |

## Implementation status

- PR and main gates: implemented in M69.1.
- Version-tag/manual release gate: implemented in M69.2.
