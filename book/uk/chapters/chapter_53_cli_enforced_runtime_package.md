# Розділ 53. CLI-enforced Runtime Package

Після появи runtime profile стало зрозуміло, що чистий runtime-пакет із `compiled/program.ir.json`, але без CLI, не дає повного enforcement. Модель могла прочитати IR напряму і пройти guided intake без deterministic helper reports.

Тому M59 вводить runtime trust layer: у runtime-пакеті має бути не тільки compiled IR, а й вбудований CLI, який є єдиним легальним інтерфейсом виконання.

```text
runtime package = compiled IR + start files + output templates + embedded runtime CLI + evidence layer
```

## Головне правило

```text
Runtime package без runnable CLI не є enforced runtime package.
```

`ordo package --profile runtime` додає:

```text
cli_embedded/ordo
cli_embedded/README.md
cli_embedded/ordo_pkg/ordo/...
```

Embedded CLI відкриває тільки runtime-команди. Команди authoring, compile, release і package у runtime wrapper блокуються.

## Hard-stop замість мʼякого fallback

Старий підхід дозволяв сказати `CLI status: not_run_cli_unavailable` і продовжити. Це було чесним самозвітом, але не змінювало поведінку.

Новий підхід:

```text
якщо cli_embedded/ordo не запускається → stop
```

Продовження можливе тільки після явної згоди користувача як nondeterministic fallback. У такому режимі кожен generated artifact має містити:

```text
DETERMINISM_NOT_ENFORCED
```

## Інкрементальний intake

M59.2 робить guided intake покроковим. Модель більше не повинна проходити весь сценарій сама. Для кожної відповіді користувача вона викликає:

```bash
cli_embedded/ordo intake . --submit <NODE_ID> --answer-file <tmp_answer.yaml>
```

CLI приймає або блокує перехід, пише evidence report і повертає digest. Модель не має права ставити наступне питання, доки submit не виконано.

## Evidence, snapshots і live state

Кожен accepted submit пише:

```text
reports/intake_submit_report.json
runtime/evidence/*_evidence.json
runtime/state_snapshots/SESSION-*.json
runtime/live_session_state.json
```

`live_session_state.json` — це UX-cache для автоматичного продовження сесії. Він не замінює evidence і не є самостійним доказом.

## Tamper-evident verification

M59.3 додає hash-chain snapshots, `verify-session`, canary detection і human final verify gate.

Команда:

```bash
cli_embedded/ordo verify-session .
```

перевіряє, що runtime session не дрейфувала непомітно. Очікувані чисті рядки:

```text
session-chain: intact
canary-scan: clean
```

Canary не забороняє пряме читання IR фізично, але робить витік доказовим: якщо службовий canary-текст зʼявляється в outputs або trace, session отримує failure.

## Trust level

M59 фіксує Level 1 без MCP і без sandbox:

```text
level_1_cli_in_package_hard_stop_hash_chain_human_verify
```

Це не криптографічний захист від зловмисника з повним доступом до файлової системи. Це захист від тихого дрейфу і випадкового обходу CLI.

## Формула

```text
CLI доступний → Runtime Mode enforced.
CLI недоступний → hard-stop.
CLI обійдено → session invalid / evidence missing / canary або chain failure.
```
