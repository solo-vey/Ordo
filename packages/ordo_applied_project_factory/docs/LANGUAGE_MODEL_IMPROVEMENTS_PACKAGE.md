# Ordo / APF — пакет покращень мовної моделі та process-model

**Дата фіксації:** 2026-07-08  
**Контекст:** розробка та ревʼю `ordo.applied_project_factory` у межах Ordo `0.12.0-preview-rc1`  
**Поточний APF-реліз:** `v0.1.0-alpha.14`  
**Поточна точка runtime-review:** гілка 1 → `Node review`; review тимчасово зупинено для формування цього пакета.

---

## 1. Призначення документа

Цей документ збирає всі покращення, які були сформовані під час поточної розмови як пакет змін до мовної/process-моделі Ordo та до прикладного модуля `ordo.applied_project_factory`.

Документ розділяє:

- вже внесені зміни в APF `v0.1.0-alpha.14`;
- підтверджені, але ще не внесені structural corrections;
- зміни, які мають стати мовними / IR-level патернами, а не лише локальною поведінкою одного модуля;
- відкриті місця для наступного patch.

---

## 2. Короткий статус

| Напрям | Статус |
|---|---|
| 4-та стартова гілка “Коригування існуючого процесу” | внесено в APF `alpha.14` |
| Minimal validation після `alpha.14` | пройдена |
| Full validation | deferred до shared terminal/pre-handoff gate |
| Гілка 4 | review закрито |
| Гілка 1 | review триває; зупинено на `Node review` |
| Гілка 2 | ще не закрита node-by-node |
| Shared output template / terminal binding model | підтверджено концептуально, patch pending |
| Progressive tree authoring model | підтверджено концептуально, patch pending |

---

## 3. Уже внесено в APF `v0.1.0-alpha.14`

### 3.1. Нова стартова гілка: “Коригування існуючого процесу”

Додано четвертий режим старту:

```text
N_FACTORY_MODE_SELECTION
→ 4. Коригування існуючого процесу
```

Сенс гілки: не створення нового процесу з нуля, а зміна вже існуючого процесу.

### 3.2. Baseline existing process

Для коригування існуючого процесу baseline може бути лише одним із двох варіантів:

```text
1. Повний workspace / dev package archive
2. self-contained source/program.ordo.yaml
```

Варіанти на кшталт “людський опис процесу” або “старі notes” прибрані як insufficient baseline, бо це вже не correction, а reconstruction / creation from scratch.

### 3.3. Два режими коригування

Гілка 4 підтримує два режими:

```text
1. Batch improvement list
2. Targeted dialogue improvement
```

#### Batch improvement list

Користувач надає список покращень, файл або текст. AI:

1. витягує candidate improvements;
2. дає користувачу обрати, які застосовувати;
3. мапить improvements на вузли / gates / state / artifacts;
4. показує before/after affected nodes;
5. формує confirmed change set;
6. застосовує scoped YAML patches;
7. запускає minimal validation.

#### Targeted dialogue improvement

Користувач вказує конкретну проблему або елемент процесу. AI:

1. допомагає знайти target process item;
2. уточнює бажану зміну;
3. показує before/after proposal;
4. дає рішення по зміні: approve / correct / defer / reject;
5. питає, чи є ще точкові покращення;
6. накопичує approved / rejected / deferred changes;
7. переводить їх у confirmed change set.

### 3.4. Shared pipeline join замість дублювання full validation

Гілка 4 не має власного дубліката:

```text
full validation
handoff readiness
correction loop
```

Замість цього вона завершується так:

```text
4-та гілка
→ confirmed change set
→ scoped YAML patches
→ minimal validation
→ JOIN existing shared full-validation / handoff pipeline
```

Це важливий мовний патерн: нові branch-specific flows мають приєднуватися до shared tail, а не копіювати його.

---

## 4. Покращення process-design review rendering

### 4.1. Явне маркування режимів

Під час design/review процесу runtime має завжди показувати, у якому режимі він працює:

```text
- tree traversal
- branch selection
- node-review decision
- branch-review decision
- execution / validation gate
- post-patch review
- branch closure
```

Це усуває плутанину між:

```text
реальним вибором користувача в майбутньому процесі
vs
поточним review-рішенням по самому вузлу дерева
```

### 4.2. Обовʼязковий current-node display block

Кожен вузол у review має показувати:

```text
- current mode
- current node / branch
- human description
- question / action
- state
- gates
- artifacts / outputs
- open / deferred / sibling branches
- expected user decision
```

