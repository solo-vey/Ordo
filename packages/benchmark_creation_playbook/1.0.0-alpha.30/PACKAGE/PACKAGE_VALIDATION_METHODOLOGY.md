# Методика перевірки пакетів Playbook та автоматичного тестування

Версія: 1.0 (накопичуваний документ)

## 1. Мета

Документ визначає перевірки, які треба виконати перед передачею playbook або automated-testing package зовнішній моделі. Статус `PASS` дозволено ставити лише на підставі фактично виконаних перевірок і збережених журналів.

## 2. Ієрархія перевірок

1. **Фізична цілісність:** ZIP відкривається, немає дубльованих/небезпечних шляхів, усі SHA-256 збігаються.
2. **Повнота пакета:** присутні manifest, runtime process, driver contract, selected-run input, overlays, templates, contracts, launch prompt і обов’язковий pre-flight validator.
3. **Runtime addressability:** кожен шлях, на який посилаються manifest, policy, protocol, scripts та process, існує саме за вказаним шляхом. Наявність «схожого» файла не є еквівалентом без явного alias contract.
4. **Version coherence:** package ID, manifest, protocol, README, launch prompt і process мають одну актуальну версію; застарілі launch prompts блокують реліз.
5. **Entrypoint:** точка входу має бути явною і однаковою в manifest, protocol, launch prompt та process. Для Structured Instructions Alpha 1.2.1 — `T001`, надрукований як Position 1.
6. **Структурна повнота:** рівно 126 унікальних позицій, 64 technical і 62 analytical, без пропусків номерів.
7. **Семантична parity:** title/action, intent, inputs, outputs, state mutation, evidence, gates, transitions, correction owner і terminal semantics зіставляються з immutable YAML source. Критична розбіжність блокує реліз.
8. **Correction-loop reachability:** correctable failure має маршрут failure → receipt → owner → invalidation → regeneration → revalidation. Hard stop не може підміняти доступний correction loop.
9. **Validator reality:** перевіряється не лише наявність валідатора, а запуск за тим самим шляхом і командою, які отримає зовнішня модель. Exit code 0 та машинний `PASS` обов’язкові.
10. **Positive і negative regressions:** сильні fixtures приймаються, дефектні відхиляються з очікуваними кодами.
11. **Black-box pre-flight:** тест виконується з розпакованого фінального ZIP, а не з build-каталогу. Заборонено використовувати файли поза архівом.
12. **Execution smoke test:** модельний маршрут не починається до зеленого pre-flight; при blocker не створюються бізнес-артефакти чи approvals.

## 3. Обов’язковий порядок

- Зібрати candidate.
- Перегенерувати checksum manifest.
- Створити ZIP.
- Розпакувати ZIP у чистий каталог.
- Запустити package pre-flight точною командою з launch prompt.
- Запустити structural/parity/regression suite.
- Перевірити журнали і відсутність stale references.
- При FAIL виправити candidate, збільшити patch version і повторити. Максимум п’ять циклів.
- Віддавати пакет лише після фінального green-light report.

## 4. Заборонені підстави для PASS

- Лише правильна кількість кроків.
- Лише наявність checksum-файла без перевірки.
- Запуск валідаторів проти іншого каталогу або історичного RUN.
- Порівняння з oracle замість перевірки поточних артефактів.
- Припущення, що зовнішня модель знайде еквівалент відсутнього шляху.
- Заявлений `PASS`, якщо команда зовнішнього запуску фактично не відпрацьована.

## 5. Відомі дефекти, які вже мають окремі gates

- обов’язковий валідатор відсутній за заявленим шляхом;
- process починається не з контрактної точки входу;
- stale package/protocol/launch-prompt versions;
- title не відповідає source intent;
- correction loop не виконується після виправного дефекту;
- validation receipts перевіряють артефакти іншого RUN або каталогу;
- валідатори пропускають неправильні literals, rollback field mismatch, duplicate-cycle defects чи cross-artifact drift.

## 6. Формат green-light evidence

Фінальний звіт повинен містити: номер циклу, SHA-256 ZIP, список виконаних команд, exit codes, підсумки checksum/integrity/addressability/version/entrypoint/count/parity/regression/black-box checks та явний `GREEN_LIGHT: true|false`.

Цей файл треба доповнювати після кожного нового класу false-positive або зовнішнього blocker.
