# Інструкції для моделі, яка формує ARF: authoritative context reload per node

## Мета

ARF має генерувати робочі playbook так, щоб модель-виконавець не покладалася на інструкції, прочитані лише на старті, або на власну пам’ять.

## Обов’язкове покращення control model

Для кожного вузла генерації, validation, confirmation, mutation, package assembly і completion ARF повинен створювати machine-checkable `mandatory_runtime_preflight`.

```yaml
mandatory_runtime_preflight:
  required: true
  execute_on_every_node_entry: true
  execute_after_reload: true
  execute_after_active_node_change: true
  execute_after_artifact_revision: true
  execute_after_context_change: true

  resolve_and_read:
    - immutable_global_execution_policy
    - active_node_contract
    - active_prompt
    - canonical_template_when_applicable
    - artifact_contract_when_applicable
    - validation_contract_when_applicable
    - confirmation_or_authorization_contract_when_applicable
    - current_confirmed_state
    - current_authorization_state

  provenance_required:
    - exact_path
    - sha256
    - package_version
    - authoritative_tree_revision

  memory_policy:
    prior_reading_is_not_execution_evidence: true
    instructions_from_memory_are_non_authoritative: true
    exact_files_must_be_reread: true
    summaries_do_not_replace_exact_contracts: true

  failure_behavior:
    missing_file: blocked_missing_instruction
    unread_file: blocked_missing_instruction
    ambiguous_reference: blocked_missing_instruction
    hash_mismatch: blocked_integrity_failure
    package_version_mismatch: blocked_integrity_failure
```

## Вимоги до ARF output

ARF повинен:

1. Створювати один immutable global execution-policy contract, а не копіювати його вручну в різних варіантах.
2. Для кожного значущого вузла визначати exact authoritative input set.
3. Додавати `AUTHORITATIVE_CONTEXT_RELOAD_GATE` як mandatory predecessor або еквівалентний глобально enforceable precondition.
4. Забороняти основну дію вузла до `preflight_status = passed`.
5. Не дозволяти вважати попереднє читання, summary або пам’ять evidence виконання.
6. Забороняти inferred/custom criteria в execution mode.
7. Повторювати preflight після reload, revision, node change або context change.
8. Зберігати provenance результату preflight у state/evidence.

## Effective instruction set

ARF має задавати фіксований порядок:

```text
immutable global policy
→ active node contract
→ node-specific authoritative inputs
→ confirmed state
→ authorization state
```

Нижчий рівень не може змінювати або послаблювати вищий.

## Regression checks для ARF

- exact validator не перечитаний перед validation → blocked;
- prompt path ambiguous → blocked;
- hash/version mismatch → integrity block;
- artifact revision без повторного preflight → blocked;
- критерії відтворені з пам’яті → blocked;
- mutation contract не перечитаний перед mutation → blocked;
- completion contracts не перечитані перед completion → blocked.

## Заборонений слабкий варіант

Недостатньо додати в startup prompt фразу «пам’ятай правила». ARF має створити runtime-enforced precondition, який перевіряється при кожному вході у вузол.
