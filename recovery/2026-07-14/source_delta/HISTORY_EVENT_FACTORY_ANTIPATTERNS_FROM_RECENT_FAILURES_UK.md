# Антипатерни для автоматичної перевірки playbook-процесів

## Призначення

Цей файл узагальнює повторювані помилки, виявлені під час розвитку History Event Analysis Package Factory. Він призначений для майбутнього процесу, який створює або перевіряє playbook-и.

Файл не є частиною factory package і не змінює його active contracts.

---

## AP-01. Evidence-free complexity assessment

**Антипатерн:** оцінювання складності реалізації без архіву проєкту або read-only доступу до репозиторію.

**Симптоми:**
- присвоєно `low / medium / high / critical` лише з опису задачі;
- названо affected files або cross-cutting impact без inspection;
- рекомендовано repository-assisted route без source evidence.

**Автоматична перевірка:**
- якщо `complexity_assessment_status = completed`, то мають бути `repository_evidence_status = available` і `repository_inspection_status = completed`;
- інакше блокувати перехід і ставити `blocked_missing_repository_evidence`.

**Правильний патерн:** repository evidence → read-only inspection → impact analysis → complexity assessment → execution route.

---

## AP-02. Approval scope inflation

**Антипатерн:** трактування одного підтвердження як дозволу на наступні незалежні дії.

**Приклади:**
- scope confirmation вважається дозволом на mutation;
- repository mutation authorization вважається підтвердженням документів;
- QA contract confirmation вважається дозволом змінювати fixture;
- загальне «підтверджую» закриває кілька неактивних вузлів.

**Автоматична перевірка:**
- кожне підтвердження застосовується лише до `active_node`;
- кожна destructive або externally-visible дія має власний authorization type;
- заборонити транзитивне успадкування approval між різними responsibility domains.

**Правильний патерн:** one approval → one explicitly named decision/action.

---

## AP-03. Mandatory-node bypass

**Антипатерн:** перехід до assembly або completion із пропуском обов’язкових downstream-вузлів.

**Симптоми:**
- `mutation completed → package completed`;
- документи не показані й не підтверджені окремо;
- metadata bundle згенерований до завершення document confirmation rail.

**Автоматична перевірка:**
- перед terminal state перевіряти всі mandatory successors;
- package assembly дозволяти лише коли всі required confirmable artifacts мають статус `confirmed`;
- заборонити альтернативні edges, які обходять authoritative final rail.

**Правильний патерн:** sequential mandatory gates with terminal-state closure validation.

---

## AP-04. Aggregate confirmation substitutes document confirmation

**Антипатерн:** зведений QA/operational contract або package composition використовується як заміна підтвердження окремих документів.

**Симптоми:**
- паспорт, Jira task, implementation prompt або Manual QA package не мали власного confirmation;
- `B1_P5_QA_DATA_CONFIRM` закриває document approval.

**Автоматична перевірка:**
- кожен confirmable artifact має власний generation/validation/confirmation state;
- aggregate gates не можуть змінювати status окремих документів на `confirmed`.

**Правильний патерн:** artifact-level confirmation before aggregate composition confirmation.

---

## AP-05. Non-authoritative document generation

**Антипатерн:** документ збирається вручну або зі скороченої імпровізованої структури замість active prompt і canonical template.

**Симптоми:**
- відсутні exact prompt/template paths;
- документ названо «скороченим шаблоном», якого немає у package;
- generation provenance не зафіксований.

**Автоматична перевірка:**
- перед generation вимагати `active_prompt_loaded = true` і `canonical_template_loaded = true`;
- фіксувати paths та hashes джерел;
- невідомі template variants блокувати як provenance violation.

**Правильний патерн:** authoritative prompt + canonical template + recorded provenance.

---

## AP-06. Confirmed-state omission

**Антипатерн:** підтверджені вимоги не переносяться до документа, який має їх узагальнювати.

**Приклад:** із паспорта випали підтверджені functional, unit/provider та integration tests.

**Автоматична перевірка:**
- будувати coverage matrix `confirmed requirement → document section`;
- забороняти confirmation, якщо є uncovered confirmed requirements;
- окремо звіряти test counts, aliases, paths, mappings, defaults і execution statuses.

**Правильний патерн:** confirmed-state coverage gate before user review.

---

## AP-07. No pre-review completeness gate

**Антипатерн:** неповний або суперечливий документ одразу передається на confirmation node.

**Автоматична перевірка:**
- перед confirmation перевіряти required sections, unresolved gaps, QA coverage, operational defaults, test execution status і міжсекційну узгодженість;
- при failure залишати документ у `draft_incomplete`.

**Правильний патерн:** generate → provenance check → coverage check → completeness validation → confirmation.

---

## AP-08. Stale confirmation after upstream change

