# Розділ 64. Спільний маршрут companion utilities

M61.3 фіксує простий практичний маршрут використання утиліт, які йдуть поруч з Ordo. Це не runtime layer і не benchmark runner. Це author/reviewer layer: спочатку подивитися дерево, потім згенерувати path/case/card artifacts, а потім за потреби підсвітити коментарі на графі.

## Чому потрібен окремий маршрут

Після M61.2 у пакеті є дві різні companion utilities:

```text
Visual Graph Generator
  → показує дерево Ordo YAML/IR як Mermaid/SVG/PNG

PathWalk
  → створює graph summary, terminal paths, clean/noise cases, review cards
```

Якщо їх просто покласти поруч без маршруту, користувач пакета не одразу розуміє, з чого починати. M61.3 відповідає на це питання.

## Рекомендований порядок

```text
source/program.ordo.yaml
  → Visual Graph Generator: подивитися дерево
  → PathWalk real-module-graph: отримати структурний summary
  → PathWalk real-module-paths: побачити terminal paths
  → PathWalk real-module-clean-cases: створити clean-path cases
  → PathWalk real-module-noise-cases: створити bounded-noise cases
  → PathWalk real-module-review-cards: створити readable scenario cards
  → Visual Graph annotation overlay: підсвітити коментарі або проблемні місця
```

## Що дивитися спочатку

Для автора або ревʼюера найкращий перший артефакт — це граф:

```bash
python3 utilities/ordo_visual_graph_generator/ordo_graph.py   source/program.ordo.yaml   --format svg   --out runs/companion_review/full_graph.svg
```

Якщо Graphviz недоступний, можна створити Mermaid:

```bash
python3 utilities/ordo_visual_graph_generator/ordo_graph.py   source/program.ordo.yaml   --format mmd   --out runs/companion_review/full_graph.mmd
```

## Далі — PathWalk artifacts

Після візуального огляду можна створювати структурні review artifacts:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-graph   --source source/program.ordo.yaml   --out runs/companion_review/graph   --force
```

Потім terminal paths:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-paths   --summary runs/companion_review/graph/REAL_MODULE_GRAPH_SUMMARY.json   --out runs/companion_review/paths   --force
```

Потім clean/noise cases і human review cards.

## Що це не доводить

Цей маршрут не доводить, що модель виконала testcase. Він не запускає runtime і не score-ить поведінку моделі. Він дає людині зрозумілі artifacts для аналізу.

Це принципова межа:

```text
visual/review artifacts ≠ runtime execution results
```

## Стабільна межа

На M61.3 companion utility layer має завершений практичний вигляд:

```text
Visual Graph Generator + PathWalk = author/reviewer toolkit
```

Runtime execution of generated testcases лишається окремим майбутнім milestone, а не частиною цього маршруту.
