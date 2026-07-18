# Startup Package Profile — History Event Guided Intake

**Milestone:** M66.1  
**Status:** package-local startup profile applied

This file documents how `startup_package_profile` is applied to the History Event Guided Intake package.

## Default startup mode

```text
analyst_quick_start
```

The default analyst entry is:

```text
prompts/hp.package.quick_start.v1.md
```

This file is intentionally small and points the analyst/AI to the normal runtime path without replacing gates, state, CLI evidence, or human approval.

## Runtime startup mode

Full Runtime Mode remains anchored in:

```text
START_PROMPT_RUNTIME_MODE.md
START_HERE_RUNTIME_MODE.md
cli_embedded/ordo
```

Runtime decisions must still come through CLI/helper evidence. The startup profile does not allow direct reading of `compiled/*` and does not weaken the Runtime Mode hard-stop fallback.

## Developer / review startup

Developers and reviewers should use:

```text
README.md
STARTUP_PACKAGE_PROFILE.md
PROMPT_REGISTRY_VALIDATION_PROFILE.md
PROMPT_MANIFEST.json
source/program.ordo.yaml
```

## Authority boundary

Startup files are allowed to guide entry, explain what to open first, and select the proper startup surface for the audience. They must not:

- override gates;
- silently confirm state;
- claim validation success;
- replace CLI evidence;
- bypass explicit approval;
- mutate runtime state by themselves.

## Readiness checks

The package-local startup readiness checks are declared in `source/program.ordo.yaml` under `startup_package_profile.readiness_gates`.
