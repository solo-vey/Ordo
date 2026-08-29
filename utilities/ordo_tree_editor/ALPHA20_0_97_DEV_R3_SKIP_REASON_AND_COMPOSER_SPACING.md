# alpha.20.0.97-dev

- Verification SKIPPED rows now expose a concrete reason subtype rather than only the generic word `SKIPPED`.
- Supported reason labels include: Not applicable, Needs runtime evidence, Needs selected gate, Needs bindings context, Needs template context, Needs tree-module context, Release-only, Toolkit-only, and Not in safe one-click.
- Descriptor `skip_kind` is the preferred future integration contract; UI also has a conservative fallback classifier for older descriptors.
- Verification JSON export includes `skip_kind` and `skip_label`.
- Chat composer outer spacing is balanced vertically; top and bottom spacing are equal in single-line, multiline, and expanded modes.
