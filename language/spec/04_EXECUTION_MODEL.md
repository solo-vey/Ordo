# 04. Execution Model

Ordo execution moves through explicit state, nodes, paths, gates and handoff. Після Process Rail reframing execution є AI-led: AI Ordo Executor веде діалог, а Semantic JSON IR і CLI helper tools стабілізують маршрут.

## Execution modes

```text
full_runtime
chat_internal
freeform_only
```

| execution_mode | Хто викликає gate | Хто перевіряє | Рівень гарантії |
|---|---|---|---|
| `full_runtime` | код / runner | код або модель за протоколом | найвищий |
| `chat_internal` | модель | код у сесії / файлова перевірка / скрипт | середній |
| `freeform_only` | модель | модель текстом | найнижчий |

## Mandatory honesty rule

Ordo-програма має вказувати `execution_mode`, щоб користувач не плутав дисципліноване виконання в чаті з примусовим runtime-виконанням.

## Generator / critic pattern

Для семантичних перевірок рекомендовано розділяти генерацію і перевірку:

```yaml
path:
  - step: GENERATE
    role: generator
    id: S1

  - step: VERIFY
    role: critic
    id: S2
    sees:
      - contract
      - result_of: S1
    does_not_see:
      - generator_rationale
    method: self_verification

  - step: DECIDE
    id: S3
    outcomes: [accept, repair, escalate]
```

Critic не оцінює прихований rationale generator-а. Він оцінює результат щодо contract/evidence.


## Hybrid Process Rail loop

```text
human_input
  → ai_interpretation
  → rail_mapping
  → proposed_state_update
  → deterministic_helper_validation
  → ai_human_explanation
  → next_conversation_move
```

CLI/helper output є машинним feedback для AI. Людина не повинна бачити raw tool dump, якщо прямо не просить. AI має пояснити стан процесу людською мовою.

## Backtracking and deviation

Execution model має підтримувати ситуації, коли людина:

- відповідає не на поточне питання;
- дає додатковий domain context;
- просить пояснення;
- змінює попередню відповідь;
- повертається на кілька кроків назад.

Такі ситуації не є помилкою діалогу. Вони є Rail Deviation або Correction Event і мають завершуватися Rail Resume: AI повертає процес на маршрут після оновлення state і helper validation.


## EXECUTION_TRACE runtime lifecycle (M72.2)

When `execution_trace.enabled` is true, runtime MUST execute the following lifecycle:

```text
compile EXECUTION_TRACE.DEF
→ initialize trace before the first process step
→ append immutable events according to capture_level
→ redact sensitive payload keys before persistence
→ write terminal event and final_state
→ calculate integrity checksum
→ validate replay readiness and terminal invariants
```

The canonical persisted form is `ordo-execution-trace.v1` JSON. The default path is `runtime/execution_trace.json`. Runtime MUST reject appends after a terminal status. `minimal`, `standard`, `full`, and `audit` are filtering policies, not different trace schemas.

Replay semantics:

- `deterministic`: recorded inputs and selected decisions are authoritative;
- `re_evaluate`: recorded inputs are reused, but gates and decisions are recalculated;
- `simulation`: produces a plan without external side effects;
- `audit_only`: reads every event without process execution.
