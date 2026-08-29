# alpha.20.0.124-dev

Data Flow automatic layout now strictly separates data lanes from operation lanes.

Data lanes:
- Analyst input / collection
- Derived state
- Document
- Archive / package

Operation lanes:
- Transformation · input → state
- Transformation · state processing
- Transformation · state → document / materialization
- Transformation · document processing / rematerialization
- Transformation · document → package

A transformation/materialization node can no longer share a row with Analyst input, Derived state, Document, or Archive/package.
