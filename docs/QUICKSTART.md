# Ordo Quickstart

Create your first Ordo playbook in a language-model chat. You do not need Python, a terminal, or prior knowledge of Ordo.

## 1. Download the ARF Playbook Kit

Download [ARF Playbook Kit 0.2.1](https://github.com/solo-vey/Ordo/releases/download/arf-playbook-kit-v0.2.1/ORDO_ARF_PLAYBOOK_KIT_0.2.1.zip). Keep the archive intact.

The Kit contains ARF Playbook Laws, a ready prompt, a template, a small weekly-status process brief, a test-and-improvement prompt, and expected deliverables. You do not need to clone the repository, install Python, or build anything.

## 2. Upload the Kit to a language-model chat

Open a new chat that accepts file uploads and attach the ZIP. Ask the model to read every file before beginning.

If the chat cannot open ZIP files, extract the archive and upload its four Markdown files together.

## 3. Paste the Kit start prompt

Open `START_PROMPT.md` from the uploaded Kit, copy its contents, and send it in the same chat.

The model should act as an AI Ordo Developer, ask only the clarification questions needed for the example, and keep Python or CLI work optional.

## 4. Create and dry-run the first playbook

Answer the model's questions about the weekly-status process. Ask it to produce a first draft, validate every required section, and perform a dry-run with the example notes from `PLAYBOOK_BRIEF.md`.

Do not accept the package if required inputs, gates, outputs, or failure behavior are missing.

## 5. Test, improve, and package

Send the prompt from `TEST_AND_IMPROVE.md` in the Kit. Review the model's test matrix, failures, corrections, and final package inventory.

The completed chat should return the artifacts listed in `EXPECTED_DELIVERABLES.md`, preferably as a ZIP.

## Expected result

The user can complete the full learning loop in one chat:

```text
create → validate → dry-run → improve → package
```

The model must not claim that a conversational dry-run is equivalent to the deterministic CLI or release gate. It should state which checks were conversational and which remain optional mechanical validation.

## Optional: validate with Python and the CLI

Use this path when you need automation, reproducibility, CI, or release-grade mechanical checks. Python 3.10 or newer is required.

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ./cli
python tools/run_golden_examples.py --example package-validation
python tools/run_golden_examples.py --example process-rail-next-step
python tools/run_golden_examples.py --example history-event-output-gate
python tools/run_golden_examples.py --all
```

The manifest at [`../examples/golden_examples.json`](../examples/golden_examples.json) is the source of truth for these CI-backed commands. Continue with the [`documentation map`](README.md) or the [`CLI reference`](../cli/README.md).
