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
8. explicit approval перед фінальним package output.

## Ordo v0.12

Пакет використовує:

- `gate.method`;
- `trust_class`;
- `execution_mode: chat_internal`;
- `ASSERTION`;
- `CLARIFY.REQUEST`;
- `FREEFORM.maturity`;
- release validation через `ordo validate-release`.

## Команди

```bash
ordo lint packages/history_event_guided_intake
ordo compile packages/history_event_guided_intake
ordo test packages/history_event_guided_intake
ordo coverage packages/history_event_guided_intake
ordo run packages/history_event_guided_intake --answers packages/history_event_guided_intake/run_inputs/answers_success.yaml
ordo intake packages/history_event_guided_intake --answers packages/history_event_guided_intake/run_inputs/intake_success.yaml --non-interactive
ordo validate-release packages/history_event_guided_intake
```

## Межі MVP

Цей пакет ще не генерує повний final History Event analytical package. Він перевіряє першу контрольовану частину процесу: збір і валідацію контракту.
