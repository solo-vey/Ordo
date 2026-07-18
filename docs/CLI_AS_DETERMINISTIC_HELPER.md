# CLI as Deterministic Helper

У M26 CLI перепозиціонується як deterministic helper layer.

CLI не є головним діалоговим runtime. Головний активний виконавець — ШІ.

CLI допомагає ШІ:

- перевіряти синтаксис Ordo package;
- компілювати source YAML у Semantic JSON IR;
- запускати tests і coverage;
- перевіряти deterministic gates;
- виявляти missing fields або inconsistency;
- формувати machine-readable diagnostics.

Raw CLI output за замовчуванням призначений для AI/developer interpretation. Human-facing response має формувати ШІ людською мовою.
