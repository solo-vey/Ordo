# Розділ 66. APF як стандартний прикладний модуль

APF, або `ordo.applied_project_factory`, — це не утиліта і не runtime core. Це стандартний прикладний модуль, який іде разом із мовним пакетом Ordo та допомагає створювати або коригувати інші Ordo-процеси / playbookʼи.

Його місце в пакеті:

```text
packages/ordo_applied_project_factory/
```

## Навіщо потрібен APF

Звичайний користувач або PM не повинен писати `source/program.ordo.yaml` руками. APF веде його через людське ревʼю процесу:

```text
мета процесу
→ тип процесу
→ ролі
→ input policy
→ output catalog
→ дерево рішень
→ node/branch review
→ terminal output binding
→ source YAML generation
→ validation / handoff
```

Головна ідея: користувач підтверджує людське розуміння процесу, а модель перетворює це розуміння в Ordo source / IR.

## Чим APF відрізняється від utilities

Visual Graph Generator і PathWalk допомагають подивитися на процес збоку. APF — це сам процес створення процесів.

```text
APF = standard applied module
Visual Graph = read-only renderer
PathWalk = testcase/review artifact generator
Ordo CLI = deterministic validation/runtime tooling
```

## Як ревʼюїти APF

Після імпорту APF можна аналізувати тим самим companion route, який уже є в пакеті:

```text
packages/ordo_applied_project_factory/source/program.ordo.yaml
  → Visual Graph Generator
  → PathWalk real-module-graph
  → PathWalk real-module-paths
  → PathWalk clean/noise cases
  → PathWalk review cards
```

Це не замінює source YAML і JSON IR. Це review aids, які допомагають побачити структуру, terminal paths і сценарії.

## Межа M62.2

M62.2 тільки документує APF як стандартний модуль. Він не переписує гілки APF, не вводить нові op-коди та не запускає execution/scoring generated testcases.

Наступний логічний крок — класифікувати APF language-pattern candidates: що лишається документаційним pattern, що стає APF subflow, що потребує schema convention, а що колись може стати IR/runtime construct.

## Важливе уточнення про PathWalk

Повний маршрут `graph → paths → clean/noise cases → review cards` є стабільним для процесів, де terminal paths можна перелічити без невирішених циклів. APF сам є self-hosted authoring process із review loops, тому для імпортованого `v0.1.0-alpha.14` PathWalk graph summary працює, але terminal path / testcase generation для самого APF може бути заблокований cycle edges. Це не помилка M62.2: адаптація APF до cycle-aware testcase generation має бути окремим майбутнім кроком.
