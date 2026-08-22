# Verification performance policy

Use the cheapest evidence that is sufficient for the current development step.

## Local TDD loop

```bash
python verify_editor.py fast
```

Budget: 15 seconds target. Any stage exceeding its encoded timeout is treated as a performance failure to investigate.

## Affected-area regression

```bash
python verify_editor.py affected --changed editor_service.py
python verify_editor.py affected --changed web/app.js
```

This always includes `fast`, then adds only the relevant broader slice.

## Exhaustive regression

```bash
python verify_editor.py full
```

This is an explicit expensive gate. It is not run after every small edit. Python has a 120-second hard budget; JS has a 45-second hard budget.

## Release sequence

1. targeted RED/GREEN tests;
2. `verify_editor.py fast`;
3. `affected` only when the changed subsystem warrants it;
4. one `full` run before release candidate finalization;
5. regenerate manifest;
6. package ZIP;
7. fresh-extract manifest + fast smoke.
