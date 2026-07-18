"""Render a MazeTree into a real Ordo source package (program.ordo.yaml + scaffold).

Every emitted package is a genuine, lintable, compilable Ordo package -
dogfooding the language itself for the benchmark (design decision from the
design discussion: no separate toy simulator).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from .maze_gen import MazeTree, END_SENTINEL

MAX_DEPTH_SLOTS = 7  # matches the design's depth range (5-7); template has this many fixed rows


def _node_to_yaml(tree: MazeTree, node_id: str) -> dict:
    node = tree.nodes[node_id]
    opts_str = ", ".join(node.options)
    question = (
        f"Ви на вузлі {node.id} (крок {node.depth + 1}/{tree.depth}). "
        f"Куди йти? Варіанти: {opts_str}."
    )
    on_answer: dict = {}
    for opt in node.options:
        branch_update = {
            f"path_step_{node.depth}": "$answer",
            f"path_node_step_{node.depth}": node.id,
        }
        target = node.children[opt]
        if target == END_SENTINEL:
            branch_update["path_complete"] = True
            branch_next = "G_PATHWALK_COMPLETE"
        else:
            branch_next = target
        on_answer[opt] = {"update_state": branch_update, "next": branch_next}
    return {
        "id": node.id,
        "question": question,
        "answer_type": "single_select",
        "allowed_answers": list(node.options),
        "on_answer": on_answer,
        "on_unmatched_input": {
            "action": "CLARIFY.REQUEST",
            "strategy": "show_valid_options_for_this_node",
            "max_attempts": 2,
            "on_exhausted": {"action": "escalate_to_human", "reason": "invalid direction repeated at this node"},
        },
        "allow_unmatched_input": False,
    }


def build_source_yaml(tree: MazeTree, package_id: str) -> dict:
    state_schema: dict = {"path_complete": False}
    for i in range(MAX_DEPTH_SLOTS):
        state_schema[f"path_step_{i}"] = None
        state_schema[f"path_node_step_{i}"] = None

    nodes = [_node_to_yaml(tree, nid) for nid in tree.nodes]

    return {
        "ordo": {
            "version": "0.12",
            "package": package_id,
            "control_level": "standard",
            "execution_mode": "chat_internal",
        },
        "intent": {
            "id": "INTENT_PATHWALK_BENCHMARK",
            "description": (
                "Determinism/fidelity benchmark: navigate a generated decision tree from "
                "start to end while recording the actual path taken, under realistic "
                "conversational noise (distractions, backtracks, corrections)."
            ),
        },
        "contract": {
            "id": "CONTRACT_PATHWALK",
            "required": ["path_complete"],
        },
        "graph_contract": {
            "entry_node": tree.start,
            "external_terminal_targets": ["G_PATHWALK_COMPLETE"],
        },
        "state": {"id": "STATE_PATHWALK", "schema": state_schema},
        "nodes": nodes,
        "gates": [
            {
                "id": "G_PATHWALK_COMPLETE",
                "method": "mechanical",
                "trust_class": "deterministic",
                "condition": "state.path_complete is true",
                "on_fail": "block",
            }
        ],
        "assertions": [],
        "outputs": [
            {
                "id": "OUT_PATHWALK_RESULT",
                "type": "document",
                "allowed_after": ["G_PATHWALK_COMPLETE"],
            }
        ],
    }


RESULT_TEMPLATE = """# PathWalk result

| step | node_id | value |
|---|---|---|
| 0 | {{ state.path_node_step_0 }} | {{ state.path_step_0 }} |
| 1 | {{ state.path_node_step_1 }} | {{ state.path_step_1 }} |
| 2 | {{ state.path_node_step_2 }} | {{ state.path_step_2 }} |
| 3 | {{ state.path_node_step_3 }} | {{ state.path_step_3 }} |
| 4 | {{ state.path_node_step_4 }} | {{ state.path_step_4 }} |
| 5 | {{ state.path_node_step_5 }} | {{ state.path_step_5 }} |
| 6 | {{ state.path_node_step_6 }} | {{ state.path_step_6 }} |

path_complete: {{ state.path_complete | bool_lower }}
"""

CATALOG_YAML = """output_templates:
- id: PATHWALK_RESULT
  type: document
  format: markdown
  path: PATHWALK_RESULT.md
  template: templates/pathwalk_result.md
  source: state
  allowed_after:
  - OUT_PATHWALK_RESULT
  render_mode: deterministic
  renderer: ordo.simple
  requires_model_rendering: false
"""

MINIMAL_START_HERE = """# START HERE — Ordo PathWalk Benchmark Package

## 0. IR ACCESS PROTOCOL — HARD RULE (M60.4)

