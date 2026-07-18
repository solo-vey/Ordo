# Chapter 70. APF rc.1 as a Release-candidate Standard Module

In M63.1, `ordo.applied_project_factory` was updated from the historical `alpha.14` import point to `v0.1.0-rc.1`.

APF is now recorded as a standard applied module rather than an incidental example package:

```yaml
module_id: ordo.applied_project_factory
version: 0.1.0-rc.1
lifecycle: release-candidate
is_standard_applied_module: true
```

Importantly, APF patterns did not automatically become core opcodes or IR objects. In this line, they remain module-local workflows, schema/documentation patterns, or future candidates.

Known limitations:

- `FLOW.JOIN` and `SHARED.TAIL.REFERENCE` remain future IR candidates.
- `validate-factory-output` remains APF-local / optional.
- `consistency: passed_with_warnings` does not block rc.1, but warnings are not hidden.
