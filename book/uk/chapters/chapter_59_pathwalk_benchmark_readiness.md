# Розділ 59. PathWalk Benchmark Readiness

У попередньому розділі ми додали безпечне повернення назад через `restore-session`. Це зробило PathWalk-сценарії з backtrack/correction технічно можливими в актуальному runtime-протоколі Ordo.

Але перед тим як запускати дорогі benchmark-прогони через зовнішні моделі, потрібна ще одна перевірка: чи сама утиліта тестування правильно підключена до поточного runtime-пакета.

Це і є задача **PathWalk Benchmark Readiness**.

## Навіщо потрібен readiness smoke

PathWalk не є частиною runtime core. Це companion-утиліта для перевірки того, як модель проходить Ordo-сценарії.

Тому перед реальними API-прогонами треба перевірити не модель, а саму інфраструктуру:

- чи PathWalk будує M60 runtime-пакет;
- чи використовує `./cli_embedded/ordo`, а не старий `ordo_run.py`;
- чи підтримує всі runtime view;
- чи читає правильні runtime artifacts;
- чи генерує score-файли;
- чи aggregate summary працює.

Це робиться дешевим no-API smoke-тестом.

## Matrix smoke

Команда:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli matrix-smoke \
  --out /tmp/pathwalk_matrix_smoke \
  --depth 2 \
  --branching 2 2 \
  --force
```

Вона перевіряє матрицю:

```text
enforced + json
enforced + ordo-code
enforced + json,ordo-code
```

Це не справжній тест якості моделі. У цьому режимі PathWalk сам проходить ground truth через embedded CLI. Мета — довести, що протокол, scorer і aggregator правильно зʼєднані.

## Які файли очікуються

Після smoke-тесту має бути структура:

```text
pathwalk_matrix_smoke/
  tree_source/
  scenarios/
    scenario_000.json
  sandboxes/
  transcripts/
  scores/
    scenario_000_json_score.json
    scenario_000_ordo-code_score.json
    scenario_000_json_ordo-code_score.json
    SUMMARY.json
    SUMMARY.md
```

Кожен score має містити:

```text
runtime_view
runtime_protocol_version
ordo_cli_version
canonical_ir_hash
targets_manifest_hash
session_trace_hash
```

Без цих полів результати різних прогонів не можна коректно порівнювати.

## Що readiness smoke не доводить

Matrix smoke не відповідає на питання:

- яка модель краща;
- які ваги `path_quality_score` правильні;
- як модель поводиться при rate limit;
- чи prompt достатньо стійкий до складного шуму.

Він відповідає тільки на одне питання:

> Чи PathWalk зараз сумісний з поточним Ordo runtime protocol?

## Правило для зовнішніх утиліт

Якщо зовнішня scenario-testing утиліта все ще потребує:

```text
python3 cli_embedded/ordo_run.py
```

або не підтримує:

```text
runtime_view
verify-targets
session.ordo.trace
restore-session
```

то вона не сумісна з актуальною M60-лінією.

Таку утиліту треба адаптувати до поточного мовного пакета, а не відкотити мовний пакет до старого runtime-протоколу.

## Головна формула

```text
Runtime CLI перевіряє один прохід.
PathWalk readiness smoke перевіряє, що сама тестова інфраструктура готова до багатьох проходів.
```

## M60.5.1: benchmark dry-run перед калібруванням

`matrix-smoke` перевіряє один сценарій у різних runtime-view. Але перед калібруванням ваг потрібен інший режим: багато сценаріїв без API-викликів, щоб зібрати сирі метрики.

Для цього додано:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli benchmark-dry-run \
  --out /tmp/pathwalk_dry_run \
  --scenario-count 20 \
  --runtime-view json \
  --runtime-view ordo-code \
  --runtime-view json,ordo-code \
  --force
```

Цей режим не тестує якість моделі. Він проходить ground truth через embedded runtime CLI і створює:

```text
RAW_METRICS.csv
SUMMARY.json
SUMMARY.md
scores/*_score.json
```

M60.5.1 також виправляє важливий blocker: dry-run більше не має повторно запускати embedded `verify-targets` / `verify-session` під час scoring, якщо ці звіти вже створив runtime-прохід. Scorer читає готові verification reports, а не запускає verification вдруге.

Головне правило:

```text
Matrix smoke показує, що підключення працює.
Benchmark dry-run збирає сирі метрики для майбутнього калібрування.
```

Калібрування ваг усе ще не входить у цей етап.


## M60.5.2b: зовнішній job-контракт для dry-run

Після перших dry-run спроб стало видно, що великий benchmark не варто вести одним довгоживучим parent-процесом. Кращий контракт такий:

