# alpha.20.0.90-dev — portable verification runner

Fixes verification checks failing with `[Errno 2] No such file or directory: python`.

- Descriptor commands remain platform-neutral.
- `python`, `python3`, and `{python}` are normalized to the exact Editor interpreter (`sys.executable`).
- UI/catalog remain descriptor-driven.
- No verification semantics were changed.
