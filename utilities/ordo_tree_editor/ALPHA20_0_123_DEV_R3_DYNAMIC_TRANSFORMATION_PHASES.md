# alpha.20.0.123-dev

Transformations no longer occupy one global layer.

Automatic Data Flow phases are inferred from actual incoming/outgoing lineage:
1. Analyst input / collection
2. Transformation · input → state
3. Derived state
4. Transformation · state → document
5. Document / document-phase transformation
6. Transformation · document → package
7. Archive / package

State→state and document→document transformations remain in their data phase. Static package-source resources (templates, registries, bindings) are excluded from phase inference so reference files do not distort the causal position of materialization transformations.
