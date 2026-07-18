# 07. FREEFORM Model

FREEFORM — це контрольований escape hatch для частин інструкції, які ще не варто або неможливо повністю формалізувати.

## v0.12 FREEFORM lifecycle

Кожен FREEFORM block може мати maturity lifecycle:

```yaml
freeform:
  id: FF_DOMAIN_EDGE_CASES
  role: domain_explanation
  maturity: volatile
  incident_count: 0
  incident_threshold: 3
```

## maturity values

| maturity | Значення |
|---|---|
| `stable` | пояснювальний блок стабільний, інцидентів мало або немає |
| `volatile` | блок змінюється, часто залежить від контексту |
| `candidate_for_formalization` | блок накопичив достатньо інцидентів для формалізації |

## Compiler/linter rule

Якщо:

```text
incident_count >= incident_threshold
```

лінтер MUST видати:

```text
WARNING: FREEFORM_FORMALIZATION_RECOMMENDED
```

## Formalization candidates

Recurring FREEFORM problems should be converted into one of:

```text
GATE.DEF
ASSERTION.DEF
NODE.DEF
TEST.DEF
Domain Pack rule
Library export
```
