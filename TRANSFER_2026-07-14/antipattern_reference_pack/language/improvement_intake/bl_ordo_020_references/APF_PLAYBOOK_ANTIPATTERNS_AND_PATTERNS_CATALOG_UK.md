# Каталог антипатернів і рекомендованих патернів для APF та History Event Analysis Playbook

## 1. Призначення

Цей документ узагальнює класи помилок, які проявилися під час створення, виправлення, міграції та валідації History Event Analysis Playbook. Мета — перенести знання з окремих інцидентів у формальні правила головного APF-пакета.

Для кожного випадку наведено:

- антипатерн;
- реальний приклад;
- ризик;
- спосіб виправлення;
- рекомендований патерн;
- blocking checks.

---

# 2. Структура процесу

## AP-01. Кілька responsibilities в одному вузлі

**Антипатерн:** один node одночасно збирає вимоги, приймає рішення, генерує artifact, перевіряє його та виконує перехід.

**Приклад:** в одному логічному вузлі могли змішуватися аналіз ChangeRecord, побудова candidate contract, генерація Manual QA, перевірка API payload і підтвердження документа.

**Ризик:** неможливо визначити точний scope defect, targeted rollback і regeneration.

**Як вирішували:** розділили rail:

```text
COLLECT_CONTRACT
→ VALIDATE_CONTRACT
→ GENERATE_ARTIFACT
→ REVIEW_ARTIFACT
→ CONFIRM_ARTIFACT
```

**Рекомендований патерн:** `Single Responsibility Process Node`.

**Blocking checks:** `NODE-RESPONSIBILITY-01`, `NODE-MULTI-MUTATION-01`.

---

## AP-02. Кілька типів артефактів в одному вузлі

**Антипатерн:** один вузол генерує Passport, Jira, Manual QA, automation spec та implementation prompt.

**Приклад:** одна відповідь могла одночасно materialize бізнес-контракт, QA runbook і implementation instructions.

**Ризик:** confirmation одного документа неявно підтверджує інші; локальний defect інвалідує надто великий scope.

**Як вирішували:** окремий generation node і gate для кожного artifact type.

**Рекомендований патерн:** `One Artifact Type per Generation Node`.

**Blocking checks:** `ARTIFACT-NODE-01`, `MULTI-TEMPLATE-MATERIALIZATION-01`, `CONFIRMATION-SCOPE-01`.

---

## AP-03. Process branch і control action змішані

**Антипатерн:** pause, resume, regenerate, return або confirm моделюються як domain branches.

**Приклад:** regeneration могла інтерпретуватися як нова бізнес-гілка або повернення до root.

**Ризик:** втрата active node і плутанина між керуванням процесом та бізнес-рішенням.

**Рішення:** окремо моделювати `process branch`, `control action`, `maintenance action`.

**Патерн:** `Separated Control Plane`.

**Blocking checks:** `CONTROL-BRANCH-SEPARATION-01`, `ACTIVE-NODE-PRESERVATION-01`.

---

# 3. State і навігація

## AP-04. Повернення до root після локальної помилки

**Антипатерн:** correction або upgrade запускає весь intake заново.

**Приклад:** після виправлення `ChangeRecord.status` або endpoint contract міг повторно запускатися процес із нуля.

**Ризик:** втрата confirmed state, повторні питання, суперечливі відповіді.

**Рішення:** state-preserving migration:

```text
snapshot
→ map logical node
→ restore state
→ reconcile affected fields
→ validate
→ return to same node
```

**Патерн:** `State-Preserving Migration`.

**Blocking checks:** `NO-ROOT-RESTART-01`, `STATE-EQUIVALENCE-01`, `NODE-MAPPING-01`.

---

## AP-05. Втрата return point після maintenance branch

**Антипатерн:** correction branch завершується, але процес не знає, куди повертатися.

**Приклад:** після `v0.8.35` exact authoring node, з якого розпочався maintenance, не був явно зафіксований у видимому state.

**Ризик:** процес лишається між завершеним maintenance і невідновленою основною rail.

**Рішення:** зберігати:

```yaml
origin_node:
return_node:
suspended_question:
resume_condition:
```

**Патерн:** `Maintenance Return Point`.

**Blocking checks:** `MAINTENANCE-RETURN-01`, `SUSPENDED-STATE-01`.

---

## AP-06. Неявний successor

**Антипатерн:** після завершення вузла немає явного наступного кроку.

**Приклад:** package generation могла передчасно завершити процес, хоча ще були impact assessment, reload prompt і final ZIP verification.

**Ризик:** premature completion, пропуск mandatory nodes, active dead ends.

**Рішення:** direct-successor validation і terminal eligibility.

**Патерн:** `Explicit Successor Contract`.

