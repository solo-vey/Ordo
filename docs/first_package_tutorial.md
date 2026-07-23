# First Package Tutorial: Build Your First Ordo Package from Scratch

This tutorial presents the minimum practical path from an empty directory to a validated Ordo package.

Goal: create a package that you can:

- validate with `ordo lint`;
- compile into Semantic JSON IR with `ordo compile`;
- verify with `ordo test`;
- assess with `ordo coverage`;
- run through the minimal runtime with `ordo run`;
- complete as guided intake with `ordo intake`;
- package with `ordo package`.

> Important: `ordo-cli v0.1.0` is not yet an AI runtime. It is the first toolchain for structuring, validating, compiling, and providing a minimal runtime layer for an Ordo package.

---

## 1. Prerequisites

Python 3.10+ is required.

Go to the `cli` directory and install the CLI in editable mode:

```bash
cd cli
python -m pip install -e .
ordo --version
```

Expected output:

```text
ordo-cli 0.1.0
```

If you do not install the package, run commands as follows:

```bash
python -m ordo.cli --version
```

---

## 2. Create a New Package

From the workspace root:

```bash
cd cli
ordo init ../packages/my_first_package
```

Or, without installing it:

```bash
cd cli
python -m ordo.cli init ../packages/my_first_package
```

This creates the following structure:

```text
packages/my_first_package/
  README.md
  ordo.yml
  source/
    program.ordo.yaml
  tests/
    test_cases.yaml
  run_inputs/
    answers_success.yaml
    intake_success.yaml
  compiled/
  reports/
  runtime/
```

The package's main file is:

```text
packages/my_first_package/source/program.ordo.yaml
```

---

## 3. Minimal Ordo Source Structure

Open `source/program.ordo.yaml`.

A minimal Ordo program must contain:

```text
ordo
intent
contract
state
nodes
gates
assertions
outputs
freeform
```

For Ordo v0.12, these fields are especially important:

```yaml
ordo:
  version: "0.12"
  package: my.first_package
  control_level: standard
  execution_mode: chat_internal
```

### Required for Gates

Each gate must include `method` and `trust_class`:

```yaml
gates:
  - id: G_GOAL_PRESENT
    method: mechanical
    trust_class: deterministic
    condition: state.package_goal is not null
    on_fail: block
```

A gate without `method` is a compilation or linting error.

### Required for Assertions

Prohibitions are described through `ASSERTION`:

```yaml
assertions:
  - id: A_NO_FINAL_WITHOUT_APPROVAL
    polarity: not
    condition: final_package_created_without_approval
    phase: [runtime, test]
    severity: block
    on_fail: STOP
```

The CLI can then interpret this as a runtime prohibition and a test expectation.

### Required for Nodes

Each node must have a controlled fallback for unmatched input:

```yaml
on_unmatched_input:
  action: CLARIFY.REQUEST
  strategy: rephrase_and_narrow
  max_attempts: 2
  on_exhausted:
    action: escalate_to_human
    reason: user input does not match this node
```

This protects guided intake from uncontrolled improvisation.

---

## 4. Validate the Package with Lint

```bash
ordo lint ../packages/my_first_package
```

`lint` verifies the basic Ordo v0.12 rules:

- `ordo.version` equals `0.12`;
- `control_level` is present;
- `execution_mode` is present;
- each gate has `method`;
- each gate has `trust_class`;
- each assertion has `polarity`, `phase`, and `severity`;
- each node has `on_unmatched_input` or an explicit fallback;
- each include has `version`;
- each FREEFORM has `maturity`.

After successful validation, this file is created:

```text
reports/lint_report.json
```

---

## 5. Compile the Source into Semantic JSON IR

```bash
ordo compile ../packages/my_first_package
```

Compilation creates:

```text
compiled/program.ir.json
reports/compile_report.json
```

What the MVP compiler does:

- reads `source/program.ordo.yaml`;
- normalizes the package;
- expands local IDs into namespaced IDs;
- creates Semantic JSON IR;
- carries `gate.method`, `trust_class`, `ASSERTION`, and `execution_mode` into the IR;
- produces a compile report.

Example IR operation:

```json
{
  "op": "GATE.DEF",
  "id": "my.first_package.G_GOAL_PRESENT",
  "source_local_id": "G_GOAL_PRESENT",
  "method": "mechanical",
  "trust_class": "deterministic"
}
```

---

## 6. Add and Run Tests

Tests are stored here:

```text
tests/test_cases.yaml
```

Example test case:

```yaml
test_cases:
  - id: TC_GOAL_PRESENT_GATE
    fixture:
      state:
        package_goal: "Prepare a document"
    expected:
      gates:
        - id: G_GOAL_PRESENT
          method: mechanical
          trust_class: deterministic
          status: passed
```

