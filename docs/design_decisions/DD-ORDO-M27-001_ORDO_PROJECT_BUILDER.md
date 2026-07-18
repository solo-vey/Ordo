# DD-ORDO-M27-001 — Ordo Project Builder

## Статус

Accepted

## Контекст

Після M26 Process Rail став центральною моделлю Ordo. Наступний практичний крок — описати механізм, через який PM або аналітик створює нові Ordo-проєкти не через ручне написання YAML, а через діалог із AI Ordo Developer.

## Рішення

Додати `ordo.project_builder` як перший Ordo package для AI-guided authoring.

PM описує задум людською мовою. AI Ordo Developer ставить питання, проектує Process Rail, створює або оновлює YAML-файли, запускає deterministic helper checks і компілює Semantic JSON IR. CLI не спілкується з PM напряму; AI інтерпретує результати перевірок.

## Наслідки

- Authoring стає first-class сценарієм Ordo.
- PM не зобов'язаний писати Ordo YAML.
- AI Ordo Developer стає окремою роллю мови.
- CLI лишається deterministic helper layer.
- Semantic JSON IR є результатом authoring loop, а не тільки внутрішнім build artifact.
