# History Event Guided Intake Ordo Package

Перший великий практичний Ordo-пакет для керованого збору контракту нової історичної події.

## Призначення

Пакет проводить аналітика через guided intake:

1. бізнесова мета події;
2. вибір path;
3. alias;
4. українська та англійська назва;
5. source field;
6. value semantics;
7. QA scope;
8. QA scope;
9. Test Strategy Contract;
10. explicit approval перед фінальним package output.

## Ordo v0.12

Пакет використовує:

- `gate.method`;
- `trust_class`;
- `execution_mode: chat_internal`;
- `ASSERTION`;
- `CLARIFY.REQUEST`;
- `FREEFORM.maturity`;
- release validation через `ordo validate-release`;
- explicit release acceptance через `ordo accept-release` / `ordo validate-acceptance`.

## Команди

```bash
ordo lint packages/history_event_guided_intake
ordo compile packages/history_event_guided_intake
ordo test packages/history_event_guided_intake
ordo coverage packages/history_event_guided_intake
ordo run packages/history_event_guided_intake --answers packages/history_event_guided_intake/run_inputs/answers_success.yaml
ordo intake packages/history_event_guided_intake --answers packages/history_event_guided_intake/run_inputs/intake_success.yaml --non-interactive
ordo validate-release packages/history_event_guided_intake
ordo diff-release packages/history_event_guided_intake --base packages/history_event_guided_intake/reports/release_provenance_base.json
ordo generate-release-notes packages/history_event_guided_intake
ordo accept-release packages/history_event_guided_intake --decision accepted --approved-by "Human reviewer" --reason "Release evidence reviewed."
ordo validate-acceptance packages/history_event_guided_intake
```

## Межі MVP

Цей пакет ще не генерує повний final History Event analytical package. Він перевіряє першу контрольовану частину процесу: збір і валідацію контракту.


## M44 QA/Test propagation fix

Пакет тепер має окремий `N_TEST_STRATEGY_CONTRACT` після `N_QA_SCOPE`. Підтверджені test requirements автоматично мають потрапляти в усі ключові output artifacts: Passport, Jira Task, Implementation Prompt і QA Package.

Generated review artifacts:

```text
01_HISTORY_EVENT_PASSPORT_<ALIAS>.md
02_JIRA_TASK_<ALIAS>.md
04_IMPLEMENTATION_PROMPT_<ALIAS>.md
05_QA_PACKAGE_<ALIAS>.md
```

`ordo validate-output` блокує draft, якщо в цих артефактах немає required test sections.

## M54 Runtime Mode entry

This package includes `START_HERE_RUNTIME_MODE.md` and should be started through the runtime entry protocol:

```bash
ordo compile .
ordo runtime-entry .
ordo next-step .
```

The guided intake order must come from `compiled/program.ir.json` plus run state. If path `A` is selected, the runtime proceeds into the declared A-flow and must not ask A1/A2/A3/A4/A5 subquestions unless those nodes are explicitly present in the compiled IR.


## Runtime Mode standard

Start this package with `START_PROMPT_RUNTIME_MODE.md`; the detailed runtime rules live in `START_HERE_RUNTIME_MODE.md`.

Runtime source-of-truth:

```text
ordo.yml = manifest / entrypoint
source/program.ordo.yaml = editable source of truth
compiled/program.ir.json = runtime source for guided execution
run_state.json = current execution state
generated artifacts = rendered output
```

The guided step order must come from `compiled/program.ir.json` when it is current. After editing `source/program.ordo.yaml`, run `ordo compile` before guided execution. CLI evidence should be recorded in `reports/CLI_VALIDATION_SUMMARY.md`.


## M59.1 Runtime CLI note

Runtime profile builds of this package include `cli_embedded/ordo`. Start Runtime Mode through the embedded CLI when available. If the embedded CLI cannot run, hard-stop; deterministic Runtime Mode is not enforced until CLI evidence exists.

## M59.3 Runtime verification note

Runtime profile packages now support `cli_embedded/ordo verify-session .`. Final approval requires the user to run this command and paste `session-chain: intact`. If the chain is broken or the compiled IR canary leaks, the runtime session is invalid and must restart through CLI.


## M65.1 Prompt Registry adoption plan

M65.1 adds a concrete adoption plan for the M65.0 Prompt Registry standard.

The plan lives in:

```text
PROMPT_REGISTRY_ADOPTION_PLAN.md
PROMPT_REGISTRY_TARGET_STRUCTURE.md
PROMPT_REGISTRY_ADOPTION_MATRIX.md
PROMPT_REGISTRY_VALIDATION_PROFILE.md
PROMPT_REGISTRY_SMOKE_TEST_PLAN.md
```

This is a plan-only milestone. It does not yet add final prompt files or rewrite `source/program.ordo.yaml`.

Planned first prompt file for the next implementation milestone:

```text
prompts/hp.package.quick_start.v1.md
```

Prompt files will be supportive guidance only. They must not replace gates, state requirements, CLI Runtime Mode evidence, or human approval ownership.

## M65.2 Prompt Registry skeleton implementation

M65.2 implements the reviewed Prompt Registry adoption skeleton for this package.

For a tiny copy-paste startup prompt, use:

```text
prompts/hp.package.quick_start.v1.md
```

For full Runtime Mode rules, use `START_HERE_RUNTIME_MODE.md` and the embedded CLI protocol.

Node, artifact, and repair helper prompts are supportive guidance only. They do not replace gates, confirmed state, CLI evidence, artifact validation, or explicit approval.

Package-local prompt manifest:

```text
PROMPT_MANIFEST.json
```


## M66.1 Startup Package Profile

M66.1 applies the M66.0 `startup_package_profile` convention to this package.

Default startup mode:

```text
analyst_quick_start
```

Default analyst entry file:

```text
prompts/hp.package.quick_start.v1.md
```

Full Runtime Mode remains anchored in:

```text
START_PROMPT_RUNTIME_MODE.md
START_HERE_RUNTIME_MODE.md
cli_embedded/ordo
```

The startup profile is an entry/discoverability contract only. It does not override gates, confirmed state, CLI evidence, prompt-registry authority boundaries, or explicit human approval.

Package-local startup profile documentation:

```text
STARTUP_PACKAGE_PROFILE.md
```