### 4.3. Control-action bookkeeping

Для кожного review-рішення потрібно розрізняти:

```text
selected_control_action
not_selected_control_actions
blocked_until_ready_actions
unreviewed_sibling_branches
deferred_return_points
```

Це не одне й те саме. Наприклад, “не вибраний control action” не означає “неперевірена sibling-гілка”.

---

## 5. Гілка 1 — “Доменна модель + дерево рішень”: підтверджені corrections

Гілка 1 зараз проходить human process review. Вона є в YAML, але ми не вважаємо її закритою, поки не завершено node-by-node / branch-by-branch review.

### 5.1. Великий контекстний вузол треба розбити

Було некоректно пакувати все в один вузол:

```text
Базовий контекст прикладного проєкту
```

Правильна атомарна послідовність:

```text
1. Мета прикладного проєкту
2. Тип процесу
3. Runtime roles
4. Domain model overview
5. Input artifacts / sources / input policy
6. Output artifact catalog
7. Terminal output binding + template verification loop
8. Open questions review
9. Runtime entry point
10. Progressive tree authoring
11. Standard node/branch review
```

### 5.2. Runtime entry point перенесено нижче

`Runtime entry point` не має визначатися одразу після roles. Його логічніше визначати після:

```text
- domain model overview
- input policy
- output artifact catalog
- open questions review
```

Бо entry point є похідним рішенням: щоб зрозуміти, з чого стартує runtime-сесія, треба вже знати предметну область, можливі inputs/outputs і відкриті питання.

### 5.3. Input та output треба розділити

Початковий вузол `Input / output sources` треба розбити на два:

```text
1. Input artifacts / sources / input policy
2. Output artifact catalog
```

Причина: input і output мають різні контракти, різні state-поля, різні gates і різні review-цикли.

---

## 6. Input artifacts / sources / input policy

### 6.1. Input artifacts не мають бути обовʼязковими

У реальному процесі користувач може не мати нічого на вході, або сам процес може не регламентувати input на цьому етапі.

Тому вузол має фіксувати не “список input artifacts”, а `input_policy`.

Допустимі стани:

```text
- inputs required
- inputs optional
- no predefined input
- inputs unknown / deferred
- inputs will be produced later in the process
```

### 6.2. Gate для input policy

Неправильно:

```text
не можна йти далі, поки input artifacts не визначені
```

Правильно:

```text
не можна йти далі, поки не зафіксовано input policy
```

---

## 7. Output artifact catalog

### 7.1. Output artifacts можуть бути неповними або невідомими

Користувач не завжди знає на старті, які документи будуть формуватись у кінцевих точках.

Тому output catalog має підтримувати:

```text
- known output artifacts
- partially known outputs
- AI-proposed outputs
- optional outputs
- deferred outputs
- no document outputs
```

### 7.2. Candidate output artifact catalog

На ранньому етапі формується не фінальний список, а candidate catalog:

```text
candidate_output_artifact_catalog
```

Користувач може:

```text
- дати перелік документів;
- дати шаблони;
- дати приклади готових результатів;
- сказати “не знаю, запропонуй”;
- сказати “поки не визначено”.
```

---

## 8. Terminal output binding + template verification loop

Це одна з ключових нових мовних/process-model ідей.

### 8.1. Проблема

Якщо просто сказати “підтвердити пакет”, користувач або тестувальник не розуміє, що саме він отримає на виході.

Потрібно, щоб результуючі документи не були black box.

### 8.2. Нова модель

Коли під час побудови дерева користувач доходить до terminal point, AI має запитати:

```text
Ми дійшли до кінцевої точки цього шляху.
Які документи / outputs треба формувати саме тут?

Ось candidate list:
1. <document A>
2. <document B>
3. <document C>

Можна:
- вибрати з переліку;
- додати новий output;
- сказати, що output тут не потрібен;
- відкласти рішення.
```

### 8.3. Selected outputs для terminal path

Для кожної terminal point треба зафіксувати:

```text
selected_terminal_outputs
no_output_decision
deferred_output_decision
output_binding_required_flag
```

### 8.4. Template status check

Для кожного selected output artifact AI перевіряє:

```text
- чи існує template;
- чи template verified;
- чи є mock-filled example;
- чи користувач бачив приклад;
- чи всі required data/state fields доступні в цій terminal path.
```

### 8.5. Якщо template вже існує

AI показує користувачу:

