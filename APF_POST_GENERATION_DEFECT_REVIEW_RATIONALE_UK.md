# Обґрунтування постгенераційної перевірки важливих документів в APF

## 1. Контекст

Під час створення та розвитку History Event Analysis Playbook ми кілька разів зіткнулися з ситуацією, коли згенерований документ виглядав технічно правильним, був внутрішньо узгодженим і проходив формальні перевірки, але все одно містив суттєву фактичну або контрактну помилку.

Найпоказовішим прикладом став Manual QA runbook для `LU_CHANGE_CAPITAL`.

У документі був використаний endpoint:

```text
POST /api/test/product-queue/publish-mongo-patch
```

Однак точний request contract цього endpoint не був підтверджений у state процесу. Через це під час генерації була створена правдоподібна, але непідтверджена Mongo-style структура:

```json
{
  "database": "dossier",
  "collection": "cards",
  "filter": {},
  "update": {
    "$set": {}
  }
}
```

Водночас canonical example використовував інший фактичний контракт:

```json
{
  "mongoId": "<CURRENT_SOURCE_MONGO_ID>",
  "collection": "cards",
  "operation": "append",
  "preview": false,
  "gzip": true,
  "operations": [
    {
      "path": "capital.value",
      "row": 0,
      "value": 2000
    }
  ]
}
```

Початкова quality review не виявила дефект, оскільки перевіряла:

- наявність endpoint;
- валідність JSON;
- внутрішню узгодженість action і rollback;
- логічну послідовність кроків.

Але вона не перевіряла головне: чи відповідає request payload реальному API contract і чи має кожен параметр authoritative evidence.

У результаті документ був синтаксично правильним, послідовним і практично непридатним до безпечного виконання.

## 2. Чому існуючих перевірок недостатньо

Традиційна перевірка артефакта часто відповідає на такі питання:

- чи документ повний;
- чи JSON/YAML синтаксично валідний;
- чи однакові поля використовуються в action і rollback;
- чи присутні обов’язкові секції;
- чи немає явних суперечностей усередині документа.

Цього недостатньо для важливих операційних документів.

Внутрішня узгодженість не гарантує зовнішньої достовірності. Помилкова конструкція може бути послідовно повторена в усіх секціях документа та успішно пройти structural review.

Особливо небезпечними є такі випадки:

1. **Непідтверджений технічний контракт заповнюється типовим припущенням.**  
   Модель бачить назву `mongo-patch` і генерує типовий `$set`, хоча конкретний endpoint має іншу семантику.

2. **Canonical example використовується вибірково або занадто пізно.**  
   Фактичний контракт є в прикладі, але приклад не позначений як authoritative source або не зіставлений із поточною версією package contracts.

3. **Старі й нові контракти змішуються.**  
   Із старого прикладу можна правильно взяти REST payload, але помилково перенести legacy `data.status`, хоча актуальний контракт використовує `ChangeRecord.status`.

4. **Quality review перевіряє форму, але не походження значень.**  
   Технічне поле може бути валідним за форматом, але не мати жодного підтвердженого джерела.

5. **Після виправлення немає незалежної повторної перевірки.**  
   Точкове виправлення може внести нову невідповідність у пов’язану секцію або інший артефакт.

## 3. Коренева процесна причина

APF мав достатні механізми для:

- генерації документа;
- structural validation;
- contract gates;
- confirmation;
- package validation;
- regression checks.

Але не мав універсального обов’язкового етапу, який після генерації ставить інше питання:

> Які частини цього документа можуть бути неправильними, навіть якщо вони виглядають логічними, повними та технічно правдоподібними?

Тобто процес перевіряв, чи документ добре сформований, але не завжди перевіряв, чи модель не заповнила невідомі місця переконливою вигадкою.

Саме тому потрібна не просто додаткова перевірка синтаксису, а окрема постгенераційна перевірка на дефекти, непідтверджені припущення, конфлікти джерел і зовнішню контрактну достовірність.

## 4. Що потрібно додати в APF

### 4.1. Новий обов’язковий вузол

Для важливих документів потрібно додати вузол:

```text
POST_GENERATION_DEFECT_REVIEW
```

Він має виконуватися після первинної structural validation, але до підтвердження документа і до його включення у release package.

Рекомендований process rail:

```text
GENERATE_ARTIFACT
→ STRUCTURAL_VALIDATION
→ CONTRACT_EVIDENCE_VALIDATION
→ ADVERSARIAL_DEFECT_REVIEW
→ CROSS_ARTIFACT_REVIEW
→ TARGETED_CORRECTION_IF_REQUIRED
→ POST_CORRECTION_REVIEW
→ CONFIRM_ARTIFACT
```

### 4.2. Класифікація критичності документів

Перевірка має бути обов’язковою для документів, помилка в яких може призвести до:

