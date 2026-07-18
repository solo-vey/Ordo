# Розділ 70. APF rc.1 як release-candidate standard module

У M63.1 `ordo.applied_project_factory` оновлено з історичної точки імпорту `alpha.14` до `v0.1.0-rc.1`.

APF тепер фіксується як standard applied module, а не як випадковий example package:

```yaml
module_id: ordo.applied_project_factory
version: 0.1.0-rc.1
lifecycle: release-candidate
is_standard_applied_module: true
```

Важливо: APF-патерни не стали автоматично core opcode або IR-обʼєктами. У цій лінії вони лишаються module-local workflow, schema/documentation patterns або future candidates.

Known limitations:

- `FLOW.JOIN` і `SHARED.TAIL.REFERENCE` лишаються future IR candidates.
- `validate-factory-output` лишається APF-local / optional.
- `consistency: passed_with_warnings` не блокує rc.1, але warnings не приховуються.