```text
- document name;
- purpose;
- template;
- mock-filled example;
- які дані з terminal path наповнюють документ;
- validation expectations.
```

Потім користувач обирає:

```text
1. Підтвердити template для цієї terminal point
2. Виправити template
3. Виправити mock example
4. Замінити document
5. Відкласти output
```

### 8.6. Якщо template ще немає

Запускається creation loop:

```text
new output artifact detected
→ define document purpose
→ define required sections
→ define data/state fields
→ draft template
→ generate mock-filled example
→ user review
→ approve / correct / defer / remove
→ add to approved output template catalog
```

### 8.7. Гарантія readiness для terminal path

Terminal path не може вважатися готовою, якщо для її selected outputs немає verified templates або явно прийнятого alpha-template.

```text
terminal_path_ready = true
тільки якщо:

1. terminal decision/status визначено;
2. selected output artifacts визначені;
3. для кожного non-deferred output:
   - template exists;
   - mock-filled example exists;
   - user reviewed it;
   - template status = approved або accepted_for_alpha;
4. required state/data fields покривають template.
```

---

## 9. Progressive tree authoring model

### 9.1. Проблема

Не можна вимагати від користувача одразу повне дерево на всю глибину.

Користувач може бачити:

```text
- тільки root point і перші гілки;
- root + одну наступну гілку;
- subtree на 2–5 рівнів;
- повний draft дерева;
- просто логіку словами.
```

### 9.2. Нова модель

Замість статичного `decision_tree_blueprint` вводиться progressive authoring:

```text
user tree vision
→ AI формує draft-subtree
→ standard verification node-by-node / branch-by-branch
→ terminal-or-continue decision
→ terminal output binding, якщо terminal
→ sibling/deferred tracking
→ repeat until all branches closed
```

### 9.3. User tree vision capture

AI питає:

```text
Як ви зараз бачите старт дерева?

Можете описати:
1. тільки root point і перші гілки;
2. root point + одну наступну гілку;
3. subtree на 2–5 рівнів;
4. повний draft дерева;
5. просто логіку словами — AI сам запропонує draft.
```

### 9.4. Draft subtree generation

AI формує:

```text
- root / current node;
- питання або дію вузла;
- гілки;
- наступні вузли, якщо описані;
- terminal candidates;
- output binding candidates;
- open questions / risks.
```

Важливе правило:

```text
draft_subtree != approved_tree
```

### 9.5. Draft subtree review

Після draft generation обовʼязково запускається:

```text
node review
branch review
terminal-or-continue decision
terminal output binding if terminal
sibling branch tracking
deferred return points
```

---

## 10. Node review model

Поточна точка, на якій ми зупинились у гілці 1:

```text
Гілка 1 → Progressive tree authoring → Draft subtree review start → Node review
```

### 10.1. Що має показувати Node review

```text
- назва / alias вузла;
- людський опис;
- питання або дія вузла;
- які state-поля він читає;
- які state-поля він записує;
- які gates застосовуються;
- які гілки з нього виходять;
- чи є open questions;
- ризики або неоднозначності.
```

### 10.2. Рішення по вузлу

```text
1. Підтвердити вузол
2. Виправити вузол
3. Відкласти вузол
```

### 10.3. Наступна потрібна модель: terminal-or-continue decision

Після підтвердження вузла має бути окреме питання:

```text
Що це за точка?

1. Це terminal point
2. Тут є наступне розгалуження
3. Потрібно додати проміжний вузол
4. Потрібно повернутись/перебудувати попередню логіку
5. Відкласти цю гілку
```

Це не замінює node review, а йде після нього.

---

## 11. Open questions model

Open questions не мають завжди блокувати рух.

Їх треба класифікувати:

```text
- blocking
- deferred
- output-related
- gate-related
- terminal-path-related
- resolved
```

Gate:

```text
не можна йти далі, поки open questions не класифіковані
```

Але не всі open questions мають бути закриті одразу.

---

## 12. Expected language / IR-level additions

Ці покращення бажано винести не лише в APF YAML, а й у мовну модель / IR як reusable constructs.

### 12.1. New or formalized concepts