Run:

```bash
ordo test ../packages/my_first_package
```

`ordo test` in v0.1.0 is a static test runner. It verifies that expected behavior is consistent with the Source:

- the expected node exists;
- the expected gate exists;
- the expected `method` matches the gate in the Source;
- the expected `trust_class` matches the gate in the Source;
- the expected assertion exists;
- an assertion with a test expectation has `phase: test`;
- `CLARIFY.REQUEST` matches `on_unmatched_input`.

Report:

```text
reports/test_report.json
```

---

## 7. Generate a Coverage Report

```bash
ordo coverage ../packages/my_first_package
```

The coverage report shows which package components are covered by tests:

- gates;
- assertions;
- nodes;
- gate methods;
- trust classes;
- execution modes;
- FREEFORM blocks.

Report:

```text
reports/coverage_report.json
```

---

## 8. Run the Runtime with `ordo run`

`ordo run` uses a prepared answer file:

```bash
ordo run ../packages/my_first_package --answers ../packages/my_first_package/run_inputs/answers_success.yaml
```

This is not AI execution. It is a minimal helper runner that:

- creates the initial state;
- applies answers to nodes;
- creates state snapshots;
- executes mechanical gates;
- does not substitute `human` or `self_verification` gates;
- blocks output when gates do not pass;
- creates a trace log.

Outputs:

```text
runtime/trace_log.json
runtime/state_snapshots/
reports/run_report.json
```

---

## 9. Complete Guided Intake

Guided intake progresses through nodes in sequence.

Non-interactive mode:

```bash
ordo intake ../packages/my_first_package \
  --answers ../packages/my_first_package/run_inputs/intake_success.yaml \
  --non-interactive
```

Interactive mode:

```bash
ordo intake ../packages/my_first_package
```

The guided intake runner:

- asks questions from `NODE`;
- accepts answers;
- checks `allowed_answers`;
- creates `CLARIFY.REQUEST` for unmatched input;
- updates state;
- executes available gates;
- blocks output when required gates do not pass.

Outputs:

```text
runtime/intake_trace_log.json
reports/intake_report.json
```

---

## 10. Package the Package

```bash
ordo package ../packages/my_first_package
```

The command creates a release archive in `dist/` or the standard output directory, depending on the current CLI implementation.

Before handoff, run the full cycle:

```bash
ordo lint ../packages/my_first_package
ordo compile ../packages/my_first_package
ordo test ../packages/my_first_package
ordo coverage ../packages/my_first_package
ordo run ../packages/my_first_package --answers ../packages/my_first_package/run_inputs/answers_success.yaml
ordo intake ../packages/my_first_package --answers ../packages/my_first_package/run_inputs/intake_success.yaml --non-interactive
ordo package ../packages/my_first_package
```

---

## 11. Common First-Package Mistakes

### A Gate without `method`

Incorrect:

```yaml
gates:
  - id: G_GOAL_PRESENT
    condition: state.package_goal is not null
```

Correct:

```yaml
gates:
  - id: G_GOAL_PRESENT
    method: mechanical
    trust_class: deterministic
    condition: state.package_goal is not null
```

### Missing `on_unmatched_input`

Incorrect:

```yaml
nodes:
  - id: N_GOAL
    question: "What is the goal?"
```

Correct:

```yaml
nodes:
  - id: N_GOAL
    question: "What is the goal?"
    on_unmatched_input:
      action: CLARIFY.REQUEST
      strategy: rephrase_and_narrow
      max_attempts: 2
      on_exhausted:
        action: escalate_to_human
```

### A Human Gate Is Expected as Mechanical

Incorrect:

```yaml
expected:
  gates:
    - id: G_APPROVAL_CONFIRMED
      method: mechanical
```

Correct:

```yaml
expected:
  gates:
    - id: G_APPROVAL_CONFIRMED
      method: human
      trust_class: human_decision
```

### FREEFORM without Maturity

Incorrect:

```yaml
freeform:
  - id: FF_NOTES
    content: "Additional explanation"
```

Correct:

```yaml
freeform:
  - id: FF_NOTES
    role: domain_explanation
    maturity: stable
    incident_count: 0
    incident_threshold: 3
    content: "Additional explanation"
```

---

## 12. What to Do Next

After your first package, try to:

1. add another node;
2. add a mechanical gate for a new state field;
3. add an assertion with `phase: [runtime, test]`;
4. add a test case;
5. run `lint → compile → test → coverage`;
6. check how `compiled/program.ir.json` changes.

This cycle is the basic approach to developing Ordo packages.
