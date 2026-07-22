# Розділ 63. Visual Graph Generator як companion utility

Visual Graph Generator — це утиліта для візуального огляду Ordo-програм. Вона читає `source/program.ordo.yaml` або сумісний YAML/IR і створює граф у форматах Mermaid, SVG або PNG.

Ця утиліта не є runtime core. Вона не виконує сесію, не викликає модель, не змінює YAML і не стверджує, що бізнес-логіка пройшла runtime validation. Її роль простіша й дуже корисна: показати структуру процесу так, щоб автор, ревʼюер або розробник могли її швидко зрозуміти.

## Де вона лежить

Починаючи з M61.2, утиліта входить у пакет так:

```text
utilities/ordo_visual_graph_generator/
```

Поруч із нею залишається PathWalk:

```text
utilities/ordo_pathwalk/
```

Ці дві утиліти не треба зливати в одну. PathWalk відповідає за тестові та review artifacts. Visual Graph Generator відповідає за візуальне пояснення дерева.

## Базове використання

Mermaid-граф:

```bash
python3 utilities/ordo_visual_graph_generator/ordo_graph.py \
  source/program.ordo.yaml \
  --format mmd \
  --out runs/visual_graph/program.mmd
```

SVG-граф, якщо встановлено Graphviz:

```bash
python3 utilities/ordo_visual_graph_generator/ordo_graph.py \
  source/program.ordo.yaml \
  --format svg \
  --out runs/visual_graph/program.svg
```

## Типовий author workflow

```text
1. Автор пише або отримує source/program.ordo.yaml.
2. Visual Graph Generator показує дерево процесу.
3. Автор перевіряє вузли, переходи, gates, artifacts і terminal branches.
4. PathWalk генерує terminal paths, clean cases, bounded noise cases і review cards.
5. Visual Graph annotation overlay може підсвітити проблемні або нові елементи графа.
```

## Annotation overlay

Окремий режим annotation overlay дозволяє підсвічувати елементи графа й додавати коментарі. Це корисно під час ревʼю: можна показати не тільки шлях, а й будь-який вузол, gate, state-поле, output або edge, який потребує уваги.

## Межа відповідальності

Visual Graph Generator має залишатися read-only utility:

```text
Ordo YAML/IR → graph artifacts
```

Він не повинен ставати runtime runner-ом, scorer-ом або benchmark harness. Якщо нам знадобиться автоматичне виконання згенерованих cases, це має бути окремий milestone, а не приховане розширення graph utility.
