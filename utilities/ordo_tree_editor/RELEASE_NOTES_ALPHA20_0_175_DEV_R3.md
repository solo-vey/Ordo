# Ordo Tree Editor 0.2.0-alpha.20.0.175-dev

- Playbook Settings is now a subtabbed workspace.
- The existing language-defined settings catalog remains the default `Settings` subtab.
- Added `Global runtime infrastructure`, `Package/startup metadata`, and `Global verification policy` subtabs.
- New resource subtabs list only package text resources that are not reachable from any node/gate References view.
- Resource classification is structural/generic and does not depend on domain-specific filenames or values.
- Regression-test implementations and ordinary knowledge resources are intentionally not surfaced in these three Settings groups.
- Each listed resource can be opened in an inline read-only preview; Markdown is rendered and source files are shown verbatim.
- Canonical Ordo, compiler semantics, and runtime execution semantics are unchanged.
