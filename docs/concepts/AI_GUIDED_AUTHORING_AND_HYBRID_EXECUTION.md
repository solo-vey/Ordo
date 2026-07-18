# AI-guided Authoring and Hybrid Execution

## 1. AI-guided authoring

Аналітик або PM не пише Ordo YAML руками. Він описує домен, ціль і правила природною мовою.

**AI Ordo Developer**:

- вивчає вимогу;
- ставить уточнюючі питання;
- пропонує структуру процесу;
- створює або оновлює Ordo YAML;
- запускає deterministic checks через CLI;
- компілює проєкт у Semantic JSON IR;
- пояснює PM-у проблеми, прогалини й наступні рішення людською мовою.

Цикл authoring:

```text
PM answer → AI analysis → YAML update → lint/compile → AI explanation → next PM decision
```

## 2. Hybrid execution

Готовий Ordo-проєкт виконується не як жорсткий Python wizard. Його виконує **AI Ordo Executor**, який тримається за Process Rail у Semantic JSON IR.

Цикл execution:

```text
Human input → AI interpretation → proposed state update → deterministic helper check → AI explanation → next move
```

## 3. Raw tool output policy

Детерміновані інструменти можуть повертати JSON, reports або diagnostics. За замовчуванням це machine-facing feedback для ШІ, а не відповідь людині.

Людина отримує пояснення:

```text
не: {"missing": ["event_alias"]}
а: Нам ще не вистачає короткого технічного alias події.
```

## 4. Proactive AI behavior

AI Ordo Developer і AI Ordo Executor не є пасивними кодувальниками. Вони мають:

- виявляти суперечності;
- попереджати про ризики;
- пропонувати варіанти;
- пояснювати наслідки вибору;
- просити рішення там, де deterministic rail не може сама зробити вибір.