**Blocking checks:** `DIRECT-SUCCESSOR-01`, `TERMINAL-ELIGIBILITY-01`, `ACTIVE-DEAD-END-01`.

---

# 4. Контракти і дані

## AP-07. Застарілий field path

**Антипатерн:** старий шлях поля лишається після зміни контракту.

**Приклад:**

Неправильно:

```text
ChangeRecord.data.status
```

Правильно:

```text
ChangeRecord.status
```

При цьому `ChangeRecord.data.root_id` і `ChangeRecord.data.item` лишаються вкладеними.

**Ризик:** неправильний pre-filter і cross-artifact inconsistency.

**Рішення:** canonical declaration field path + versioned regression.

**Патерн:** `Field Path Source of Truth`.

**Blocking checks:** `FIELD-PATH-IDENTITY-01`, `STATUS-PATH-01`, `CROSS-ARTIFACT-PATH-01`.

---

## AP-08. Сліпе копіювання canonical example

**Антипатерн:** приклад переноситься повністю без version reconciliation.

**Приклад:** із canonical example треба було взяти REST payload shape, але не legacy `data.status`.

**Ризик:** старі поля повертаються в нову версію.

**Рішення:**

```text
current confirmed contracts
+ compatible canonical-example invariants
+ repository evidence
→ reconciled artifact
```

**Патерн:** `Selective Canonical Reuse`.

**Blocking checks:** `CURRENT-VERSION-RECONCILIATION-01`, `CANONICAL-EXAMPLE-SCOPE-01`.

---

## AP-09. Schema виводиться з назви endpoint

**Антипатерн:** назва endpoint використовується як доказ request schema.

**Приклад:** із `publish-mongo-patch` було помилково виведено:

```json
{
  "filter": {},
  "update": {
    "$set": {}
  }
}
```

Фактичний contract містив `mongoId`, `operation`, `preview`, `gzip`, `operations[]`.

**Ризик:** правдоподібний, але вигаданий executable request.

**Рішення:** `Do not infer REST request schemas from endpoint names.`

**Патерн:** `Evidence-Backed Endpoint Contract`.

**Blocking checks:** `NO-INFERENCE-FROM-ENDPOINT-NAME-01`, `REQUEST-SCHEMA-EVIDENCE-01`.

---

## AP-10. Змішування path domains

**Антипатерн:** source path, ChangeRecord delta path і REST patch path вважаються однаковими.

**Приклад:**

Неправильно в REST operation:

```text
item.capital.value
```

Правильно:

```text
capital.value
```

**Ризик:** patch адресує неправильне поле.

**Рішення:** окремі domains:

```text
source_document_path
change_record_delta_path
rest_patch_operation_path
```

**Патерн:** `Typed Path Domains`.

**Blocking checks:** `PATH-DOMAIN-01`, `PATH-PREFIX-01`, `REST-PATH-CONVENTION-01`.

---

## AP-11. Placeholder alias замість exact identity

**Антипатерн:** placeholder не збігається з exact key.

**Приклад:**

Неправильно:

```text
{old_value}
```

Правильно:

```text
{old#value}
```

**Ризик:** template rendering failure і прихований alias mapping.

**Рішення:**

```text
BUILD_ITEM_VALUES_KEYS
→ DERIVE_TEMPLATE_PLACEHOLDERS_FROM_KEYS
→ GENERATE_TEXT_TEMPLATE
→ PLACEHOLDER_IDENTITY_GATE
```

**Патерн:** `Exact Placeholder Identity`.

**Blocking checks:** `PLACEHOLDER-IDENTITY-01`, `BILINGUAL-PLACEHOLDER-CONSISTENCY-01`.

---

# 5. Evidence і генерація

## AP-12. Model-proposed значення стає confirmed technical value

**Антипатерн:** модель заповнює невідомий contract правдоподібним значенням.

**Приклад:** `database`, `filter`, `update`, `$set` не мали evidence, але потрапили в executable runbook.

**Ризик:** hallucinated operational contract.

**Рішення:** provenance classification:

```text
confirmed_user
canonical_example
repository_derived
package_confirmed
official_schema
model_proposed
unknown
```

`model_proposed` і `unknown` блокують executable generation.

**Патерн:** `Evidence per Technical Value`.

**Blocking checks:** `EVIDENCE-COVERAGE-01`, `MODEL-PROPOSED-BLOCK-01`.

---

## AP-13. Open gap приховується правдоподібним JSON

**Антипатерн:** замість явної прогалини генерується “тимчасовий” executable body.

**Правильно:**

```text
REST request body: repository-derived open gap.
```

**Ризик:** draft виглядає production-ready і може бути виконаний.

**Рішення:** unknown schema → explicit gap, no executable payload.

**Патерн:** `Fail Closed on Unknown Contract`.

