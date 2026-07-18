# Module Versioning Policy

Applies to: `ordo.applied_project_factory`

Current module version: `0.1.0-alpha.7`

Compatible language package: `Ordo 0.12.0-preview-rc1`

## Rule

`ordo.applied_project_factory` is a module/package inside the Ordo ecosystem and has its own versioning. It must not be numbered as if every change were a full Ordo language-package release.

## Inclusion model

```text
Ordo language package version X
  includes ordo.applied_project_factory version Y
```

The language package can evolve independently. When a new language package arrives, this module is adapted and released as a new module version.

## Historical mapping

The old `M61.x` labels are treated as internal development checkpoints only. They map to early alpha versions and are not the module's public versioning scheme.

## Practical rule for future work

Use filenames and reports like:

```text
ordo_applied_project_factory_v0_1_0_alpha_7_dev.zip
APF_0_1_0_ALPHA_7_VALIDATION_REPORT.json
```

Do not name module releases as full language-package milestones unless the whole language package is being released.

## M63.0 RC module import markers

This section records deterministic contract coverage markers for the M62 parent-language import.

- `module_versioning_policy`: `module_local_versioning_with_parent_language_import_at_explicit_version`
- `language_package_inclusion_model`: `standard_applied_module_in_m62_language_package`
- `module_version`: `0.1.0-rc.1`
- Parent language package: `0.12.0-preview-rc1`
