> M64.2 note: this conceptual model is now complemented by `language/PROCESS_RAIL_SCHEMA_CONVENTION.md`, `language/CONVERSATION_SEMANTICS.md`, and `language/registry/INTERACTION_PROCESS_RAIL_CONVERSATION_VALUES.md`. M64.2 keeps process rail as a docs/schema convention, not a new opcode or runtime-core implementation.

# 11. Process Rail Model

## 1. Статус

**Ordo language line:** v0.12  
**Milestone:** M26 — Process Rail Reframing  
**Статус:** conceptual extension

## 2. Призначення

Process Rail — центральна модель Ordo для стабілізації AI-guided процесів.

Ordo не вимагає повністю детермінованого діалогу. Діалог веде ШІ. Process Rail фіксує маршрут, стан, gates, allowed deviations, backtracking і output readiness.

## 3. Базова формула

```text
Human ↔ AI
        ↓
   Process Rail
        ↓
Semantic JSON IR
        ↓
Deterministic helper tools
        ↓
AI explanation / next move
```

## 4. Мінімальна source-модель

```yaml
interaction_model:
  human_role: pm
  ai_role: ordo_developer
  proactive_ai_behavior: required
  raw_tool_output_policy: ai_interprets_before_user

process_rail:
  rail_id: example_rail
  purpose: guide_ai_without_replacing_ai_reasoning
  state_tracking: required
  allow_deviation: true
  require_resume_after_deviation: true
  backtracking: enabled

conversation_semantics:
  on_unmatched_input:
    strategy: classify_and_route
    allowed_classes:
      - answer_current_question
      - answer_future_question
      - correction_previous_answer
      - clarification_request
      - domain_context
      - approval
      - refusal
      - out_of_scope
    require_state_validation: true
```

## 5. AI roles

### AI Ordo Developer

Створює або модернізує Ordo-проєкт через діалог із PM: проектує YAML, запускає checks, компілює Semantic JSON IR і пояснює стан.

### AI Ordo Executor

Виконує готовий Ordo-проєкт: читає Semantic JSON IR, веде людину по процесу, обробляє відхилення, викликає deterministic helper tools і пояснює наступні кроки.

## 6. CLI role

CLI є deterministic helper layer. Він може виконувати lint, compile, test, coverage, state validation, gate checks і next-step suggestions. CLI не є головним conversational runtime.

## 7. Semantic JSON IR impact

Semantic JSON IR має містити process rail semantics:

```json
{
  "process_rail": {},
  "conversation_semantics": {},
  "backtracking_rules": [],
  "tool_hooks": [],
  "human_explanation_policy": {}
}
```