**Blocking checks:** `OPEN-GAP-VISIBILITY-01`, `EXECUTABLE-BLOCKED-WHEN-UNKNOWN-01`.

---

## AP-14. Автопідтвердження обходить технічні gates

**Антипатерн:** “підтверджую автоматом” трактується як право підтвердити технічно недоведений artifact.

**Ризик:** user approval підміняє correctness.

**Рішення:** розділити approval intent, technical eligibility і artifact confirmation.

**Патерн:** `Approval Does Not Override Safety Gates`.

**Blocking checks:** `CONFIRMATION-ELIGIBILITY-01`, `APPROVAL-SCOPE-01`.

---

# 6. Валідація

## AP-15. Structural validation приймається за correctness validation

**Антипатерн:** документ вважається правильним, бо JSON валідний, секції присутні, action і rollback узгоджені.

**Приклад:** REST payload був синтаксично правильний, але контрактно хибний.

**Рішення:**

```text
syntax
→ structure
→ evidence
→ contract
→ cross-artifact
→ adversarial review
```

**Патерн:** `Layered Validation`.

**Blocking checks:** `CONTRACT-EVIDENCE-VALIDATION-01`, `ADVERSARIAL-REVIEW-01`.

---

## AP-16. Немає перевірки після correction

**Антипатерн:** artifact автоматично стає `passed` після виправлення.

**Приклад:** після заміни REST payload треба повторно перевірити action, rollback, paths, status і залежні artifacts.

**Патерн:** `Correction Requires Independent Revalidation`.

**Blocking checks:** `POST-CORRECTION-REVIEW-01`, `AFFECTED-REGRESSION-01`.

---

## AP-17. Review не шукає “правдоподібно неправильне”

**Антипатерн:** reviewer шукає лише явні defects.

**Контрольне питання:**

```text
Що в цьому документі може бути зовнішньо неправильним,
хоча внутрішньо виглядає правильним?
```

**Патерн:** `Adversarial Review Pass`.

**Blocking checks:** `NEGATIVE-REVIEW-QUESTION-01`, `HIDDEN-ASSUMPTION-01`.

---

# 7. Invalidation і correction

## AP-18. Увесь artifact інвалідується через локальний defect

**Антипатерн:** дефект REST section скидає весь Manual QA package.

**Приклад:** у `LU_CHANGE_CAPITAL` коректними були test cases, lookup і business expectations; помилковими — лише action/rollback REST blocks.

**Рішення:** targeted status:

```text
patch_request_contract_correction_required
```

**Патерн:** `Section-Level Invalidation`.

**Blocking checks:** `INVALIDATION-SCOPE-01`, `PRESERVED-SECTIONS-01`.

---

## AP-19. Correction без impact assessment

**Антипатерн:** виправлення в одному місці не поширюється на prompts, templates, tests і compiled outputs.

**Приклад:** `ChangeRecord.data.status` було змінено не всюди.

**Патерн:** `Dependency-Aware Correction`.

**Blocking checks:** `CHANGE-IMPACT-01`, `DEPENDENCY-COVERAGE-01`.

---

# 8. Templates і prompts

## AP-20. Старий prompt лишається активним

**Антипатерн:** нова версія prompt є в registry, але node посилається на стару.

**Ризик:** fix формально існує, але не застосовується.

**Патерн:** `Prompt Reference Integrity`.

**Blocking checks:** `PROMPT-REGISTRY-01`, `ACTIVE-PROMPT-VERSION-01`.

---

## AP-21. Prompt містить приклад забороненого значення

**Антипатерн:** правило виправлено, але example лишився старим.

**Приклад:** у prompt залишився `{old_value}`, хоча contract вимагав `{old#value}`.

**Патерн:** `Examples Are Part of the Contract`.

**Blocking checks:** `PROMPT-EXAMPLE-CONSISTENCY-01`, `FORBIDDEN-TOKEN-SCAN-01`.

---

# 9. Package і release engineering

## AP-22. Ручне редагування compiled outputs

**Антипатерн:** source змінюється, а compiled artifacts правляться вручну.

**Ризик:** `program.ir.json`, `program.ordo.view`, manifest і hashes розходяться.

**Патерн:** `Source Is the Only Editable Truth`.

**Blocking checks:** `SOURCE-DERIVED-SYNC-01`, `TARGET-MANIFEST-HASH-01`.

---

## AP-23. Runtime/cache файли потрапляють у ZIP

**Антипатерн:** у release входять `__pycache__`, `.pyc`, transient reports і cache.

**Патерн:** `Clean Source Package`.

**Blocking checks:** `CLEAN-PACKAGE-01`, `FORBIDDEN-ENTRY-01`, `POST-UNPACK-VALIDATION-01`.

---

## AP-24. Generated outputs не відокремлені від source