```text
INPUT.POLICY
OUTPUT.CANDIDATE_CATALOG
OUTPUT.BIND.TERMINAL
OUTPUT.TEMPLATE.STATUS_CHECK
OUTPUT.TEMPLATE.CREATE
OUTPUT.MOCK_EXAMPLE.REVIEW
TERMINAL.READINESS.CHECK
TREE.AUTHOR.PROGRESSIVE
TREE.DRAFT.SUBTREE
TREE.REVIEW.NODE
TREE.REVIEW.BRANCH
TREE.NEXT_STEP.DECISION
BRANCH.JOIN.SHARED_TAIL
CONTROL.ACTION.BOOKKEEPING
PROCESS.REVIEW.MODE_LABEL
```

### 12.2. Recommended IR/state fields

```text
input_policy
required_input_artifacts
optional_input_artifacts
input_unknown_or_deferred
candidate_output_artifact_catalog
selected_terminal_outputs
terminal_output_binding_status
output_template_status
mock_filled_example_status
approved_output_template_catalog
deferred_output_template_catalog
removed_output_artifact_log
terminal_path_ready
user_tree_vision_depth
draft_subtree_status
draft_nodes
draft_branches
terminal_candidates
terminal_output_binding_points
current_node_review_status
current_branch_review_status
node_next_step_decision
selected_control_action
not_selected_control_actions
blocked_until_ready_actions
unreviewed_sibling_branches
deferred_return_points
```

---

## 13. Expected APF patch after branch 1 / branch 2 review

Після завершення review гілок 1 і 2 бажаний patch має:

1. Перевпорядкувати гілку 1:

```text
Мета прикладного проєкту
→ Тип процесу
→ Runtime roles
→ Domain model overview
→ Input artifacts / sources / input policy
→ Output artifact catalog
→ Open questions review
→ Runtime entry point
→ Progressive tree authoring
→ Draft subtree generation
→ Node/branch review
→ Terminal output binding
→ Tree complete
→ Source YAML generation approval
→ Shared validation pipeline
```

2. Замінити статичний `decision_tree_blueprint` на progressive tree authoring flow.

3. Додати або формалізувати terminal output binding loop.

4. Додати mock-filled example review для output templates.

5. Поширити output binding model на гілку 2.

6. Для гілки 3 перевірити, чи free-dialogue draft tree також використовує terminal output binding.

7. Для гілки 4 використовувати цей loop тільки якщо зміна зачіпає outputs/templates.

---

## 14. Поточні закриті / незакриті ділянки дерева

### Закрито

```text
Гілка 4: Коригування існуючого процесу
```

Статус:

```text
review_status: approved
patch_status: applied
module_version: 0.1.0-alpha.14
minimal_validation_status: passed
```

### У процесі

```text
Гілка 1: Доменна модель + дерево рішень
```

Поточна точка:

```text
Node review
```

### Не закрито

```text
Гілка 2: Ручне дерево рішень
```

Потрібно перевірити, чи вона також використовує:

```text
- input policy;
- output candidate catalog;
- progressive / manual subtree review;
- terminal output binding;
- mock-filled template review;
- shared validation tail.
```

### Частково закрито / потребує sync

```text
Гілка 3: Вільний діалог
```

Вона стабілізована раніше, але після нових output/template правил треба перевірити, чи її terminal paths також проходять output binding.

---

## 15. Рекомендований наступний крок

Повернутися до вузла:

```text
Гілка 1 → Node review
```

і продовжити review з урахуванням цього пакета покращень.

Після закриття гілки 1 перейти до гілки 2, а потім зробити scoped YAML patch для всіх підтверджених змін.

---

## 16. Короткий список покращень для changelog

```text
- Added explicit existing-process improvement branch.
- Added baseline policy for process correction.
- Added batch and targeted improvement modes.
- Added shared-tail join policy to avoid duplicate validation/handoff flows.
- Formalized process-design review rendering modes.
- Split branch 1 context into atomic nodes.
- Moved runtime entry point after domain/input/output/open-question context.
- Introduced input policy instead of mandatory input artifacts.
- Split input artifacts from output artifacts.
- Introduced candidate output artifact catalog.
- Introduced terminal output binding loop.
- Required verified templates or accepted alpha-templates for terminal outputs.
- Required mock-filled examples for output template review.
- Replaced static decision tree blueprint with progressive tree authoring.
- Added user tree vision capture and draft subtree generation.
- Added explicit terminal-or-continue decision after node review.
- Strengthened control-action bookkeeping and sibling/deferred tracking.
```

## 13. Контекстний пакет: що саме ми збираємось передати в мовний пакет

Цей розділ додає до пакета покращень не лише перелік локальних правок APF, а й загальне розуміння того, яку process-model ми фактично проєктуємо для мовного пакета Ordo.

