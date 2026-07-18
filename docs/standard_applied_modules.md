# Standard Ordo Applied Modules

Updated in M63.1.

## Current standard modules

### ordo.applied_project_factory

```yaml
module_id: ordo.applied_project_factory
package_path: packages/ordo_applied_project_factory/
version: 0.1.0-rc.1
lifecycle: release-candidate
is_standard_applied_module: true
parent_language_line: M62 line closure
source_base: 0.1.0-alpha.21
current_integration: M63.1 APF rc.1 package import
```

APF is a standard applied module for creating and improving applied Ordo process/playbook packages. It is not a companion utility and it is not part of the language runtime core.

Historical note: M62 imported APF `0.1.0-alpha.14` as the first package import point. That import is obsolete for current use and retained only as history.

## Boundary

Standard applied modules may demonstrate reusable language patterns, but those patterns are not automatically promoted to core IR/runtime semantics.