**Антипатерн:** source, compiled, runtime reports, evidence і cache змішані.

**Рішення:**

```text
generated_outputs/
runtime_reports/
release_evidence/
cache/
```

**Патерн:** `Artifact Class Isolation`.

**Blocking checks:** `ARTIFACT-ROOT-SEPARATION-01`, `SOURCE-OF-TRUTH-PROTECTION-01`.

---

## AP-25. Runtime metadata не відповідає package version

**Антипатерн:** у runtime лишається стара версія або старі hashes.

**Патерн:** `Version and Hash Reconciliation`.

**Blocking checks:** `RUNTIME-METADATA-01`, `PACKAGE-VERSION-IDENTITY-01`.

---

# 10. Testing і regression

## AP-26. Production defect не стає regression case

**Антипатерн:** defect виправлено, але test catalog не оновлено.

**Приклади:**

- `ChangeRecord.data.status`;
- `{old_value}`;
- generic `$set` payload;
- premature completion;
- skipped impact assessment.

**Патерн:** `Every Confirmed Defect Becomes a Regression`.

**Blocking checks:** `DEFECT-TO-REGRESSION-01`, `REAL-CASE-REPLAY-01`.

---

## AP-27. Неструктуровані expectations

**Антипатерн:**

```yaml
expected: "..."
```

замість machine-readable objects.

**Ризик:** parser exception і неможливість точно перевірити outcome.

**Патерн:** `Machine-Readable Test Expectations`.

**Blocking checks:** `TEST-SCHEMA-01`, `EXPECTATION-OBJECT-01`.

---

## AP-28. Перевірка лише до пакування

**Антипатерн:** робоче дерево валідне, але фактичний ZIP після збірки не перевіряється.

**Рішення:**

```text
build ZIP
→ unpack ZIP
→ re-run validators
→ verify forbidden entries
→ verify required evidence
```

**Патерн:** `Post-Build Independent Verification`.

**Blocking checks:** `POST-BUILD-VERIFY-01`, `REPRODUCIBLE-RELEASE-01`.

---

# 11. Позитивні патерни APF

- `P-01 Single Responsibility Node`
- `P-02 One Artifact per Generation Node`
- `P-03 State-Preserving Migration`
- `P-04 Maintenance Return Point`
- `P-05 Evidence-Backed Contract`
- `P-06 Fail Closed on Unknown Schema`
- `P-07 Selective Canonical Reconciliation`
- `P-08 Typed Path Domains`
- `P-09 Exact Placeholder Identity`
- `P-10 Layered Validation`
- `P-11 Adversarial Review`
- `P-12 Section-Level Invalidation`
- `P-13 Dependency-Aware Correction`
- `P-14 Source-Only Editing`
- `P-15 Artifact Class Isolation`
- `P-16 Every Defect Becomes a Regression`
- `P-17 Post-Correction Review`
- `P-18 Post-Build Verification`

---

# 12. Рекомендована schema запису

```yaml
antipattern:
  id: AP-XX
  name: ""
  category: process | state | contract | evidence | validation | artifact | release | testing

  description: ""
  trigger_conditions: []
  observable_symptoms: []

  example:
    context: ""
    wrong_behavior: ""
    expected_behavior: ""

  risks: []
  root_cause: ""

  correction:
    invalidation_scope: ""
    preserved_state: []
    regeneration_scope: []
    required_revalidation: []

  recommended_pattern:
    pattern_id: P-XX
    name: ""
    rule: ""

  blocking_gates: []
  regression_cases: []
```

---

# 13. Як інтегрувати в головний APF-пакет

## Authoring guidance

Під час створення node, graph, contract або template перевіряти рішення проти каталогу антипатернів.

## Lint rules

Автоматизувати:

- multi-responsibility node detection;
- multiple artifact outputs;
- missing successor;
- forbidden legacy paths;
- stale prompt refs;
- source/compiled hash drift;
- forbidden ZIP entries.

## Runtime gates

Блокувати:

- executable generation без evidence;
- unknown schema materialization;
- confirmation без post-generation review;
- maintenance exit без return point;
- completion без terminal eligibility.

## Real-case replay

Кожен антипатерн повинен мати:

- negative case;
- positive case;
- correction case;
- no-regression replay.

---

# 14. Висновок

Проблеми поточного playbook-а були не випадковими одиничними помилками. Вони утворили повторювані класи: змішування responsibilities, змішування artifact types, втрата state, застарілі paths, сліпе копіювання прикладів, inference contract із назви, приховування unknown як готового output, недостатня validation depth, надто широка invalidation, відсутність impact assessment, drift між source і derived artifacts та відсутність post-build verification.

Формальний каталог антипатернів дозволить APF виявляти ці проблеми не після релізу, а ще під час authoring, generation, review, migration і package validation.
