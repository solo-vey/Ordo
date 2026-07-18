# Node Helper — N_VALUE_SEMANTICS comparison and normalization

Use this helper when explaining old/new comparison, compared fields, ignored fields, and normalization.

## Goal

Help the analyst choose value semantics and normalization rules that are testable and safe for History Event creation.

## Explain simply

We need to know when a value has meaningfully changed. This can be raw comparison, trimmed comparison, case-normalized comparison, custom mapping, or strict no-normalization.

## Ask only what is needed

- Which field or fields are compared?
- Is there a stable matching key?
- Which technical or volatile fields must be ignored?
- Should empty, missing, and null be treated as equal or different?
- Is normalization only for comparison, or also for the final HistoryEvent value?

## Do not

- Do not create events from volatile technical fields alone.
- Do not hide null/missing/empty behavior.
- Do not invent normalization mappings.
- Do not claim that tests or validation succeeded.

## Authority boundary

This helper explains comparison. It does not update state by itself and does not override gates, contracts, or artifact requirements.
