# Розділ 77. Optional Flow Reuse

M77 додає до Ordo механізм повторного використання flow-фрагментів. Важлива межа: це **рекомендований механізм**, а не правило, яке змушує кожен playbook ділити процес на reusable flows.

Повторне використання доречне, коли одна й та сама логіка справді повторюється і має стабільний контракт.

```text
duplicate stable logic
→ reuse candidate
→ namespace/state contract
→ reference resolution
→ runtime provenance
```

## Namespace і state merge

Reusable flow має власний namespace. Його state не повинен мовчки перезаписувати state батьківського процесу.

Merge rules повинні явно визначати:

```text
input mapping
local state
exported state
conflict policy
```

Конфлікт без визначеного правила є blocking validation error.

## Compiler lowering

Compiler розв'язує flow references і створює runtime representation без другого source of truth. Reuse syntax є authoring layer; compiled IR отримує однозначні resolved references і provenance.

Нерозв'язане посилання, namespace collision або несумісний contract блокують compile/validation.

## Runtime semantics

Під час переходу в reusable flow runtime зберігає:

```text
caller
callee
entry transition
state mapping
return transition
provenance
```

Trace повинен показувати, що логіка була виконана через reused flow, а не виглядати як невідомий стрибок між вузлами.

## Advisory reuse detection

CLI може виявляти схожі flow-фрагменти і рекомендувати reuse. Але рекомендація не є автоматичним rewrite.

```text
reuse candidate detected → advisory
```

Автор вирішує, чи є логіка семантично спільною.

Головний принцип M77:

```text
reuse is optional;
conflicts are explicit;
compiler resolves;
runtime preserves provenance.
```