- виконання неправильного API request;
- модифікації даних;
- неправильного rollback;
- реалізації помилкового контракту;
- створення некоректного Jira task;
- запуску неправильних тестів;
- втрати або пошкодження state;
- неправильного package migration;
- помилкового release decision.

До цієї категорії належать:

- Manual QA runbooks;
- automation specifications;
- implementation prompts;
- API contracts;
- migration/reload prompts;
- release reports;
- Jira implementation tasks;
- operational playbooks;
- rollback instructions.

Для некритичних описових документів перевірка може бути спрощеною або `not-applicable`.

### 4.3. Evidence review кожного технічного твердження

Кожне executable або contract-sensitive значення повинно мати evidence source.

Допустимі класи:

```text
confirmed_user
canonical_example
repository_derived
package_confirmed
official_schema
model_proposed
unknown
```

Правила:

- `confirmed_user`, `canonical_example`, `repository_derived`, `package_confirmed`, `official_schema` можуть дозволяти materialization;
- `model_proposed` і `unknown` не можуть використовуватися у фінальному executable блоці;
- непідтверджене значення має залишатися explicit open gap;
- назва endpoint, файлу або поля не є доказом його schema чи semantics.

### 4.4. Adversarial defect review

Після звичайної перевірки APF має запускати окремий негативний review.

Він повинен шукати:

- правдоподібні, але непідтверджені параметри;
- поля, яких немає в canonical schema;
- пропущені required fields;
- неправильні path conventions;
- змішування source path, delta path і REST path;
- перенесення legacy contracts зі старих прикладів;
- неправильну operation semantics;
- action/rollback contract drift;
- значення, виведені лише з назви endpoint;
- приховані assumptions, які не позначені як assumptions;
- суперечності між документом і repository/package evidence.

Ключове контрольне питання:

> Що в цьому документі може бути зовнішньо неправильним, хоча внутрішньо виглядає правильним?

### 4.5. Cross-artifact review

Важливий документ не можна перевіряти ізольовано.

APF має зіставляти його з пов’язаними артефактами:

- Passport;
- Jira task;
- Manual QA;
- automation spec;
- implementation prompt;
- API contract;
- rollback contract;
- package manifest;
- confirmed user decisions.

Наприклад, якщо Manual QA використовує `ChangeRecord.status`, а implementation prompt досі містить `ChangeRecord.data.status`, confirmation має блокуватися.

### 4.6. Selective reconciliation джерел

При конфлікті між canonical example і поточним package contract не можна:

- сліпо копіювати весь приклад;
- повністю відкидати приклад;
- вибирати новіший файл лише за timestamp.

Потрібно виконувати selective reconciliation:

```text
current confirmed contracts
+ сумісні canonical-example invariants
+ repository evidence
→ reconciled artifact
```

У прикладі з `publish-mongo-patch`:

- REST payload shape переноситься;
- `mongoId`, `operation`, `preview`, `gzip`, `operations`, `row` переносяться;
- legacy `data.status` не переноситься;
- актуальний `ChangeRecord.status` зберігається;
- REST operation path не отримує зайвий `item.`.

### 4.7. Targeted invalidation

Після знайденого дефекту APF не повинен автоматично скидати весь документ.

Необхідно визначити defect scope.

Для дефекту request contract потрібно:

- зберегти підтверджені test cases;
- зберегти Mongo lookup;
- зберегти business expectations;
- зберегти інші коректні секції;
- інвалідувати action REST request blocks;
- інвалідувати rollback REST request blocks;
- повторно перевірити пов’язані API-contract assertions.

Приклад статусу:

```text
patch_request_contract_correction_required
```

Це зменшує втрату підтвердженого state і робить correction traceable.

### 4.8. Обов’язкова перевірка після виправлення

Correction не повинна автоматично означати `passed`.

Після targeted regeneration потрібно повторно виконати:

- structural validation;
- contract evidence validation;
- adversarial defect review;
- cross-artifact consistency;
- regression checks для знайденого класу дефекту.

Лише після цього artifact може знову стати confirmation-eligible.

## 5. Нові APF gates

Рекомендовано додати такі універсальні gates:

```text
EVIDENCE-COVERAGE-01
Кожне executable або contract-sensitive значення має допустиме джерело.

NO-UNSUPPORTED-INFERENCE-01
Невідомий contract не заповнений типовим або правдоподібним припущенням.

CANONICAL-CONTRACT-01
Artifact відповідає canonical example, official schema або repository-derived contract.

CURRENT-VERSION-RECONCILIATION-01
Legacy поля зі старих прикладів не перевизначають актуальні confirmed contracts.

PATH-DOMAIN-01
Source path, ChangeRecord delta path і REST operation path розділені та підтверджені.

ROLLBACK-CONTRACT-01
Rollback використовує той самий підтверджений endpoint contract.

CROSS-ARTIFACT-01
Пов’язані артефакти використовують однакові confirmed contracts.

ADVERSARIAL-REVIEW-01
Виконано негативний пошук прихованих assumptions і зовнішніх невідповідностей.

POST-CORRECTION-REVIEW-01
Після correction виконана незалежна повторна перевірка.
```

