# 05. Gate and Assertion Model

## Gate

Gate — це контрольна точка, яка може дозволити, заблокувати, попередити або ескалювати виконання.

## v0.12 required fields

Кожен gate MUST мати:

```yaml
method: mechanical | self_verification | self_consistency | human
trust_class: deterministic | model_judgment | repeated_model_judgment | human_decision
```

## Method semantics

| method | Хто перевіряє | Клас довіри | Використання |
|---|---|---|---|
| `mechanical` | код/runtime/script | `deterministic` | формат, кількість, наявність поля, структурна перевірка |
| `self_verification` | модель за evidence-протоколом | `model_judgment` | семантична відповідність, фактологічна підтримка |
| `self_consistency` | N незалежних модельних проходів | `repeated_model_judgment` | критичні семантичні рішення |
| `human` | людина | `human_decision` | бізнесове, юридичне, незворотне рішення |

## Gate report

```json
{
  "id": "domain_pack.history_event.G_CONTRACT_CONFIRMED",
  "method": "self_verification",
  "trust_class": "model_judgment",
  "status": "passed",
  "evidence": {},
  "trace_source": "model_self_report"
}
```

## ASSERTION

`ASSERTION` — канонічний примітив для обовʼязкових і заборонених станів.

```yaml
assertion:
  id: A_NO_INVENTED_ALIAS
  polarity: not
  condition: alias_created_without_user_confirmation
  phase: [runtime, test]
  severity: block
  on_fail: STOP
```

## Projections

```text
ASSERT.NOT = runtime shortcut/projection of ASSERTION(polarity=not)
EXPECT.NOT = test projection of ASSERTION(polarity=not)
negative gate = gate/check projection of ASSERTION
```

Compiler MUST keep these projections traceable to the original `ASSERTION.DEF`.
