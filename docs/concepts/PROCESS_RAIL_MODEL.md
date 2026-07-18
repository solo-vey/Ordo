# Process Rail Model

## Коротко

**Process Rail** — це опорна структура процесу для ШІ. Вона дозволяє ШІ вести гнучкий діалог із людиною, але тримає стан, маршрут, gates, обов'язкові рішення, повернення назад і правила результату.

Ordo не замінює ШІ детермінованим wizard-ом. Ordo дає ШІ рейки.

```text
AI thinks and speaks.
Process Rail keeps the process aligned.
Deterministic helper tools validate what can be validated.
```

## Проблема

- Prompt-only підхід гнучкий, але модель може пропустити крок, забути попереднє рішення або загубитися після повернення назад.
- Hardcoded wizard стабільний, але погано працює з відкритими відповідями, уточненнями, зміною думки й доменним мисленням.
- Ordo має дати проміжний варіант: живий ШІ-діалог, стабілізований формальною Process Rail.

## Основні частини Process Rail

- `rail_state` — поточний стан проходження.
- `rail_node` — поточний або доступний вузол процесу.
- `required_checkpoints` — обов'язкові точки, які не можна пропустити.
- `gates` — формальні перевірки дозволу рухатися далі або генерувати output.
- `deviation_policy` — що робити, якщо людина відійшла від поточного питання.
- `backtracking_policy` — як повертатися до попереднього рішення.
- `resume_policy` — як повернутися на основний маршрут після відхилення.

## Роль ШІ

ШІ залишається головним активним елементом. Він:

- інтерпретує природну мову;
- ставить уточнюючі питання;
- радить і попереджає про ризики;
- пропонує рішення;
- пояснює стан процесу;
- перетворює технічні результати інструментів у людське пояснення.

## Роль CLI

CLI не веде діалог із людиною. CLI допомагає ШІ:

- перевіряти синтаксис;
- компілювати Ordo source у Semantic JSON IR;
- перевіряти state/gates;
- знаходити missing fields;
- порівнювати state/IR;
- виконувати deterministic checks.

Raw CLI output не показується людині без потреби. ШІ інтерпретує його.

## Два сценарії

### AI-guided authoring

PM описує задачу природною мовою. AI Ordo Developer проектує Ordo-проєкт, створює YAML, запускає lint/compile і пояснює PM-у стан.

### Hybrid execution

Користувач проходить готовий Ordo-проєкт. AI Ordo Executor читає Semantic JSON IR, веде діалог, обробляє відхилення і використовує CLI як deterministic helper.

## Definition of Done

Process Rail model вважається зафіксованою, якщо:

- Ordo не описаний як CLI-first runtime;
- AI явно залишається активним cognitive executor;
- CLI позиціонується як helper/checker;
- Semantic JSON IR містить process rail semantics;
- backtracking/deviation/resume описані як частина мови.
