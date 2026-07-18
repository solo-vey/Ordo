# Розділ 47. Two-tier rendering model

До цього моменту Ordo вже вміє перевіряти, чи підтверджені контракти дійшли до generated artifacts. Але виникає інша проблема: не всі output-шаблони однакові.

Одні шаблони прості. Вони містять лише підстановки на кшталт `{{ state.alias }}` або `{{ state.list | bullets }}`. Такі шаблони може безпечно рендерити CLI.

Інші шаблони складні. Вони містять цикли, умови, таблиці, traceability matrix, nested YAML blocks або ручні QA/automation сценарії. Такі шаблони не повинен рендерити простий deterministic renderer.

Тому Ordo вводить two-tier rendering model.

## Перший рівень: deterministic rendering

Deterministic template — це шаблон, який повністю підтримує CLI renderer `ordo.simple`.

```yaml
render_mode: deterministic
renderer: ordo.simple
requires_model_rendering: false
```

У ньому дозволені прості підстановки:

```text
{{ state.scalar }}
{{ state.list | bullets }}
{{ state.value | safe_name }}
{{ state.object | json }}
```

Але заборонені конструкції типу:

```text
{% for %}
{% if %}
loop.index
.items()
| default("...")
```

Якщо така конструкція потрапляє у deterministic template, `ordo lint` або `ordo generate-output` має впасти. Це важливо: CLI не має вдавати, що він розуміє складні AI-шаблони.

## Другий рівень: model-assisted rendering

Model-assisted template — це шаблон, який має рендерити AI model.

```yaml
render_mode: model_assisted
renderer: ai.markdown
requires_model_rendering: true
validation: strict_confirmed_state_only
tbd_policy: preserve_tbd_until_confirmed
```

CLI не рендерить такий шаблон напряму. Замість цього він створює handoff packet:

```text
runtime/model_assisted_render_handoff/<ARTIFACT_ID>.json
```

У цьому пакеті є:

- template content;
- confirmed state;
- expected output path;
- TBD policy;
- forbidden inference rules;
- post-validation requirements.

AI може заповнити складний Markdown/YAML/JSON artifact, але не має права вигадувати відсутні значення.

## Головне правило

Model-assisted rendering може використовувати тільки confirmed state і explicit TBD defaults.

Якщо значення не підтверджене, воно має залишитися як:

```text
⚠️ TBD
```

AI не має права прибрати TBD тільки тому, що “здається очевидним”.

## Post-validation

Після AI-rendering Ordo знову повертається в deterministic режим:

```text
validate-artifacts → consistency → go-no-go
```

Перевіряється:

- чи не залишились unresolved placeholders;
- чи валідний YAML/JSON;
- чи збігаються confirmed values зі state;
- чи не зʼявилися inferred values;
- чи не прибрано TBD без підтвердження.

Two-tier rendering model робить межу чесною: модель може допомогти зі складним документом, але фінальна перевірка знову deterministic.


## Стандартні помилки rendering layer

```text
ORDO-RENDER-001 deterministic template contains unsupported syntax
ORDO-RENDER-002 model-assisted template rendered by simple renderer
ORDO-RENDER-003 model-assisted output contains inferred unconfirmed value
ORDO-RENDER-004 TBD marker removed without confirmed state
ORDO-RENDER-005 model-assisted YAML output is invalid
ORDO-RENDER-006 model-assisted output not validated after rendering
```