Це **не фінальна реалізація** і не повна специфікація програми створення playbookʼів. Це contextual handoff для моделі / розробника мовного пакета: які концепти, runtime-патерни й IR-рішення ми хочемо перенести з поточного APF-ревʼю на рівень мови.

---

### 13.1. Головна ідея

Ми будуємо не просто окремий guided dialogue для створення одного YAML-файлу.

Фактично формується **self-hosted authoring system** для створення прикладних Ordo-процесів / playbookʼів:

```text
human analyst / PM / tester
→ описує процес людською мовою
→ AI допомагає сформувати дерево рішень
→ AI показує поточні вузли, гілки, gates, outputs і open questions
→ користувач перевіряє процес node-by-node / branch-by-branch
→ AI генерує source/program.ordo.yaml
→ AI валідує структуру
→ AI готує пакет для handoff
```

Ключовий принцип:

```text
користувач не пише YAML напряму;
користувач підтверджує людське розуміння процесу;
модель відповідає за перетворення цього розуміння в Ordo source / IR.
```

---

### 13.2. Що таке “playbook / applied project factory” у цьому контексті

У межах нашої розмови `ordo.applied_project_factory` поступово перетворюється на фабрику playbookʼів:

```text
playbook = прикладний процес,
який має:
- мету;
- користувача;
- роль AI;
- entry point;
- дерево рішень;
- state;
- gates;
- terminal paths;
- output artifacts;
- templates;
- validation rules;
- handoff package.
```

Тобто результатом є не лише YAML, а зрозумілий runtime-процес, який можна запускати, тестувати, пояснювати, переглядати й покращувати.

---

### 13.3. Чотири стартові режими APF

Поточна модель має чотири top-level режими старту:

```text
1. Доменна модель + дерево рішень
2. Ручне дерево рішень
3. Вільний діалог
4. Коригування існуючого процесу
```

#### 13.3.1. Доменна модель + дерево рішень

Користувач ще не має готового дерева, але може пояснити домен, процес, ролі, очікувані outputs і логіку прийняття рішень.

Поточний узгоджений порядок для цієї гілки:

```text
1. Мета прикладного проєкту
2. Тип процесу
3. Runtime roles
4. Domain model overview
5. Input artifacts / sources / input policy
6. Output artifact catalog
7. Terminal output binding + template verification loop
8. Open questions review
9. Runtime entry point
10. Progressive decision tree authoring
11. User tree vision capture
12. Draft subtree generation
13. Draft subtree review start
14. Node review
15. Branch review
16. Terminal-or-continue decision
17. Terminal output binding, якщо шлях terminal
18. Repeat until tree review complete
19. Approval to generate source/program.ordo.yaml
20. Shared validation / handoff pipeline
```

Поточна точка review у чаті:

```text
branch_1_status: in_review
current_node: Node review
review_paused_for_language_improvement_package: true
```

#### 13.3.2. Ручне дерево рішень

Користувач може одразу будувати дерево руками, але все одно не пише YAML.

Очікувана логіка:

```text
manual root node
→ branch definitions
→ node-by-node review
→ branch-by-branch review
→ terminal-or-continue decision
→ terminal output binding
→ state/gates/templates check
→ approval to generate source YAML
```

Ця гілка ще не закрита node-by-node у поточному review, але має використовувати ті ж shared-патерни, що й гілка 1.

#### 13.3.3. Вільний діалог

Користувач просто описує процес, ідеї, проблеми, outputs або приклади без структури.

Узгоджена логіка:

```text
raw notes
→ structured extraction
→ candidate nodes / gates / outputs / templates
→ draft tree
→ depth-first node review
→ branch review
→ terminal handling
→ stabilized branch handoff
```

Ця гілка стала джерелом багатьох reusable runtime-патернів: current-node rendering, node-review decision, sibling branch tracking, deferred return points.

#### 13.3.4. Коригування існуючого процесу

Ця гілка вже внесена в APF `v0.1.0-alpha.14`.

Baseline може бути тільки:

```text
1. Повний workspace / dev package archive
2. self-contained source/program.ordo.yaml
```

Режими коригування:

```text
1. Batch improvement list
2. Targeted dialogue improvement
```

Після унікальної частини гілка 4 не дублює validation/handoff, а робить join:

```text
confirmed change set
→ scoped YAML patches
→ minimal validation
→ JOIN shared terminal full-validation / handoff pipeline
```

---

