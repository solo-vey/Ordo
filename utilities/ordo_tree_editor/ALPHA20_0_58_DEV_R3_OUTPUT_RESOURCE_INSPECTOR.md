# alpha.20.0.58-dev — derived output/resource inspector

R3 generic UI/runtime-inspection fix.

- Derived `OUT::...` graph entities are now inspectable instead of routing-only.
- The inspector resolves producer nodes for the selected output path.
- Template/bindings/resource references are aggregated from those producers.
- The same Overview / Template / Parameters / References / Raw tabs are reused.
- Orphan outputs without an inspectable producer fail closed.
- No playbook/domain-specific semantics were added.
