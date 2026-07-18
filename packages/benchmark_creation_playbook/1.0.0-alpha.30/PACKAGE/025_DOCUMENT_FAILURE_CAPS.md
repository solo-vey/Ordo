# 025. Document Failure Caps

**Version:** 0.8.0  
**Backlog:** BL-BENCH-025  
**Status:** implemented

## Application rule

Only confirmed failures supported by the final artifact may trigger a cap. If several caps apply, the lowest cap wins. Caps never increase a score.

## Common caps

| Failure ID | Applies to | Maximum score |
|---|---|---:|
| `DCF-001-WRONG-CONTRACT` | all | 0 |
| `DCF-002-FABRICATED-CRITICAL-FACT` | all | 20 |
| `DCF-003-MISSING-PRIMARY-PURPOSE` | all | 40 |
| `DCF-004-CONTRADICTS-CANONICAL-CONTRACT` | derived views | 30 |
| `DCF-005-NO-TRACEABILITY` | all | 60 |
| `DCF-006-UNRENDERABLE-OR-UNREADABLE` | all | 40 |

## Artifact-specific caps

| Failure ID | Artifact | Maximum score |
|---|---|---:|
| `DCF-PAS-001-NO-CANONICAL-BEHAVIOR` | Passport | 40 |
| `DCF-PAS-002-UNTESTABLE-CONTRACT` | Passport | 55 |
| `DCF-JIR-001-NO-ACCEPTANCE-CRITERIA` | Jira | 60 |
| `DCF-JIR-002-NOT-A-DELIVERY-VIEW` | Jira | 55 |
| `DCF-IMP-001-NO-IMPLEMENTATION-SCOPE` | Implementation Prompt | 50 |
| `DCF-IMP-002-INVENTED-ARCHITECTURE-AS-REQUIREMENT` | Implementation Prompt | 35 |
| `DCF-MQA-001-NOT-EXECUTABLE` | Manual QA | 50 |
| `DCF-MQA-002-NO-PASS-FAIL-ASSERTIONS` | Manual QA | 60 |
| `DCF-AUT-001-NO-RUNNER-CONTRACT` | Automation | 45 |
| `DCF-AUT-002-FALSE-IMPLEMENTED-CLAIM` | Automation | 25 |

## Explicit non-failures for Jira

The following do not trigger a deduction or cap by themselves:

- absence of unit-test implementation details;
- reference to Passport instead of duplicating it;
- required sections appearing in a different order;
- concise payload description when detailed payload is canonically referenced elsewhere.

## Cap evidence record

Every applied cap must include failure ID, evidence location, finding, confidence, and resulting maximum score.
