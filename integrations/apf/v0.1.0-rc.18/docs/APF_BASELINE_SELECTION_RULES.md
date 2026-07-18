# APF baseline selection rules

## Rule

Always use the latest confirmed closure archive as source baseline.

## Current source baseline

```text
APF_TRANSFER_PACKAGE_CURRENT_STATE_RC9_CONFIRMED_CLOSURE.zip
```

## Archive classes

- working patch archive: a patch result that may not be an accepted baseline yet.
- confirmed closure archive: accepted baseline for the next APF patch.
- older closure archive: historical baseline; do not use for new work when a newer confirmed closure exists.

## Prohibition

The next model must not choose a baseline manually by similarity. It must use the latest confirmed closure archive.
