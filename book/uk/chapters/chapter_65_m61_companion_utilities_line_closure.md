# Розділ 65. Закриття M61: стабільний шар companion utilities

M61 завершує формування шару утиліт, які йдуть поруч із Ordo, але не стають runtime core.

Цей шар потрібен для практичної роботи з мовою: подивитися дерево, зрозуміти шляхи, згенерувати clean/noise test cases і підготувати human-readable review cards.

## Що входить у стабільний шар

На межі M61 стабільними вважаються дві companion utilities.

**PathWalk** відповідає за artifact-only testing/review flow:

```text
source/program.ordo.yaml
  → graph summary
  → terminal paths
  → clean cases
  → bounded noise cases
  → review cards
```

**Visual Graph Generator** відповідає за read-only visualization flow:

```text
source/program.ordo.yaml
  → Mermaid / SVG / PNG graph
  → subtree / context / path views
  → optional annotation overlays
```

## Чого цей шар не робить

Companion utilities не виконують runtime-сесію і не доводять, що модель правильно пройшла процес. Вони допомагають автору й ревʼюеру побачити структуру, підготувати сценарії та перевірити логіку вручну.

Важлива межа:

```text
visual/review artifacts ≠ runtime execution evidence
```

## Чому M61 треба закрити

Після M61.3 зʼявився повний практичний маршрут:

```text
YAML → visual graph → paths → cases → review cards
```

Додавати ще дрібні варіанти шуму або часткові інтеграції без нового сильного milestone означало б знову потрапити в нескінченний блок покращень. Тому M61 закривається як стабільний utility layer.

## Що лишається на майбутнє

У backlog винесено:

- runtime execution of generated testcases;
- scoring and calibration for executed cases;
- process-boundary/watchdog hardening;
- `backtrack` і `correction_backtrack` patterns;
- можливе майбутнє обʼєднання утиліт тільки після того, як воно матиме окремий сенс.

Це не blockers для M61. Вони мають бути окремими майбутніми milestones.