### 13.4. Важливе розділення: YAML validity ≠ human process review completeness

У поточному APF є кілька різних статусів, які не можна змішувати:

```text
YAML parse passed
≠
Ordo lint passed
≠
compile / refresh IR passed
≠
human process review closed
≠
full validation passed
≠
ready for handoff
```

Для мовного пакета треба підтримати цю різницю як first-class status model.

Рекомендовані статуси:

```text
technical_validation_status:
- not_started
- minimal_passed
- failed
- full_passed
- deferred

human_review_status:
- not_started
- in_progress
- node_confirmed
- branch_confirmed
- deferred
- closed

handoff_status:
- blocked
- ready
- deferred_not_validated
```

---

### 13.5. Поточний вузол має показувати не лише питання

Один із важливих патернів, який треба винести в мову: поточний вузол під час design/review не може бути просто текстовим питанням.

Він має мати user-facing current-node block:

```text
current_mode:
- tree_traversal
- branch_selection
- node_review_decision
- execution_gate
- validation_gate
- branch_closure

current_node_display_block:
- human description
- question / action
- state read/write
- transitions
- gates
- artifacts / outputs / templates
- open questions
- sibling branches
- deferred return points
- expected user decision
```

Це потрібно, щоб користувач розумів, чи він зараз:

```text
- рухається по дереву;
- вибирає гілку;
- ревʼюїть вузол;
- підтверджує зміну;
- закриває branch;
- запускає validation;
- приймає handoff decision.
```

---

### 13.6. Control actions і bookkeeping

Модель має чітко розділяти:

```text
unreviewed_sibling_branches
≠
not_selected_control_actions
≠
blocked_until_ready_actions
```

Приклад:

```text
selected_control_action:
- Підтвердити вузол

not_selected_control_actions:
- Виправити вузол
- Відкласти вузол

unreviewed_sibling_branches:
- гілка B
- гілка C

blocked_until_ready_actions:
- approve_tree blocked until all required branches reviewed
```

Це має бути не просто UI-деталь, а частина execution/review semantics.

---

### 13.7. Progressive tree authoring model

Ми відмовились від ідеї, що користувач має одразу описати все дерево.

Правильна модель:

```text
користувач може описати:
- тільки root point;
- root + перші гілки;
- одну гілку вглиб;
- subtree на 2–5 рівнів;
- весь draft;
- просто логіку словами.
```

AI формує draft-subtree відповідної глибини, а потім запускає standard verification:

```text
user tree vision
→ draft subtree generation
→ draft subtree review start
→ node review
→ branch review
→ terminal-or-continue decision
→ terminal output binding if terminal
→ sibling/deferred tracking
→ repeat until tree review complete
```

Новий мовний патерн:

```text
PROGRESSIVE_TREE_AUTHORING
```

Можливі IR-level обʼєкти:

```text
TREE.VISION.CAPTURE
SUBTREE.DRAFT
SUBTREE.REVIEW.START
NODE.REVIEW
BRANCH.REVIEW
NODE.NEXT_STEP_DECISION
TREE.REVIEW.COMPLETE
```

---

### 13.8. Terminal-or-continue decision

Після підтвердження вузла користувач має визначити, що відбувається далі.

Це окреме рішення, не те саме, що “підтвердити вузол”.

```text
node review decision:
1. approve node
2. correct node
3. defer node

next-step decision:
1. this is terminal point
2. continue with branching
3. add intermediate node
4. rebuild previous logic
5. defer branch
```

Якщо користувач каже, що це terminal point, автоматично запускається output binding.

---

### 13.9. Input artifacts / sources / input policy

Input artifacts не мають бути обовʼязковими.

Користувач може:

```text
- мати готові input artifacts;
- не мати нічого на цей момент;
- не регламентувати input взагалі;
- сформувати input пізніше;
- мати optional inputs залежно від сценарію.
```

Тому вузол має фіксувати не “які inputs є”, а input policy:

```text
input_policy:
- required_inputs
- optional_inputs
- no_predefined_input
- input_unknown_deferred
- input_will_be_produced_later
```

Мовний патерн:

```text
INPUT.POLICY
```

---

### 13.10. Output artifact catalog

Output artifacts теж не завжди відомі на початку.

Можливі стани:

```text
output_artifact_catalog_status:
- known
- partially_known
- ai_should_propose
- deferred
- no_document_outputs
```

На ранньому етапі достатньо candidate catalog:

