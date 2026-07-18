# Fundamental Anti-pattern Taxonomy and Governance

## Canonical model

The package uses two levels:

1. **Fundamental anti-patterns** — broad failures in process-design approach.
2. **Subpatterns / detector cases / examples** — concrete manifestations used by runtime detectors and regression tests.

The canonical fundamental set contains **12 rules**. New process-specific failures must first be mapped to one of them.

## Owner-controlled rule

- New fundamental-level rules are forbidden without explicit project-owner approval.
- A new case is added by default as an example, subpattern, signal set or regression fixture.
- Fundamental names and definitions must remain independent of any specific process, artifact name, endpoint, fixture or project.
- The recommended total is 10–20 fundamental rules.

## Current detector mapping

| Existing detector pattern | Fundamental rule |
|---|---|
| `PROMPT_AS_IMPLEMENTATION` | `EVIDENCE_REALITY_MISMATCH` |
| `PACKAGE_VALIDATION_WITHOUT_COMPLETENESS_VALIDATION` | `INCOMPLETE_VALIDATION_MODEL` |
| `MANDATORY_BRANCH_SHORT_CIRCUIT` | `CONTROL_FLOW_INTEGRITY_VIOLATION` |
| `FINAL_LABEL_OVERCLAIM` | `STATUS_EVIDENCE_MISMATCH` |
| `SCOPE_CONFIRMATION_AS_IMPLEMENTATION_AUTHORIZATION` | `AUTHORIZATION_BOUNDARY_VIOLATION` |
| `COMPLEXITY_ROUTING_AND_EXECUTION_IN_ONE_NODE` | `RESPONSIBILITY_CONFLATION` |

## Source-derived cases

The History Event cases AP-01…AP-15 are retained as reference cases. They do not create fifteen new fundamental rules.