compiled/* is CLI-owned. Do not read it directly in enforced mode. Use only the
embedded runtime CLI (`cli_embedded/ordo`) for runtime information. If the
embedded CLI cannot run, hard-stop instead of silently falling back.

## Protocol

This package is a decision tree. Use:

```bash
./cli_embedded/ordo verify-targets .
./cli_embedded/ordo next-step . --format auto
./cli_embedded/ordo intake . --submit <node_id> --answer-file <file>
./cli_embedded/ordo restore-session . --to-seq <N> --reason "..."
./cli_embedded/ordo verify-session .
```

JSON IR decides. Ordo-code explains. Session-trace proves.
"""


def emit_package(tree: MazeTree, out_dir: Path, package_id: str, *, force: bool = False) -> Path:
    out_dir = Path(out_dir)
    if out_dir.exists():
        if not force:
            raise FileExistsError(f"{out_dir} already exists; pass force=True to overwrite")
        shutil.rmtree(out_dir)
    (out_dir / "source").mkdir(parents=True)
    (out_dir / "compiled").mkdir(parents=True)
    (out_dir / "reports").mkdir(parents=True)
    (out_dir / "runtime" / "state_snapshots").mkdir(parents=True)
    (out_dir / "generated_outputs").mkdir(parents=True)
    (out_dir / "tests").mkdir(parents=True)
    (out_dir / "run_inputs").mkdir(parents=True)
    tmpl_dir = out_dir / "output_templates"
    (tmpl_dir / "templates").mkdir(parents=True)

    manifest = {
        "name": package_id,
        "version": "0.1.0",
        "ordo_version": "0.12",
        "source": "source/program.ordo.yaml",
        "tests": "tests/test_cases.yaml",
        "compiled": "compiled/program.ir.json",
        "reports": "reports",
    }
    (out_dir / "ordo.yml").write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

    source_yaml = build_source_yaml(tree, package_id)
    (out_dir / "source" / "program.ordo.yaml").write_text(
        yaml.safe_dump(source_yaml, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

    (out_dir / "tests" / "test_cases.yaml").write_text(
        yaml.safe_dump({"test_cases": []}, allow_unicode=True), encoding="utf-8"
    )

    (tmpl_dir / "output_templates.yaml").write_text(CATALOG_YAML, encoding="utf-8")
    (tmpl_dir / "templates" / "pathwalk_result.md").write_text(RESULT_TEMPLATE, encoding="utf-8")

    template_start_here = Path(__file__).resolve().parents[2] / "cli" / "ordo" / "templates" / "package_template" / "START_HERE_RUNTIME_MODE.md"
    if template_start_here.exists():
        shutil.copy2(template_start_here, out_dir / "START_HERE_RUNTIME_MODE.md")
    else:
        (out_dir / "START_HERE_RUNTIME_MODE.md").write_text(MINIMAL_START_HERE, encoding="utf-8")

    template_start_prompt = template_start_here.parent / "START_PROMPT_RUNTIME_MODE.md"
    if template_start_prompt.exists():
        shutil.copy2(template_start_prompt, out_dir / "START_PROMPT_RUNTIME_MODE.md")
    else:
        (out_dir / "START_PROMPT_RUNTIME_MODE.md").write_text(
            "Read START_HERE_RUNTIME_MODE.md and follow it strictly for this PathWalk package.\n",
            encoding="utf-8",
        )
    (out_dir / "reports" / "CLI_VALIDATION_SUMMARY.md").write_text(
        "# CLI validation summary\n\n"
        "Generated PathWalk benchmark package.\n\n"
        "CLI status: not_run_cli_unavailable (generated package; run `ordo lint`/`ordo compile` "
        "and, for a live session, the embedded CLI to produce a real status)\n",
        encoding="utf-8",
    )
    (out_dir / "README.md").write_text(
        f"# PathWalk benchmark package `{package_id}`\n\n"
        f"Generated tree, depth={tree.depth}, seed={tree.seed}.\n\n"
        "Read START_HERE_RUNTIME_MODE.md (points to START_PROMPT_RUNTIME_MODE.md) before use.\n"
        "Runtime source: compiled/program.ir.json. Editable source: source/program.ordo.yaml.\n",
        encoding="utf-8",
    )
    (out_dir / "reports" / ".gitkeep").write_text("", encoding="utf-8")

    (out_dir / "tree_meta.json").write_text(
        __import__("json").dumps(tree.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Deterministic green runtime path for release validation of disposable packages.
    answers = {}
    current = tree.start
    visited = set()
    while current in tree.nodes and current not in visited:
        visited.add(current)
        node = tree.nodes[current]
        choice = node.options[0]
        answers[current] = choice
        target = node.children[choice]
        if target == END_SENTINEL:
            break
        current = target
    (out_dir / "run_inputs" / "answers_success.yaml").write_text(
        yaml.safe_dump(answers, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    (out_dir / "run_inputs" / "intake_success.yaml").write_text(
        yaml.safe_dump(answers, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

    return out_dir
