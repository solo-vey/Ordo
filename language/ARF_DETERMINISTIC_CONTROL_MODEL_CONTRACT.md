# ARF Deterministic Control Model Contract v1

Status: implemented for BL-ORDO-027 step 1.

## Core defaults

```yaml
runtime_mode: PROCESS_EXECUTOR_ONLY
decision_model: closed_world
default_role: executor
undefined_action: blocked_missing_instruction
```

## Modes

- `EXECUTION_MODE`: виконує лише allowlisted дії активного вузла. Зміна дизайну або package/repository mutation заборонені.
- `DESIGN_MODE`: дозволяє аналіз і пропозиції, але не фактичну mutation та не заяву про implementation.
- `AUTHORIZED_MAINTENANCE_MODE`: дозволяє mutation лише після окремої explicit authorization і лише в погодженому scope.

Неявний перехід між режимами заборонений.

## Closed-world rule

Дозволено лише те, що явно визначено активним node contract, поточним mode contract і чинною authorization. Невідома дія або transition переводить runtime у `blocked_missing_instruction`.

## Ambiguity rule

При відсутній інструкції дозволена лише дія `request_exact_user_decision`. Fallback на `best judgement` заборонено.

## Boundary of this step

Цей крок визначає загальний control model. Профілі контрактів вузлів підключені через `ARF Node Contract Profiles v1`; кожен executable node має рівно один profile, а multi-profile responsibility вимагає split node.