```text
candidate_output_artifact_catalog:
- known_output_artifacts
- candidate_output_artifacts
- optional_output_artifacts
- deferred_output_artifacts
- no_document_outputs_flag
```

Це не означає, що templates вже готові.

---

### 13.11. Terminal output binding + template verification loop

Це одне з найважливіших покращень.

Ми зафіксували, що недостатньо просто “підтвердити пакет в цілому”. Користувач / тестувальник має бачити, які документи він отримає на виході, як вони виглядатимуть і з яких даних формуватимуться.

Коли під час побудови дерева користувач доходить до terminal point, AI має питати:

```text
Ми дійшли до кінцевої точки цього шляху.

Які outputs треба формувати саме тут?

Ось загальний candidate list:
1. <document A>
2. <document B>
3. <document C>

Можна:
- вибрати з переліку;
- додати новий output;
- сказати, що output тут не потрібен;
- відкласти рішення.
```

Після вибору outputs AI перевіряє:

```text
для кожного selected output:
- template exists?
- template verified?
- mock-filled example exists?
- user approved visual/content shape?
- required state/data fields available on this terminal path?
```

Якщо template є, він проходить review.

Якщо template немає, запускається creation loop:

```text
new output artifact detected
→ define purpose
→ define required sections
→ define data/state fields
→ draft template
→ generate mock-filled example
→ user review
→ approve / correct / defer / remove
→ add to approved output template catalog
```

Мовні патерни:

```text
TERMINAL.OUTPUT.SELECT
OUTPUT.TEMPLATE.CHECK
OUTPUT.TEMPLATE.DRAFT
OUTPUT.MOCK.EXAMPLE
OUTPUT.TEMPLATE.REVIEW
TERMINAL.OUTPUT.BIND
TERMINAL.READY.CHECK
```

---

### 13.12. Mock-filled example як обовʼязковий review artifact

Шаблон сам по собі часто недостатній: користувач бачить placeholderʼи, але не розуміє фінальний вигляд документа.

Тому для кожного важливого output template треба мати:

```text
1. raw template;
2. mock-filled example;
3. data/state mapping;
4. validation expectations;
5. user review decision.
```

Mock example може використовувати штучні значення, але має показувати реальний вигляд майбутнього документа.

---

### 13.13. Terminal path readiness

Terminal path не може вважатися готовим лише тому, що дерево дійшло до кінця.

Потрібна readiness check:

```text
terminal_path_ready = true
тільки якщо:

1. terminal decision/status визначено;
2. output decision визначено:
   - selected outputs
   - no-output decision
   - deferred output decision
3. для кожного non-deferred selected output:
   - template exists;
   - mock-filled example exists;
   - user reviewed it;
   - template status = approved або accepted_for_alpha;
4. required state/data fields покривають template;
5. unresolved blocking questions відсутні.
```

Мовний патерн:

```text
TERMINAL.READY.CHECK
```

---

### 13.14. Shared tail / join-point model

Коли різні гілки доходять до спільної частини процесу, не треба дублювати вузли.

Правильна модель:

```text
branch-specific flow
→ JOIN shared_tail
```

Для APF це виглядає так:

```text
branch 4 unique flow
→ minimal validation
→ JOIN shared terminal full-validation / handoff pipeline
```

Мовний патерн:

```text
FLOW.JOIN
SHARED.TAIL.REFERENCE
```

Це важливо для уникнення дублювання `full validation`, `correction loop`, `handoff readiness` у кожній гілці.

---

### 13.15. Incremental YAML patch discipline

Під час review не треба після кожної думки користувача переписувати весь YAML.

Правильна дисципліна:

```text
review / correction накопичує intended structural corrections
→ після closure відповідної гілки або scoped block
→ apply scoped YAML patch
→ minimal validation:
   - YAML parse
   - lint
   - compile / refresh IR
→ full validation deferred до terminal/pre-handoff gate
```

Мовний патерн:

```text
YAML.PATCH.SCOPED
VALIDATION.MINIMAL
VALIDATION.FULL.DEFERRED
```

---

### 13.16. Process feedback loop

Користувач може під час проходження процесу сказати, що сам процес треба змінити.

Тоді AI має не “просто відповісти”, а перейти в process-feedback mode:

```text
process feedback detected
→ proposed process change
→ show before/after
→ user approves/corrects/defer
→ scoped YAML patch
→ minimal validation
→ reload/continue from updated flow
```

Мовний патерн:

