# M74.0 Audit Decision Matrix

| Finding | Decision | Implementation line | Current effect |
|---|---|---|---|
| CSG validated without a model | Accept | M74.0 + M74.3 | Reclassify evidence; model benchmark remains not run |
| Constructs outside canonical registry | Accept | M74.1 | Add registry classes and blocking completeness diagnostics |
| Baseline contains process-history noise | Accept | M74.4 | Prepare separate public baseline, process archive, and book artifacts |
| APF remains a monolithic YAML | Accept with boundary | M74.5–M74.6 | Language prepares equivalence tooling; APF performs downstream decomposition |
| Hygiene tests fail after editable install | Accept | M74.2 | Separate dev-tree policy from release-archive cleanliness |
