# Розділ 79. Generic Template Tooling

M79 виносить роботу з шаблонами з окремих playbook-specific рішень у generic tooling layer.

Це окрема Python-утиліта в пакеті, подібна за роллю до Visual Graph Generator або PathWalk. Вона не є runtime core.

## Template Registry

Кожен керований template отримує registry record:

```text
template id
version
format
render mode
input contract
output contract
owner
compatibility metadata
```

Consistency gate перевіряє, що template references і registry не розходяться.

## Generic renderer

Renderer має єдиний interface незалежно від конкретного playbook-а.

Він отримує:

```text
template reference
confirmed input/state
render context
output destination
```

і повертає output та rendering evidence.

Renderer не повинен вигадувати відсутні business values.

## Generic review engine

Review engine перевіряє generated artifact за template contract і створює evidence format, придатний для machine та human review.

Перевіряються, зокрема:

```text
required sections
unresolved placeholders
confirmed-state consistency
format validity
TBD policy
```

## Version diff і breaking-change gate

Template version diff визначає зміни між версіями. Breaking-change gate блокує несумісну зміну, якщо вона не має явного migration decision.

## Реальні playbook-и

M79 перевіряє tooling щонайменше на двох реальних playbook-ах. Це важливо: generic tooling не вважається generic лише тому, що так названий його interface.

Головне правило M79:

```text
registry identifies;
renderer produces;
review engine verifies;
version diff protects compatibility.
```
