from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import yaml


UTILITY_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = UTILITY_ROOT.parents[1]
CLI_ROOT = REPOSITORY_ROOT / "cli"
if not CLI_ROOT.is_dir():
    CLI_ROOT = REPOSITORY_ROOT / "cli_embedded" / "ordo_pkg"
if str(CLI_ROOT) not in sys.path:
    sys.path.insert(0, str(CLI_ROOT))

from ordo.graph_validation import validate_process_graph  # noqa: E402
from ordo.linter import lint_source  # noqa: E402


NODE_TEMPLATES = {
    "question": {
        "id": "N_NEW_QUESTION",
        "question": "Describe the decision this node must collect.",
        "answer_type": "free_text",
        "allow_unmatched_input": True,
        "on_answer": {"continue": {"next": "N_NEXT"}},
        "allowed_from": [],
    },
    "gate": {
        "id": "N_NEW_GATE",
        "question": "Run or review the required gate.",
        "answer_type": "enum",
        "allow_unmatched_input": True,
        "allowed_answers": ["pass", "revise"],
        "on_answer": {
            "pass": {"next": "N_NEXT"},
            "revise": {"next": "N_REPAIR"},
        },
        "allowed_from": [],
    },
    "materialization": {
        "id": "N_NEW_MATERIALIZATION",
        "question": "Materialize the reviewed output artifact.",
        "answer_type": "confirmation",
        "allow_unmatched_input": True,
        "on_answer": {"confirmed": {"next": "N_NEXT"}},
        "allowed_from": [],
    },
    "terminal": {
        "id": "N_NEW_TERMINAL",
        "question": "Confirm the terminal outcome.",
        "answer_type": "confirmation",
        "allow_unmatched_input": True,
        "terminal": True,
        "allowed_from": [],
    },
}


def parse_yaml(text: str) -> dict[str, Any]:
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("The YAML root must be a mapping.")
    return data


def dump_yaml(source: dict[str, Any]) -> str:
    return yaml.safe_dump(source, allow_unicode=True, sort_keys=False)


def dump_value_yaml(value: Any) -> str:
    rendered = yaml.safe_dump(value, allow_unicode=True, sort_keys=False)
    if rendered.endswith("\n...\n"):
        rendered = rendered[:-5]
    return rendered.strip()


def node_sections(node: dict[str, Any]) -> list[dict[str, str]]:
    return [{"key": str(key), "value_yaml": dump_value_yaml(value)} for key, value in node.items()]


def replace_node(source: dict[str, Any], old_id: str, replacement: dict[str, Any]) -> dict[str, Any]:
    """Replace one node while preserving the rest of the loaded playbook."""
    new_id = replacement.get("id")
    if not isinstance(new_id, str) or not new_id.strip():
        raise ValueError("The replacement node must declare a non-empty id.")
    nodes = source.get("nodes")
    if not isinstance(nodes, list):
        raise ValueError("The loaded source does not contain a nodes list.")
    matches = [index for index, node in enumerate(nodes) if isinstance(node, dict) and node.get("id") == old_id]
    if len(matches) != 1:
        raise ValueError(f"Cannot identify exactly one node with id {old_id!r}.")
    if new_id != old_id and any(isinstance(node, dict) and node.get("id") == new_id for node in nodes):
        raise ValueError(f"A node with id {new_id!r} already exists.")
    nodes[matches[0]] = replacement
    if new_id != old_id:
        def replace_next_targets(value: Any) -> Any:
            if isinstance(value, dict):
                return {key: (new_id if key == "next" and child == old_id else replace_next_targets(child)) for key, child in value.items()}
            if isinstance(value, list):
                return [replace_next_targets(child) for child in value]
            return value

        for node in nodes:
            if not isinstance(node, dict):
                continue
            if isinstance(node.get("allowed_from"), list):
                node["allowed_from"] = [new_id if value == old_id else value for value in node["allowed_from"]]
            if isinstance(node.get("transitions"), dict):
                node["transitions"] = {key: new_id if value == old_id else value for key, value in node["transitions"].items()}
            if "on_answer" in node:
                node["on_answer"] = replace_next_targets(node["on_answer"])
        for container_key in ("graph_contract", "playbook"):
            container = source.get(container_key)
            if isinstance(container, dict) and container.get("entry_node") == old_id:
                container["entry_node"] = new_id
    return source


def replace_node_sections(source: dict[str, Any], old_id: str, sections: dict[str, str]) -> dict[str, Any]:
    replacement: dict[str, Any] = {}
    for key, value_yaml in sections.items():
        if not isinstance(key, str) or not key.strip() or not isinstance(value_yaml, str):
            raise ValueError("Each node section must have a non-empty key and YAML value.")
        replacement[key] = yaml.safe_load(value_yaml)
    return replace_node(source, old_id, replacement)


def _targets(value: Any) -> list[str]:
    targets: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "next" and isinstance(item, str):
                targets.append(item)
            else:
                targets.extend(_targets(item))
    elif isinstance(value, list):
        for item in value:
            targets.extend(_targets(item))
    return targets


