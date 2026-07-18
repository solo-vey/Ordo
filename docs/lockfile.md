# Ordo dependency lockfile

`ordo.lock.json` фіксує resolved залежності Ordo-пакета: template sets, а надалі також libraries, profiles і domain packs.

## Навіщо це потрібно

Без lock-файлу пакет може згенерувати інші outputs після зміни registry або версії template set. M10 робить package output відтворюваним: release має знати, які саме шаблони, джерела й hash були використані.

## Команди

```bash
ordo lock packages/history_event_guided_intake
ordo validate-lock packages/history_event_guided_intake
ordo validate-release packages/history_event_guided_intake
```

## Формат

```json
{
  "lockfile_version": "1.0",
  "package": {
    "name": "history_event.guided_intake",
    "version": "0.1.0",
    "ordo_version": "0.12"
  },
  "dependencies": [
    {
      "kind": "output_template_set",
      "id": "history_event.guided_intake_outputs",
      "version": "0.1.0",
      "source": "package_registry",
      "hash": {
        "algorithm": "sha256-tree",
        "value": "..."
      }
    }
  ]
}
```

## Правило release

`validate-release` автоматично генерує й перевіряє lock-файл. Якщо resolved залежності не збігаються з `ordo.lock.json`, release має бути заблокований.
