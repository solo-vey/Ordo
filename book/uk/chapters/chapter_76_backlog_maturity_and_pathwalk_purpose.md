# Розділ 76. Синхронізація backlog, maturity-state і призначення PathWalk

Після великої кількості milestone-ів Ordo зіткнувся з організаційною проблемою: реалізація могла вже змінитися, а backlog і maturity-state документи ще описували попередній стан.

M76 вводить правило синхронізації керівних артефактів.

```text
implementation state
→ validation evidence
→ backlog status
→ maturity-state
```

Backlog не є журналом побажань, відірваним від коду. Якщо пункт закрито, повинно існувати evidence. Якщо реалізація ще не завершена, maturity-state не повинен створювати враження повної зрілості.

Окремо M76 уточнює роль PathWalk. Його основне призначення — не створити одну універсальну «оцінку якості моделі», а вимірювати проходження процесу за окремими компонентами:

```text
path correctness
protocol compliance
runtime integrity
compiled-read violations
noise recovery
```

Загальний score може бути зручним summary, але він не повинен приховувати причину помилки.

M76 також фіксує окремий backlog для graph cycles і dead-end paths. Цикл у графі не завжди є помилкою: review loop або correction loop можуть бути навмисними. Тому tooling повинен відрізняти допустимий цикл від нерозв'язного terminal-path enumeration.

Головне правило M76:

```text
maturity claims follow evidence;
benchmark purpose follows observable behavior;
graph warnings must preserve process semantics.
```
