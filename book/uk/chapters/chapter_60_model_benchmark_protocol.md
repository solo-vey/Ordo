# Розділ 60. Model Benchmark Protocol

## Навіщо цей розділ

Після M60.6 Ordo вже має стабільний no-API PathWalk dry-run baseline. Але dry-run baseline не є реальним benchmark-ом моделі: там ground-truth driver проходить дерево ідеально, тому всі метрики дорівнюють `1.0`.

M60.6.3 фіксує наступний шар: **протокол реального model benchmark-а**.

Головне правило:

```text
Dry-run proves wiring.
Model benchmark measures behavior.
Calibration requires variance.
```

## Чому не можна одразу міняти ваги

У M60.6.2 було підтверджено:

```text
60/60 cases passed
all component metrics = 1.0
metric variance = 0
```

Це означає, що dry-run показує готовність інфраструктури, але не показує, які ваги `path_quality_score` кращі.

Тому рішення M60.6.3:

```text
weights remain locked until real model or transcript evidence passes calibration gates
```

## Два дозволені режими benchmark-а

### API-driven benchmark

Модель реально проходить PathWalk-сценарії через harness.

В enforced mode вона має взаємодіяти тільки з runtime CLI:

```bash
./cli_embedded/ordo next-step . --format auto
./cli_embedded/ordo intake . --submit <NODE_ID> --answer-file <file>
./cli_embedded/ordo restore-session . --to-seq <N> --reason "..."
./cli_embedded/ordo verify-session .
```

Читати `compiled/*` напряму не можна.

### Transcript-replay benchmark

Замість live API береться вже записаний transcript поведінки моделі.

Це безпечніший перший pilot, бо він дозволяє перевірити scoring і failure buckets без витрат API та без нестабільності зовнішнього провайдера.

## Які artifacts має створити benchmark

Мінімальний набір:

```text
MODEL_BENCHMARK_PLAN.json
jobs/<job_id>.json
transcripts/<job_id>_transcript.json
scores/<job_id>_score.json
RAW_MODEL_METRICS.csv
SUMMARY.json
SUMMARY.md
MODEL_RUN_MANIFEST.json
CALIBRATION_DECISION.md
CALIBRATION_DECISION.json
```

Це важливо: модельний benchmark має зберігати не лише score, а й transcript evidence.

## Які метрики потрібні

`RAW_MODEL_METRICS.csv` має містити не тільки фінальний score, а й компоненти:

```text
path_quality_score
cell_match_rate
protocol_compliance_rate
distraction_recovery_rate
backtrack_accuracy
turn_accuracy_rate
invalid_branch_rejection_rate
skip_ahead_resistance_rate
clarification_handling_rate
correction_recovery_rate
restore_session_usage_rate
```

Окремо треба фіксувати:

```text
tool_call_count
turn_count
completion_latency_ms
failure_bucket
transcript_sha256
canonical_ir_hash
targets_manifest_hash
session_trace_hash
weights_hash
```

## Failure buckets

Невдалі або неідеальні проходження не можна просто складати в одну купу. Їх треба класифікувати:

```text
protocol_violation
wrong_branch
invalid_submit
missed_backtrack
distraction_followed
skip_ahead
clarification_failure
timeout_or_loop
runtime_error
scorer_error
```

Це потрібно, щоб не переплутати помилку моделі з помилкою runtime або scorer-а.

## Calibration gates

Ваги не можна міняти, якщо:

```text
- сценарії не однакові між runtime views;
- мало cases;
- усі scores знову 1.0;
- немає nonzero variance;
- failed cases не класифіковані;
- protocol violations не відділені від path-quality mistakes;
- немає transcript hash / runtime metadata hash;
- не зроблено manual review failed transcripts.
```

Практичне правило:

```text
Failing any calibration gate means: keep weights unchanged.
```

## Що це означає для наступних milestone

M60.6.3 не запускає real benchmark. Він тільки встановлює контракт, за яким benchmark можна буде запускати.

Наступний безпечний крок:

```text
M60.6.4 — Transcript Replay / Model Benchmark Pilot
```

А ідея M60.7/M61 про генерацію test cases з реального `source/program.ordo.yaml` лишається відкладеною, доки модельний benchmark protocol не буде перевірений на pilot evidence.

## M60.6.4 — transcript-replay pilot

M60.6.4 перевіряє цей protocol на маленькому executable pilot без live API.

Pilot створює:

```text
MODEL_BENCHMARK_PLAN.json
transcripts/*_transcript.json
scores/*_score.json
RAW_MODEL_METRICS.csv
SUMMARY.json / SUMMARY.md
MODEL_RUN_MANIFEST.json
CALIBRATION_DECISION.md / .json
```

У pilot навмисно є три типи evidence:

```text
perfect transcript → failure_bucket = none
distraction/model-quality miss → failure_bucket = distraction_followed
пряме читання compiled/* в enforced mode → failure_bucket = protocol_violation
```

Це важливо, бо після M60.6.2 dry-run мав нульову дисперсію. M60.6.4 показує, що transcript-replay шлях уже може створювати non-saturated metrics і failure buckets.

Але це ще не calibration run. Ваги лишаються locked, бо pilot малий і не проходить gates:

```text
sufficient_cases
repeatability_checked
confidence_summary_present
manual_failure_review_done
```

Практичний висновок:

```text
Transcript replay protocol works.
Calibration is still blocked.
Weights remain unchanged.
```