```text
PROCESS.FEEDBACK.CAPTURE
PROCESS.CHANGE.PROPOSE
PROCESS.CHANGE.APPLY
PROCESS.RESUME
```

---

### 13.17. Existing process improvement branch як reusable pattern

Гілка 4 стала прикладом reusable pattern для будь-якого Ordo-процесу:

```text
existing process correction
→ baseline validation
→ choose improvement mode
→ batch improvements або targeted improvements
→ before/after review
→ confirmed change set
→ scoped patches
→ minimal validation
→ shared full validation
```

Цей pattern може бути винесений на рівень мови як general improvement workflow.

Можливі мовні обʼєкти:

```text
PROCESS.BASELINE.LOAD
IMPROVEMENT.CANDIDATES.EXTRACT
IMPROVEMENT.SELECT
IMPROVEMENT.MAP_TO_PROCESS
CHANGE.BEFORE_AFTER
CHANGE.SET.CONFIRM
PATCH.APPLY.SCOPED
```

---

### 13.18. Graph/SVG policy

SVG/graph не генерується автоматично на кожному кроці.

Правило:

```text
SVG generation default: off
Generate only when user explicitly requests
Default rendering when requested: context view
Full tree: overview / review aid only
```

Для великих дерев потрібні режими:

```text
- full overview
- focused subtree
- root-to-current-node context
- path-only
- annotation/highlight overlay
```

Це має бути review aid, а не validation source of truth.

---

### 13.19. Що має зрозуміти модель із цього пакета

Модель, яка отримає цей MD-пакет, має зрозуміти таке:

1. Ми будуємо APF не як простий wizard, а як self-hosted process/playbook authoring runtime.
2. Користувач не пише YAML; він підтверджує людське дерево, вузли, гілки, outputs і templates.
3. Review має бути покроковим: node-by-node, branch-by-branch, terminal-by-terminal.
4. Terminal point не готова без output decision і template readiness.
5. Output documents мають бути зрозумілі користувачу до handoff, бажано через mock-filled examples.
6. Input може бути відсутнім або optional; це policy, а не required artifact.
7. Runtime entry point краще визначати після доменної моделі, input/output policy і open questions.
8. Tree authoring має бути progressive: root-only, shallow subtree, deep subtree або free-form logic.
9. Shared validation/handoff pipeline не дублюється; гілки мають join-point.
10. Scoped patches і minimal validation відділені від full validation.
11. Current-node rendering має явно показувати режим: traversal, branch selection, node review, validation gate, closure.
12. Це все має стати або мовними патернами, або APF-level reusable subflows, а не залишитись випадковими домовленостями чату.

---

### 13.20. Мінімальний candidate list для мовного пакета

Нижче перелік концептів, які варто розглянути як майбутні мовні / IR-level additions:

```text
INPUT.POLICY
OUTPUT.CANDIDATE.CATALOG
OUTPUT.TEMPLATE.CHECK
OUTPUT.TEMPLATE.DRAFT
OUTPUT.MOCK.EXAMPLE
OUTPUT.TEMPLATE.REVIEW
TERMINAL.OUTPUT.SELECT
TERMINAL.OUTPUT.BIND
TERMINAL.READY.CHECK
TREE.VISION.CAPTURE
SUBTREE.DRAFT
SUBTREE.REVIEW.START
NODE.REVIEW
BRANCH.REVIEW
NODE.NEXT_STEP_DECISION
FLOW.JOIN
SHARED.TAIL.REFERENCE
PROCESS.FEEDBACK.CAPTURE
PROCESS.CHANGE.PROPOSE
PROCESS.CHANGE.APPLY
YAML.PATCH.SCOPED
VALIDATION.MINIMAL
VALIDATION.FULL.DEFERRED
CURRENT.NODE.DISPLAY.BLOCK
CONTROL.ACTION.BOOKKEEPING
```

Цей список не є фінальним API. Це candidate vocabulary для обговорення і подальшого формального введення в мовний пакет.

---

### 13.21. Наступна робоча точка після цього документа

Після формування цього пакета runtime-review можна продовжити з місця, де він був зупинений:

```text
branch: 1. Доменна модель + дерево рішень
current_node: Node review
status: paused_for_language_model_improvements_package
```

Після закриття гілки 1 треба:

```text
1. закрити гілку 2 node-by-node;
2. внести scoped patch для гілок 1/2 і shared output-template model;
3. виконати minimal validation;
4. за потреби згенерувати actual tree SVG;
5. потім перейти до full validation / handoff readiness.
```