**Антипатерн:** після зміни upstream-документа або коду downstream-документи залишаються `confirmed`.

**Симптоми:**
- revision не інвалідовує залежні артефакти;
- composition, consistency або metadata reports залишаються valid після зміни змісту.

**Автоматична перевірка:**
- підтримувати dependency graph артефактів;
- upstream change переводить залежні artifacts у `stale_requires_reconfirmation`;
- composition, consistency і metadata bundle переводити у `stale`.

**Правильний патерн:** deterministic invalidation cascade.

---

## AP-09. Parallel finalization rails

**Антипатерн:** у дереві існує більше одного маршруту до package completion.

**Симптоми:**
- старі й нові assembly nodes активні паралельно;
- один маршрут має слабші prerequisites;
- completion можна досягти в обхід confirmation rail.

**Автоматична перевірка:**
- знайти всі paths до terminal package state;
- вимагати однаковий mandatory prerequisite set;
- позначати лише один authoritative final rail.

**Правильний патерн:** single authoritative finalization path.

---

## AP-10. Generated-only artifact treated as confirmable

**Антипатерн:** generated-only документи отримують зайві confirmation nodes або блокують процес.

**Приклади:**
- `07_PROCESS_IMPROVEMENT_FEEDBACK_<ALIAS>.md`;
- `09_QA_AUTOMATION_README_<ALIAS>.md`.

**Автоматична перевірка:**
- для кожного artifact має бути policy: `confirmable`, `generated-only`, `optional-generated-only`;
- generated-only artifacts перевіряються validation gate, але не потребують user approval.

**Правильний патерн:** explicit artifact confirmation policy.

---

## AP-11. Package boundary leakage

**Антипатерн:** analytical package неявно містить code package, repository source copies, patch або службові каталоги.

**Симптоми:**
- `code/`, `files/`, `change_set/`, `review_snapshot/` всередині analytical package;
- користувачу незрозуміло, де аналітичний deliverable, а де змінений проєкт.

**Автоматична перевірка:**
- analytical package має exact allowlist файлів;
- code package завжди окремий artifact;
- forbidden-path scan перед ZIP assembly.

**Правильний патерн:** strict analytical/code package separation.

---

## AP-12. Weak dedup identity

**Антипатерн:** deduplication лише за `source_change_id`, хоча одна source change може породжувати кілька типів подій.

**Автоматична перевірка:**
- primary dedup key має бути `(source_change_id, item.alias)`;
- тестувати три випадки: same/same → duplicate; same/different → allowed; different/same → allowed.

**Правильний патерн:** dedup identity відповідає бізнес-ідентичності події.

---

## AP-13. Endpoint contract reconstruction from endpoint name

**Антипатерн:** request payload, auth, base URL або response semantics виводяться з назви endpoint без authoritative evidence.

**Автоматична перевірка:**
- exact executable REST contract має посилатися на source evidence;
- unknown fields залишаються unknown, а не домислюються;
- base URL/auth не оголошуються process gaps, якщо це локально виключено контрактом.

**Правильний патерн:** executable contract only from authoritative evidence.

---

## AP-14. Fixture authorization conflation

**Антипатерн:** дозвіл на QA scope, code generation або repository mutation використовується як дозвіл змінити конкретну fixture-картку.

**Автоматична перевірка:**
- fixture mutation і rollback мають окремі authorization events;
- rollback не успадковує дозвіл від initial mutation;
- без explicit fixture authorization дозволені лише read-only checks.

**Правильний патерн:** per-mutation authorization for concrete fixture data.

---

## AP-15. False validation success

**Антипатерн:** звіт має загальний статус `passed`, хоча compilation або lint завершились із forced errors/warnings.

**Автоматична перевірка:**
- `passed` дозволений лише за чистих mandatory checks;
- forced lint errors → щонайменше `passed-with-warnings` або `partial`;
- report summary має збігатися з деталями checks.

**Правильний патерн:** validation status reflects the weakest mandatory check.

---

## Рекомендований формат автоматичного правила

Для кожного антипатерну майбутній playbook-checker повинен зберігати:

```yaml
id: AP-XX
name: stable_machine_name
severity: blocker | high | medium | low
scope: graph | state | artifact | package | authorization | validation
trigger: machine-readable condition
evidence_required: []
forbidden_transition: null
required_transition: null
remediation: concise corrective action
regression_cases: []
```

## Мінімальний набір blocker-перевірок

До blocker-рівня варто віднести:

- AP-01 Evidence-free complexity assessment;
- AP-02 Approval scope inflation;
- AP-03 Mandatory-node bypass;
- AP-05 Non-authoritative document generation;
- AP-06 Confirmed-state omission;
- AP-08 Stale confirmation after upstream change;
- AP-09 Parallel finalization rails;
- AP-11 Package boundary leakage;
- AP-14 Fixture authorization conflation.