def _node_targets(node: dict[str, Any]) -> list[str]:
    """Return graph targets from the canonical and ARF prototype forms."""
    targets = _targets(node.get("on_answer", {}))
    transitions = node.get("transitions", {})
    if isinstance(transitions, dict):
        targets.extend(
            target
            for target in transitions.values()
            if isinstance(target, str) and not target.startswith("$")
        )
    return targets


def _node_edges(node: dict[str, Any]) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    transitions = node.get("transitions", {})
    if isinstance(transitions, dict):
        edges.extend(
            {"target": target, "storage": "transitions", "key": str(key)}
            for key, target in transitions.items()
            if isinstance(target, str) and not target.startswith("$")
        )
    for target in _targets(node.get("on_answer", {})):
        edges.append({"target": target, "storage": "on_answer", "key": "nested next"})
    return edges


def graph_view(source: dict[str, Any]) -> dict[str, Any]:
    nodes = [node for node in source.get("nodes", []) if isinstance(node, dict) and node.get("id")]
    return {
        "nodes": [
            {
                "id": str(node["id"]),
                "label": str(node.get("question") or node.get("purpose") or node["id"]),
                "answer_type": node.get("answer_type") or node.get("kind", "unspecified"),
                "terminal": node.get("terminal") is True,
                "allowed_from": node.get("allowed_from", []),
                "record_yaml": dump_yaml(node),
                "sections": node_sections(node),
            }
            for node in nodes
        ],
        "edges": [
            {"source": str(node["id"]), **edge}
            for node in nodes
            for edge in _node_edges(node)
        ],
    }


def validate_source(source: dict[str, Any]) -> dict[str, Any]:
    graph = validate_process_graph(source)
    lint = lint_source(source, {"test_cases": []}, repo_root=str(REPOSITORY_ROOT))
    issues = [
        {"validator": "graph", **issue}
        for issue in graph.get("issues", [])
    ] + [
        {"validator": "lint", **issue}
        for issue in lint.get("issues", [])
    ]
    return {
        "status": "passed" if not any(issue.get("severity") == "error" for issue in issues) else "failed",
        "graph": graph,
        "lint": lint,
        "issues": issues,
    }


def tree_module_manifest_path() -> Path:
    candidates = (
        REPOSITORY_ROOT / "packages" / "ordo_applied_project_factory" / "source" / "tree_module_library" / "manifest.yaml",
        REPOSITORY_ROOT / "source" / "tree_module_library" / "manifest.yaml",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("Cannot find an ARF tree-module library manifest.")


def _json_response(handler: SimpleHTTPRequestHandler, payload: dict[str, Any], status: int = HTTPStatus.OK) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class EditorHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(UTILITY_ROOT / "web"), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def end_headers(self) -> None:
        """Keep local editor assets fresh while an extracted package is iterated."""
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()

    def do_POST(self) -> None:  # noqa: N802
        if self.path not in {"/api/parse", "/api/validate", "/api/export", "/api/update-node", "/api/update-node-sections"}:
            _json_response(self, {"status": "failed", "error": "Unknown API endpoint."}, HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            source = parse_yaml(payload["yaml"]) if "yaml" in payload else payload["source"]
            if not isinstance(source, dict):
                raise ValueError("source must be a mapping.")
            if self.path == "/api/export":
                _json_response(self, {"status": "passed", "yaml": dump_yaml(source)})
            elif self.path == "/api/update-node":
                replacement = parse_yaml(payload["node_yaml"])
                replace_node(source, str(payload["old_id"]), replacement)
                _json_response(self, {"status": "passed", "node_id": replacement["id"], "source": source, "graph": graph_view(source)})
            elif self.path == "/api/update-node-sections":
                replace_node_sections(source, str(payload["old_id"]), payload["sections"])
                _json_response(self, {"status": "passed", "node_id": yaml.safe_load(payload["sections"]["id"]), "source": source, "graph": graph_view(source)})
            else:
                response = {"status": "passed", "source": source, "graph": graph_view(source)}
                if self.path == "/api/validate":
                    response["validation"] = validate_source(source)
                _json_response(self, response)
        except (KeyError, TypeError, ValueError, yaml.YAMLError) as error:
            _json_response(self, {"status": "failed", "error": str(error)}, HTTPStatus.BAD_REQUEST)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/node-templates":
            _json_response(self, {"status": "passed", "templates": NODE_TEMPLATES})
            return
        if self.path == "/api/tree-modules":
            manifest = tree_module_manifest_path()
            _json_response(self, {"status": "passed", "library": yaml.safe_load(manifest.read_text(encoding="utf-8"))})
            return
        super().do_GET()


def run_server(port: int, open_browser: bool) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", port), EditorHandler)
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"Ordo Tree Editor is running at {url}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nOrdo Tree Editor stopped.")
    finally:
        server.server_close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local Ordo Tree Editor.")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)
    run_server(args.port, open_browser=not args.no_browser)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