```text
dry-run-plan
    ↓
dry-run-job для кожного scenario/runtime_view
    ↓
dry-run-collect
```

`dry-run-plan` створює `DRY_RUN_PLAN.json`, сценарії та runtime templates. Кожен `dry-run-job` виконує рівно один case. `dry-run-collect` збирає `RAW_METRICS.csv`, `SUMMARY.json` і `SUMMARY.md`.

Це важливо для реальних benchmark-прогонів: один завислий або проблемний case не має блокувати весь набір. Такий підхід також легше переноситься в CI, де кожен job можна запускати окремо.

## M60.5.4: artifact-only dry-run executor

M60.5.4 changes the recommended dry-run execution shape. Instead of relying on a
single long-lived Python process to run every scenario/runtime-view pair,
PathWalk now treats the benchmark as a set of artifacts:

```text
DRY_RUN_PLAN.json
jobs/<job_id>.json
job_scripts/<job_id>.sh
scores/*_score.json
RAW_METRICS.csv
SUMMARY.json
SUMMARY.md
```

The stable execution model is:

```text
dry-run-plan
    ↓
independent job execution
    ↓
dry-run-collect
```

This matters because benchmark jobs may call embedded runtime CLIs many times.
If one worker or subprocess has unusual lifecycle behavior, it must not hold the
entire benchmark parent process hostage. In M60.5.4, each generated job script
executes exactly one case and redirects stdin from `/dev/null`.

The convenience `benchmark-dry-run` command remains useful for local smoke
checks, but acceptance evidence should use the artifact-only plan/job/collect
flow.

## M60.6: calibration preparation baseline

M60.6 is the first stable baseline run for calibration preparation. It still does **not** calibrate weights and does **not** call a real model API.

The accepted baseline shape is:

```text
20 scenarios
× 3 runtime views: json, ordo-code, json,ordo-code
= 60 dry-run cases
```

The run uses the artifact-only execution contract:

```text
dry-run-plan
    ↓
independent job_scripts/*.sh
    ↓
dry-run-collect
```

The important output is not the temporary runtime sandbox. The important output is the compact evidence set:

```text
DRY_RUN_PLAN.json
jobs/*.json
job_scripts/*.sh
scores/*_score.json
RAW_METRICS.csv
SUMMARY.json
SUMMARY.md
```

For the M60.6 baseline all 60 dry-run cases passed. `RAW_METRICS.csv` was collected for future calibration analysis.

The rule after M60.6 is strict:

```text
Do not change path_quality_score weights from dry-run alone.
Dry-run prepares calibration. It does not perform calibration.
```

Real model/API benchmarks and real-module testcase generation remain future milestones.


## M60.6.1: clean-room release integrity hardening

After M60.6, the next safety gate is a clean-room archive check: unpack the release artifacts into a fresh directory and verify that the documented commands and generated artifacts still work outside the original build folder.

M60.6.1 fixes one important handoff issue: generated `job_scripts/*.sh` must not contain a baked absolute path to the temporary workspace used during generation. Instead, job scripts use this portable contract:

```bash
export ORDO_PATHWALK_ROOT=<workspace-or-pathwalk-rc-root>
export ORDO_CLI_ROOT=<developer-bundle-root>/cli  # only needed when PathWalk root has no cli/ordo
```

The script must fail fast if it cannot find `ordo_pathwalk/` or `cli/ordo/`. This keeps artifact-only execution deterministic without hiding environment assumptions.

This is a handoff/integrity fix only. It does not change M60.6 dry-run metrics, scoring weights, or runtime semantics.

## M60.6.2: calibration report refinement

M60.6.2 does not run a new benchmark and does not change scoring weights. It refines the interpretation of the M60.6 baseline.

The baseline is useful because it proves the artifact-only dry-run contract is wired correctly across the three runtime views:

```text
json
ordo-code
json,ordo-code
```

But the same baseline is not enough for calibration. All 60 dry-run cases passed and all component metrics were `1.0`:

```text
path_quality_score = 1.0
cell_match_rate = 1.0
protocol_compliance_rate = 1.0
distraction_recovery_rate = 1.0
backtrack_accuracy = 1.0
turn_accuracy_rate = 1.0
```

That means the dataset has zero variance. A zero-variance dry-run can confirm readiness, but it cannot show whether `cell_match_rate`, `protocol_compliance_rate`, `distraction_recovery_rate`, or `backtrack_accuracy` should receive different weights.

The M60.6.2 decision is therefore:

```text
Do not change path_quality_score weights from dry-run-only data.
Collect model/API or transcript-based runs with real variance before calibration.
```

Before real calibration, PathWalk needs evidence with non-perfect cases, failed cases, per-noise-type labels, repeated seeds/models, and a clear distinction between protocol violations and path-quality mistakes.
