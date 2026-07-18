# Ordo Project Builder

`Ordo Project Builder` — це authoring-механізм для створення нових Ordo-проєктів через діалог PM з AI Ordo Developer.

## Головна ідея

PM не пише Ordo-код напряму. PM пояснює, який процес, домен або аналітичний продукт потрібен. AI Ordo Developer перетворює ці пояснення в Ordo YAML, перевіряє їх через CLI і компілює в Semantic JSON IR.

## Loop

```text
PM пояснює задум
  ↓
AI Ordo Developer уточнює і пропонує рішення
  ↓
AI оновлює Ordo YAML
  ↓
CLI helper перевіряє syntax / gates / compile
  ↓
AI пояснює PM-у стан людською мовою
  ↓
PM підтверджує, змінює або додає інформацію
```

## Роль AI Ordo Developer

AI Ordo Developer не є пасивним кодувачем. Він має:

- виявляти прогалини;
- пропонувати структуру Process Rail;
- радити щодо gates і state;
- пояснювати наслідки рішень PM;
- підтримувати YAML і Semantic JSON IR у валідному стані;
- не показувати raw CLI output без інтерпретації.

## Результат

Результатом authoring session є Ordo project, який має:

- `ordo.yml`;
- `source/program.ordo.yaml`;
- tests;
- output templates, якщо потрібні;
- compiled Semantic JSON IR;
- зрозуміле PM-facing summary.
