# Розділ 78. APF Replay, Prompt Registry і внутрішні mini-prompts

M78 перевіряє APF не лише статичними тестами, а на реальному сценарії створення процесу. Мета — побачити досвід аналітика: де процес зрозумілий, де виникає зайва фрикція, і де runtime або prompt layer підштовхує модель до небажаної поведінки.

## Real-case replay

APF replay проходить реальний case через існуючі process rails і фіксує:

```text
active step
analyst input
classification
state mutation
transition
friction finding
```

Це не заміна benchmark. Replay є product/process review конкретного applied module.

## Prompt Registry reconciliation

У міру розвитку APF з'явилися різні prompts: startup prompts, runtime prompts, handoff prompts і внутрішні task-specific prompts.

Prompt Registry потрібен, щоб для кожного prompt було видно:

```text
prompt id
purpose
owner layer
version
entry condition
expected output
replacement/deprecation relation
```

Дублікати або застарілі prompts не повинні мовчки залишатися активними.

## Internal mini-prompts

M78 також перевіряє, де внутрішній mini-prompt справді корисний. Mini-prompt доречний для локальної model-assisted задачі з чітким input/output contract.

Він не повинен замінювати:

```text
runtime transition rules
gates
state contracts
compiler validation
deterministic CLI checks
```

Головний принцип:

```text
use mini-prompts for bounded model work;
use APF/runtime contracts for process control.
```
