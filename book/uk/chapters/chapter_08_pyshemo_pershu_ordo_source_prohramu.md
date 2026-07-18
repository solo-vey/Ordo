# Розділ 8. Пишемо першу Ordo Source-програму

## 8.1. Навіщо починати з Ordo Source

До цього моменту ми говорили про Ordo як про спосіб мислення: є мета, контракт, стан, вузли, відповіді, результати й перевірки. Але рано чи пізно це потрібно записати у форму, з якою може працювати модель або майбутній runtime.

Для цього існує Ordo Source.

![Nebu — ідея: Ordo Source як перша програма](../assets/mascots/64x64/Nebu_idea_64x64.png)

Ordo Source — це людсько-читабельний опис програми поведінки моделі. Його має розуміти людина, яка створює процес. Він не обов'язково є найкращим форматом для виконання моделлю, але він зручний для написання, обговорення, ревʼю і зміни.

Можна провести аналогію з класичним програмуванням:

```text
людина пише source code
компілятор перетворює його у форму для виконання
машина виконує скомпільовану форму
```

В Ordo ідея схожа:

```text
людина пише Ordo Source
Ordo compiler / translator перетворює його в Ordo IR
модель або runtime виконує Ordo IR
```

На ранніх етапах ми можемо не мати справжнього compiler-а. Але навіть ручне написання Ordo Source уже допомагає структурувати інструкцію набагато краще, ніж звичайний prompt.

---

## 8.2. Якою має бути перша програма

Першу Ordo-програму краще робити дуже простою.

Не треба одразу брати великий playbook із десятками gates і шаблонів. Почнемо з задачі, яку легко зрозуміти:

```text
Підсумуй текст українською у максимум 3 пункти.
Не додавай фактів, яких немає у вхідному тексті.
Якщо тексту недостатньо, скажи про це.
```

Це хороший перший приклад, тому що тут уже є всі базові елементи Ordo:

```text
мета;
вхідні дані;
контракт результату;
правила;
перевірки;
fallback-поведінка;
результат.
```

Звичайний prompt виглядав би так:

```text
Підсумуй наведений текст українською у максимум 3 пункти. Не додавай фактів, яких немає у вхідному тексті. Якщо тексту недостатньо для змістовного підсумку, скажи про це.
```

Це нормально для простого використання. Але ми хочемо побачити, як той самий зміст виглядає як Ordo Source.

---

## 8.3. Мінімальна структура Ordo Source

Мінімальна Ordo Source-програма може мати такі частини:

```text
ordo
program
intent
contract
context
state
path
result
handoff
```

Не кожна програма завжди має всі ці частини в повному вигляді, але для навчального прикладу краще показати повну форму.

Загальний каркас:

```yaml
ordo: "0.12-draft"
program: "minimal.summary.uk"

intent:
  goal: "summarize_text"

contract:
  input: {}
  output: {}
  rules: []

context: {}

state: {}

path:
  steps: []
  gates: []

result: {}

handoff: {}
```

Це ще не програма, а тільки порожній скелет. Тепер заповнимо його.

---

## 8.4. Описуємо intent

`intent` відповідає на питання: “Що ми хочемо зробити?”

Для нашого прикладу:

```yaml
intent:
  goal: "summarize_text"
  language: "uk"
```

Тут ми не пишемо довге пояснення. Ми фіксуємо головну дію: потрібно підсумувати текст.

![Nebu — увага: не запихати правила в intent](../assets/mascots/64x64/Nebu_attention_64x64.png)

Важливо: `intent` не має містити всі правила. Не треба туди записувати “не вигадувати факти”, “максимум 3 пункти”, “якщо тексту недостатньо”. Це вже contract і gates.

Типова помилка:

```yaml
intent:
  goal: "summarize_text_in_ukrainian_max_3_items_without_facts_and_with_fallback"
```

Так робити не варто. Це перетворює intent на неконтрольовану фразу. Краще розділити:

```yaml
intent:
  goal: "summarize_text"
```

А решту винести у `contract`.

---

## 8.5. Описуємо contract

`contract` визначає, що вважається правильним результатом.

Для нашого прикладу:

```yaml
contract:
  input:
    text: required

  output:
    format: "bullet_list"
    max_items: 3
    language: "uk"

  rules:
    - id: R1
      rule: "use_only_input_text"
    - id: R2
      rule: "do_not_invent_facts"
    - id: R3
      rule: "if_input_insufficient_return_insufficient_data_status"
```

