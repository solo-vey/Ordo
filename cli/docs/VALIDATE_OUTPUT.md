# validate-output and Runtime Order

`validate-output` checks generated outputs after rendering.

M53 adds a stricter runtime order:

```text
validate-state must pass before generate-output
validate-output must pass before package
```

If output is generated before `validate-state` passed, CLI returns:

```text
ORDO-COV-005 output generated before validate-state passed
```

If a package archive is created before `validate-output` passed, CLI returns:

```text
ORDO-COV-006 package created before validate-output passed
```

This prevents a package from being distributed when the current run state or rendered artifacts were never deterministically checked.
