# Measurement Model

Each valid run is evaluated on six dimensions:

1. Scenario completion correctness.
2. Control-flow correctness, including branches, loops, rollback, restore, and transitions.
3. State, trace, snapshot, and evidence integrity.
4. Artifact quality and completeness.
5. Validation and evaluator reliability.
6. Safe behavior under invalid, missing, contradictory, or irrelevant inputs.

The comparison unit is a scenario within a task example. Scenario scores may be aggregated only when the scenarios and scoring rules are explicitly identified.

Contaminated runs are excluded from quality comparison. Invalid test constructions are retained as test-design history but are not used as model-performance evidence.
