# Розділ 52. Runtime Checkpoint Discipline

M57 додає в Ordo Runtime Mode правило контрольних точок.

Ідея проста:

```text
one node at a time
one contract at a time
one decision at a time
earliest incomplete node wins
```

Це потрібно, щоб AI Ordo Developer не стискав кілька runtime-вузлів в одну відповідь. Якщо одночасно закриваються бізнесові поля, ChangeRecord, trigger/no-op і naming decisions, стає незрозуміло, який контракт реально підтверджений, а де ще є прогалина.

## Checkpoint table

`run_state` тепер має містити або отримувати від helper-команд `checkpoint_table`:

```json
{
  "current_node": "",
  "last_closed_node": "",
  "earliest_incomplete_node": "",
  "checkpoint_table": {},
  "forward_allowed": false,
  "open_required_fields": [],
  "node_merge_attempt_detected": false
}
```

## Як поводиться runtime

Якщо знайдена прогалина, Ordo не йде вперед. Він повертається до найранішого незавершеного вузла, питає одне focused питання і продовжує тільки після закриття цієї прогалини.

`next-step` має пріоритетно повертати `earliest_incomplete_node`, а не останній вузол, до якого хотіла перейти модель.

## Чому це важливо

Checkpoint discipline робить guided intake audit-friendly: у кожен момент видно, який вузол відкритий, які required fields підтверджені, які залишились відкритими, і чи дозволений рух уперед.

PDF книги не перегенеровувався в цьому кроці.


## Стандартні помилки checkpoint discipline

```text
ORDO-CHECKPOINT-001 node advanced before current contract closed
ORDO-CHECKPOINT-002 earlier mandatory node incomplete
ORDO-CHECKPOINT-003 multiple node contracts merged without allow_batch_confirmation
ORDO-CHECKPOINT-004 missing checkpoint table in run_state
ORDO-CHECKPOINT-005 next-step ignored earliest_incomplete_node
ORDO-CHECKPOINT-006 generated output requested while checkpoint gaps remain
```
