# Optional Vibe dependencies

The original Vibe `0.1.2` snapshot bundled Playbook Simulation Kit ZIP files.
They are not committed to this repository-native source package because they
are versioned binary dependencies.

The core Vibe authoring source, templates, patterns, validators, and the three
release profiles do not require those ZIP files. Simulation-specific workflows
must declare and obtain the exact Simulation Kit release separately, then
record its version and SHA-256 in run evidence.

Run the optional strict simulation contour only after supplying that dependency:

```bash
python tools/run_verification_profile.py . --vibe-root . --through PRE_EDITOR --include-simulation
```