Тут уже видно, чим Ordo відрізняється від prompt-а. Ми не просто просимо “будь ласка, не вигадуй”. Ми створюємо явний contract rule.

Контракт має бути максимально конкретним. Якщо результат має бути списком — це пишеться. Якщо максимум 3 пункти — це пишеться. Якщо мова українська — це пишеться. Якщо модель не має права додавати зовнішні факти — це теж пишеться.

Контракт — це не рекомендація. Це умова правильності результату.

---

## 8.6. Описуємо context

`context` визначає, звідки модель бере дані.

У нашому прикладі джерело одне — текст користувача:

```yaml
context:
  source:
    text: "$USER_INPUT.text"
```

Цей запис означає: не бери текст із памʼяті, не шукай додаткові факти, не додавай знання ззовні. Основне джерело — вхідний текст користувача.

У складніших програмах context може містити:

```text
документи;
таблиці;
source row;
попередній стан;
приклади;
правила проєкту;
підтверджені контракти;
обмеження середовища.
```

Але для першої програми достатньо одного source.

---

## 8.7. Описуємо state

Навіть проста програма може мати стан.

Для summary-задачі нам достатньо такого стану:

```yaml
state:
  status: "draft"
  assumptions: []
  unsupported_facts: []
```

Навіщо це потрібно?

`status` показує, що результат ще не фінальний до проходження gates.

`assumptions` фіксує припущення, якщо модель змушена щось припустити.

`unsupported_facts` фіксує факти, які модель не змогла підтвердити у вхідному тексті.

Для простого summary це може виглядати надлишково, але принцип важливий: Ordo-програма має знати, що вона вже зібрала, що перевірила і що не може підтвердити.

---

## 8.8. Описуємо path і steps

`path` описує, як модель має дійти до результату.

У нашому прикладі шлях простий:

```yaml
path:
  id: "summarize_or_report_insufficient_input"
  steps:
    - id: S1
      do: "read_input_text"
    - id: S2
      do: "extract_supported_points"
    - id: S3
      do: "select_up_to_3_key_points"
    - id: S4
      do: "render_ukrainian_bullet_summary"
```

Тут важливо, що ми не просимо модель одразу “написати підсумок”. Ми задаємо порядок:

```text
спочатку прочитати;
потім виділити підтверджені пункти;
потім вибрати максимум 3;
потім оформити українською.
```

Це зменшує ризик того, що модель одразу почне генерувати красивий, але не перевірений текст.

---

## 8.9. Додаємо gates

Тепер додамо контрольні точки.

```yaml
path:
  gates:
    - id: G1
      check: "input_text_present"
      on_fail: "return_insufficient_data"

    - id: G2
      check: "no_unsupported_facts"
      on_fail: "remove_or_mark_unsupported"

    - id: G3
      check: "max_3_items"
      on_fail: "compress_to_3_items"

    - id: G4
      check: "output_language_uk"
      on_fail: "rewrite_in_ukrainian"
```

![Nebu — подумати: gate як місце перевірки](../assets/mascots/64x64/Nebu_thinking_64x64.png)

Gate — це місце, де модель має зупинитися і перевірити умову.

`G1` перевіряє, чи є текст.

`G2` перевіряє, чи немає вигаданих фактів.

`G3` перевіряє, чи не більше трьох пунктів.

`G4` перевіряє мову результату.

Важливо: `on_fail` не завжди означає “помилка і кінець”. Іноді це repair action. Наприклад, якщо пунктів 5, модель може стиснути до 3. Якщо мова не українська, модель може переписати українською. Але якщо вхідного тексту немає, треба повернути fallback.

---

## 8.10. Описуємо result і handoff

`result` визначає, що саме повертається.

```yaml
result:
  primary: "summary"
  fallback: "insufficient_data_message"
```

`handoff` визначає, що модель має показати наприкінці:

```yaml
handoff:
  include:
    - "status"
    - "result"
    - "gate_report"
```

Це означає, що користувач має отримати не тільки сам підсумок, а й статус і короткий звіт по gates, якщо це потрібно.

У простому UI gate report можна приховати. Але для навчання та складних задач він дуже корисний.

---

## 8.11. Повна перша Ordo Source-програма

Тепер зберемо все разом.

