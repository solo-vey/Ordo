# Розділ 72. APF rc.1: класифікація мовних патернів

M63.3 фіксує важливу межу: APF `v0.1.0-rc.1` уже є standard applied module, але його внутрішні патерни не стають автоматично частиною ядра мови.

APF показує багато корисних ідей: input policy, progressive tree authoring, node/branch/subtree review, terminal output binding, template recipe, mock render і validation handoff tail. Але для release-candidate інтеграції вони лишаються або APF-local, або documentation/schema patterns, або future tooling candidates.

Найсильніші кандидати на майбутнє IR-рішення — `FLOW.JOIN` і `SHARED.TAIL.REFERENCE`. Вони винесені в backlog, бо потребують окремої стабільної семантики для source YAML і Semantic JSON IR.

Це дозволяє прийняти APF rc.1 без breaking migration: модуль уже корисний як прикладний процес, але core runtime не змінюється поспіхом.
