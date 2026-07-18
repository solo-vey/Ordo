# Розділ 44. Прийом зовнішнього feedback після review

Після того як Ordo package передано на зовнішню перевірку, найнебезпечніша помилка — одразу почати виправляти все підряд.

У Process Rail це поганий шлях. Feedback має спочатку стати структурованим фактом, а вже потім рішенням.

```text
review finding → feedback item → triage → decision → milestone
```

## Чому не можна виправляти одразу

Зовнішній reviewer може знайти справжній blocker, корисне покращення, непорозуміння в документації або ідею, яка виходить за межі поточного release.

Якщо все це одразу змішати з кодом, release candidate перестає бути стабільним. Тому M49 додає не нову runtime-логіку, а шар прийому feedback.

## Feedback item

Кожне зауваження має бути записане як окремий item:

```text
id
area
severity
evidence
recommended_action
decision
target_milestone
status
```

Це дозволяє відокремити факт від рішення.

## Рішення

Для feedback використовуються прості статуси:

```text
accepted
accepted_with_scope_limit
needs_more_evidence
deferred
rejected
not_applicable
```

Наприклад, якщо reviewer каже, що CLI падає в CI, це може бути `blocker` і `accepted`. Якщо reviewer пропонує повністю переписати мову, це може бути `deferred` або `accepted_with_scope_limit`.

## Роль AI Ordo Developer

AI Ordo Developer не має одразу змінювати package. Спочатку він має:

1. розбити feedback на окремі findings;
2. класифікувати кожен finding;
3. записати evidence;
4. запропонувати decision;
5. назвати target milestone тільки для прийнятих пунктів.

Це продовжує головну ідею Ordo: модель може мислити гнучко, але процес має залишатися керованим.