Результат кожного gate:

```text
passed
failed
not-applicable
```

Blocking defect не можна приховувати як warning.

## 6. Формат результату постперевірки

Для кожного важливого документа APF має створювати компактний review record:

```yaml
post_generation_review:
  artifact_id: ""
  artifact_version: ""
  criticality: critical | high | normal
  status: passed | failed | passed_with_notes

  reviewed_sections: []
  authoritative_sources: []

  defects_found:
    - defect_id: ""
      severity: blocker | high | medium | low
      section: ""
      description: ""
      evidence: ""
      invalidation_scope: ""

  assumptions_found: []
  evidence_gaps: []
  conflicting_sources: []

  corrected_sections: []
  preserved_sections: []
  unresolved_risks: []

  cross_artifact_checks: []
  regression_checks: []

  confirmation_eligible: true | false
```

Цей record може бути:

- частиною artifact metadata;
- окремим release evidence;
- записом Execution Trace;
- підставою для targeted regeneration.

## 7. Зміни в confirmation semantics

Поточна модель підтвердження має бути посилена.

Artifact не може вважатися confirmed лише тому, що:

- він повний;
- він красиво оформлений;
- JSON/YAML валідний;
- action і rollback внутрішньо узгоджені;
- користувач автоматично підтвердив package change.

Для critical artifact confirmation eligibility має вимагати:

```text
structural_validation = passed
contract_evidence_validation = passed
adversarial_defect_review = passed
cross_artifact_review = passed
post_correction_review = passed | not-applicable
blocking_evidence_gaps = 0
```

Автоматичне підтвердження може підтверджувати запропоновану зміну процесу, але не повинно обходити технічні gates достовірності.

## 8. Зміни в Execution Trace

APF має фіксувати:

- які джерела були використані;
- які поля були підтверджені;
- які значення були model-proposed;
- які defects знайдені;
- які секції інвалідовано;
- які секції збережено;
- що було перегенеровано;
- які gates пройдені після correction;
- хто або що підтвердило artifact.

Приклад подій:

```text
POST_GENERATION_REVIEW_STARTED
UNSUPPORTED_INFERENCE_DETECTED
ARTIFACT_SECTION_INVALIDATED
TARGETED_REGENERATION_COMPLETED
POST_CORRECTION_REVIEW_PASSED
ARTIFACT_CONFIRMATION_ELIGIBLE
```

## 9. Regression strategy

Кожен знайдений production-like defect повинен ставати regression case.

Для розглянутого випадку:

### Негативний кейс

Payload:

```json
{
  "database": "dossier",
  "filter": {},
  "update": {
    "$set": {}
  }
}
```

без repository або canonical evidence повинен дати:

```text
unsupported_model_inference
confirmation_eligible = false
```

### Позитивний кейс

Payload із:

```text
mongoId
collection
operation
preview
gzip
operations[]
operations[].path
operations[].row
operations[].value
```

може пройти лише за наявності evidence для кожного ключа.

### Version reconciliation кейс

Canonical example містить:

```text
data.status
```

але current package contract містить:

```text
ChangeRecord.status
```

Очікування:

- REST payload shape переноситься;
- legacy status path відкидається;
- current package contract має пріоритет.

## 10. Очікуваний результат для APF

Після внесення цих змін APF має перейти від моделі:

```text
документ сформований
→ документ структурно валідний
→ документ підтверджений
```

до моделі:

```text
документ сформований
→ структура перевірена
→ технічні твердження звірені з evidence
→ виконано негативний defect review
→ перевірена узгодженість з іншими артефактами
→ дефекти виправлені точково
→ correction повторно перевірена
→ документ допущений до підтвердження
```

Це не усуне всі можливі помилки моделі, але суттєво зменшить найнебезпечніший клас дефектів: переконливі, внутрішньо узгоджені та технічно правдоподібні вигадки в operational artifacts.

## 11. Підсумкове формулювання

Ми прийшли до необхідності постгенераційної перевірки не через одиничну помилку в одному runbook, а через системну властивість генеративного процесу: за відсутності підтвердженого контракту модель може створити правдоподібну технічну конструкцію, а стандартна structural review не відрізнить її від справжнього рішення.

Тому APF має окремо перевіряти не лише якість форми документа, а й походження, доказовість та зовнішню достовірність кожного критичного твердження. Для важливих документів це повинно стати обов’язковим blocking етапом перед confirmation і release.
