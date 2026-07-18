# DD-ORDO-M26-001 — Process Rail як центральна модель Ordo

**Статус:** accepted  
**Milestone:** M26 — Process Rail Reframing  
**Дата:** 2026-07-06

## Рішення

Ordo трактується як **AI-guided process language**, а не як CLI-first runtime і не як повністю детермінований wizard.

Центральна модель Ordo — **Process Rail**: формалізована опорна структура процесу, яка допомагає ШІ вести живий діалог із людиною, але не втрачати маршрут, стан, gates, повернення назад, перевірки й правила генерації результату.

## Причина

Основна ціль Ordo — поєднати гнучкість ШІ з детермінованими частинами процесу.

ШІ має залишатися активним мислячим виконавцем: аналізувати, ставити питання, радити, інтерпретувати відповіді й пояснювати рішення. Process Rail не замінює це мислення, а стабілізує його.

## Наслідки

- CLI є deterministic helper layer, а не головний діалоговий runtime.
- Semantic JSON IR є машинозчитуваною формою Process Rail.
- Ordo має два ключові режими: AI-guided authoring і hybrid execution.
- Raw tool output не є human-facing output за замовчуванням; ШІ має інтерпретувати його людською мовою.
- Backtracking, correction handling і deviation/resume semantics є first-class concerns мови.
