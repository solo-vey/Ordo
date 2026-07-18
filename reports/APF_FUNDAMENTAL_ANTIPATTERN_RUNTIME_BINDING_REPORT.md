# APF Fundamental Anti-pattern Runtime Binding Report

Status: **passed**

- Fundamental taxonomy: 12 active rules.
- Runtime detector level: 6 active subpatterns.
- Mapping: 6/6 detector rules mapped to active fundamental rules.
- New fundamental rule requires explicit project-owner approval.
- Process-specific failures remain examples, detector cases, subpatterns or regression fixtures.
- Focused runtime tests: 21/21 passed.
- Registry/schema tests: 4/4 passed.
- Modular source assembly: passed.
- Graph structural validation: passed.

Runtime compatibility is preserved: hooks continue to invoke detector-level IDs, while every gate report now exposes the corresponding fundamental anti-pattern IDs.
