# Testing Ordo Visual Graph Generator

This utility has a pytest suite under `tests/`.

## Install test dependencies

```bash
pip install -r requirements-dev.txt
```

Graphviz is required only for SVG/PNG rendering tests:

```bash
dot -V
```

## Run tests

From the utility root:

```bash
pytest -q
```

## What is covered

The tests cover:

- branch labels from `question` text;
- branch labels from `update_state.selected_path_label`;
- branch labels from `update_state.test_coverage_level`;
- free-text direct transitions do not render noisy `answer` labels;
- unknown transition targets fail fast;
- gate ids are valid transition targets;
- terminal artifact extraction from question bullets;
- `--artifact-mode none`;
- `--artifact-mode package`;
- `subtree` focus mode;
- `context` focus mode;
- SVG line breaks through Graphviz, when `dot` is installed.