```yaml
ordo: "0.12-draft"
program: "minimal.summary.uk"

intent:
  goal: "summarize_text"
  language: "uk"

contract:
  input:
    text: required
  output:
    format: "bullet_list"
    max_items: 3
    language: "uk"
  rules:
    - id: R1
      rule: "use_only_input_text"
    - id: R2
      rule: "do_not_invent_facts"
    - id: R3
      rule: "if_input_insufficient_return_insufficient_data_status"

context:
  source:
    text: "$USER_INPUT.text"

state:
  status: "draft"
  assumptions: []
  unsupported_facts: []

path:
  id: "summarize_or_report_insufficient_input"
  steps:
    - id: S1
      do: "read_input_text"
    - id: S2
      do: "extract_supported_points"
    - id: S3
      do: "select_up_to_3_key_points"
    - id: S4
      do: "render_ukrainian_bullet_summary"

  gates:
    - id: G1
      check: "input_text_present"
      on_fail: "return_insufficient_data"
    - id: G2
      check: "no_unsupported_facts"
      on_fail: "remove_or_mark_unsupported"
    - id: G3
      check: "max_3_items"
      on_fail: "compress_to_3_items"
    - id: G4
      check: "output_language_uk"
      on_fail: "rewrite_in_ukrainian"

result:
  primary: "summary"
  fallback: "insufficient_data_message"

handoff:
  include:
    - "status"
    - "result"
    - "gate_report"
```

Це вже повноцінна маленька Ordo Source-програма.

---

## 8.12. Що тут важливо помітити

Перше: програма не дуже довга, але в ній уже є структура.

Друге: правила не заховані в одному реченні. Вони винесені в contract і gates.

Третє: модель має fallback-поведінку, якщо тексту недостатньо.

Четверте: результат має обмеження: формат, кількість пунктів, мова.

Пʼяте: є handoff, тобто визначено, що саме повертається користувачу.

У звичайному prompt-і це все теж можна написати, але Ordo робить структуру явною.

---

## 8.13. Як така програма виконується людиною через модель

Якщо ми ще не маємо Ordo-runtime, можна дати цю програму моделі як інструкцію і попросити виконувати її буквально:

```text
Використовуй наведену Ordo Source-програму як execution contract.
Не виконуй задачу як звичайний prompt.
Спочатку перевір gates, потім поверни result і gate_report.
```

Це не ідеально, бо модель усе ще сама інтерпретує Ordo Source. Але навіть так поведінка стає дисциплінованішою.

У майбутньому runtime зможе читати Ordo Source або compiled IR і сам контролювати порядок виконання.

---

## 8.14. Типові помилки при написанні першої Ordo-програми

### Помилка 1. Запхати все в intent

Погано:

```yaml
intent:
  goal: "summarize text in 3 bullets without unsupported facts and fallback if insufficient"
```

Краще:

```yaml
intent:
  goal: "summarize_text"

contract:
  output:
    max_items: 3
  rules:
    - do_not_invent_facts
```

### Помилка 2. Не описати gates

Погано:

```yaml
rules:
  - do_not_invent_facts
```

Але немає gate, який це перевіряє.

Краще:

```yaml
gates:
  - id: G_NO_UNSUPPORTED_FACTS
    check: "no_unsupported_facts"
    on_fail: "remove_or_mark_unsupported"
```

### Помилка 3. Не описати fallback

Якщо вхідних даних немає, модель не має вигадувати зміст. Тому fallback має бути явним.

### Помилка 4. Змішати source і result

`context` — це звідки беремо дані.

`result` — це що повертаємо.

Їх не треба змішувати.

### Помилка 5. Вважати Ordo Source фінальним машинним форматом

Ordo Source — це зручна людська форма. Для виконання краще мати compiled IR. Про це буде наступний розділ.

---

## 8.15. Короткий підсумок розділу

Ordo Source — це людсько-читабельний запис Ordo-програми.

Він потрібен, щоб автор міг описати процес не як суцільний prompt, а як структурований execution contract.

Перша проста Ordo-програма має містити:

```text
intent;
contract;
context;
state;
path;
steps;
gates;
result;
handoff.
```

Головний принцип:

```text
не писати “модель, будь ласка, зроби правильно”,
а явно описувати, що означає “правильно”.
```

---

## Міні-вправа

Спробуйте переписати звичайний prompt у Ordo Source.

Prompt:

```text
Напиши короткий лист клієнту українською. Поясни, що ми отримали його звернення, розберемо ситуацію і повернемося з відповіддю. Тон має бути ввічливий, без обіцянок конкретного строку.
```

Опишіть:

```text
1. intent;
2. contract.output;
3. contract.rules;
4. context;
5. gates;
6. result;
7. handoff.
```

Підказка: окремим gate варто зробити перевірку, що в листі немає конкретного строку відповіді.

---

<!-- REVIEWED: chapter 08; Nebu markers checked -->
