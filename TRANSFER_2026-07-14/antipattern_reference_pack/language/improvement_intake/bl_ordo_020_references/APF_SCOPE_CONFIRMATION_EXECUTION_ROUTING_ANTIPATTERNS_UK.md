# Scope confirmation, complexity та execution routing: приклад і антипатерни

## Виявлений дефект

Після повідомлення `scope підтверджую` процес одразу заявив, що починає оновлення repository. Це було неправильно: підтвердження scope означає лише згоду з межами змін, а не дозвіл на implementation.

## Правильний rail

```text
SCOPE_CONFIRMED
→ CHANGE_COMPLEXITY_ASSESSMENT
→ EXECUTION_ROUTE_SELECTION
→ IMPLEMENTATION_AUTHORIZATION
→ CODE_IMPLEMENTATION
```

## Антипатерн 1: SCOPE_CONFIRMATION_AS_IMPLEMENTATION_AUTHORIZATION

**Симптом:** позитивна відповідь на scope автоматично запускає repository mutation.

**Причина:** semantic identity різних рішень не розділена.

**Рішення:** scope confirmation ніколи не встановлює `repository_mutation_authorized=true`.

## Антипатерн 2: COMPLEXITY_ROUTING_AND_EXECUTION_IN_ONE_NODE

**Симптом:** один вузол оцінює складність, пояснює ризики, обирає маршрут, отримує дозвіл і починає реалізацію.

**Ризик:** одна відповідь помилково підтверджує кілька незалежних рішень.

**Рішення:** окремі single-responsibility nodes для assessment, route selection та mutation authorization.

## Рекомендоване питання

Після оцінки складності користувачу показуються чотири варіанти:

1. **Реалізувати тут** — після цього ще потрібна окрема авторизація repository mutation; commit, push і PR не дозволяються автоматично.
2. **Підготувати пакет для розробника** — repository не змінюється; створюються implementation instructions, acceptance criteria, test plan і ризики.
3. **Підготувати лише proposed patch** — diff формується, але не застосовується.
4. **Залишитися на етапі аналізу** — implementation не запускається.

## Recovery

Якщо mutation ще не почалася, scope зберігається, repository лишається незмінним, процес повертається до `CHANGE_COMPLEXITY_ASSESSMENT`. Якщо mutation уже сталася без дозволу, подальші зміни блокуються, автоматичний rollback заборонений, а процес переходить до `UNAUTHORIZED_MUTATION_REVIEW`.

## Blocking gates

- `SCOPE-NOT-AUTHORIZATION-01`
- `COMPLEXITY-ASSESSMENT-REQUIRED-01`
- `EXECUTION-ROUTE-SELECTION-01`
- `REPOSITORY-MUTATION-AUTHORIZATION-01`
- `NO-IMPLEMENTATION-BEFORE-ROUTE-01`
- `PUSH-PR-SEPARATE-AUTHORIZATION-01`
