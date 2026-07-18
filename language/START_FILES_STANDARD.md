# START files standard

Every Runtime Mode ready subject package should include:

```text
START_HERE_RUNTIME_MODE.md
START_PROMPT_RUNTIME_MODE.md
README.md
ordo.yml
source/program.ordo.yaml
compiled/
run_inputs/
tests/
output_templates/
reports/CLI_VALIDATION_SUMMARY.md
```

## `START_HERE_RUNTIME_MODE.md`

Contains the complete runtime instruction: loading protocol, source-of-truth rule, CLI pipeline, CLI truthfulness rule, fallback mode, no-memory-mode rule, gate discipline, artifact validation discipline, workspace rule, state handling, and short working protocol.

## `START_PROMPT_RUNTIME_MODE.md`

Contains only the minimal prompt:

```text
Ти працюєш у режимі AI Ordo Developer Runtime Mode.
Я завантажив Ordo package `<PACKAGE_ID>`.
Спочатку прочитай `START_HERE_RUNTIME_MODE.md` і далі працюй строго за ним.
Почни з runtime loading protocol і постав перше питання guided intake.
```

It must not duplicate the full runtime protocol.

## `reports/CLI_VALIDATION_SUMMARY.md`

A human-readable evidence file for actual CLI execution status. It must include `CLI status:`.


## M59.1 hard-stop rule

`START_HERE_RUNTIME_MODE.md` must explain the embedded CLI path, hard-stop fallback, and `DETERMINISM_NOT_ENFORCED` marker. `START_PROMPT_RUNTIME_MODE.md` remains minimal and must not duplicate these runtime details.
