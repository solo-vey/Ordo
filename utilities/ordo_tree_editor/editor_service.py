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


def _records(source: dict[str, Any], collection: str) -> list[dict[str, Any]]:
    records = source.get(collection)
    if not isinstance(records, list):
        raise ValueError(f"The loaded source does not contain a {collection} list.")
    return [record for record in records if isinstance(record, dict)]


def _replace_target_references(value: Any, old_id: str, new_id: str) -> Any:
    if isinstance(value, dict):
        if set(value) and all(isinstance(child, str) for child in value.values()):
            return {key: new_id if child == old_id else child for key, child in value.items()}
        return {
            key: new_id if key in {"next", "to", "on_pass", "on_fail", "pass_to", "fail_to"} and child == old_id else _replace_target_references(child, old_id, new_id)
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [_replace_target_references(child, old_id, new_id) for child in value]
    return value


def replace_record(source: dict[str, Any], collection: str, old_id: str, replacement: dict[str, Any]) -> dict[str, Any]:
    """Replace a node or executable gate while preserving the rest of the source."""
    if collection not in {"nodes", "gates"}:
        raise ValueError("Only nodes and gates can be edited as records.")
    new_id = replacement.get("id")
    if not isinstance(new_id, str) or not new_id.strip():
        raise ValueError("The replacement record must declare a non-empty id.")
    records = source.get(collection)
    if not isinstance(records, list):
        raise ValueError(f"The loaded source does not contain a {collection} list.")
    matches = [index for index, record in enumerate(records) if isinstance(record, dict) and record.get("id") == old_id]
    if len(matches) != 1:
        raise ValueError(f"Cannot identify exactly one {collection[:-1]} with id {old_id!r}.")
    all_records = [
        record
        for records_key in ("nodes", "gates")
        for record in source.get(records_key, [])
        if isinstance(record, dict)
    ]
    if new_id != old_id and any(record.get("id") == new_id for record in all_records):
        raise ValueError(f"A node or gate with id {new_id!r} already exists.")
    records[matches[0]] = replacement
    if new_id != old_id:
        for record in all_records:
            for contract_key in ("allowed_from", "allowed_to"):
                if isinstance(record.get(contract_key), list):
                    record[contract_key] = [new_id if value == old_id else value for value in record[contract_key]]
            navigation = record.get("navigation_contract")
            if isinstance(navigation, dict):
                for contract_key in ("allowed_from", "allowed_to"):
                    if isinstance(navigation.get(contract_key), list):
                        navigation[contract_key] = [new_id if value == old_id else value for value in navigation[contract_key]]
            for key, value in list(record.items()):
                record[key] = _replace_target_references(value, old_id, new_id)
        for container_key in ("graph_contract", "playbook"):
            container = source.get(container_key)
            if isinstance(container, dict) and container.get("entry_node") == old_id:
                container["entry_node"] = new_id
    return source


def replace_node(source: dict[str, Any], old_id: str, replacement: dict[str, Any]) -> dict[str, Any]:
    return replace_record(source, "nodes", old_id, replacement)


def replace_record_sections(source: dict[str, Any], collection: str, old_id: str, sections: dict[str, str]) -> dict[str, Any]:
    replacement: dict[str, Any] = {}
    for key, value_yaml in sections.items():
        if not isinstance(key, str) or not key.strip() or not isinstance(value_yaml, str):
            raise ValueError("Each record section must have a non-empty key and YAML value.")
        replacement[key] = yaml.safe_load(value_yaml)
    return replace_record(source, collection, old_id, replacement)


def replace_node_sections(source: dict[str, Any], old_id: str, sections: dict[str, str]) -> dict[str, Any]:
    return replace_record_sections(source, "nodes", old_id, sections)


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
    elif isinstance(transitions, list):
        targets.extend(
            item["to"] for item in transitions
            if isinstance(item, dict) and isinstance(item.get("to"), str) and not item["to"].startswith("$")
        )
    navigation = node.get("navigation_contract", {})
    if isinstance(navigation, dict) and isinstance(navigation.get("allowed_to"), list):
        targets.extend(target for target in navigation["allowed_to"] if isinstance(target, str) and not target.startswith("$"))
    return targets


def _node_edges(node: dict[str, Any]) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    explicit_targets: set[str] = set()
    if isinstance(node.get("next"), str) and not node["next"].startswith("$"):
        edges.append({"target": node["next"], "storage": "next", "key": "next"})
    transitions = node.get("transitions", {})
    if isinstance(transitions, dict):
        edges.extend(
            {"target": target, "storage": "transitions", "key": str(key)}
            for key, target in transitions.items()
            if isinstance(target, str) and not target.startswith("$")
        )
        explicit_targets.update(edge["target"] for edge in edges)
    elif isinstance(transitions, list):
        explicit_targets = set()
        for index, transition in enumerate(transitions):
            if not isinstance(transition, dict) or not isinstance(transition.get("to"), str):
                continue
            target = transition["to"]
            if target.startswith("$"):
                continue
            explicit_targets.add(target)
            label = transition.get("id") or transition.get("when") or transition.get("outcome") or f"transition_{index + 1}"
            edges.append({"target": target, "storage": "transitions_list", "key": str(label), "index": str(index)})
    navigation = node.get("navigation_contract", {})
    if isinstance(navigation, dict) and isinstance(navigation.get("allowed_to"), list):
        for target in navigation["allowed_to"]:
            if isinstance(target, str) and not target.startswith("$") and target not in explicit_targets:
                edges.append({"target": target, "storage": "navigation_allowed_to", "key": target})
    on_answer = node.get("on_answer", {})
    if isinstance(on_answer, dict):
        if isinstance(on_answer.get("next"), str) and not on_answer["next"].startswith("$"):
            edges.append({"target": on_answer["next"], "storage": "on_answer_next", "key": "next"})
        for outcome, route in on_answer.items():
            if outcome == "next":
                continue
            targets = _targets(route)
            edges.extend({"target": target, "storage": "on_answer", "key": str(outcome)} for target in targets)
    return edges


def _route_targets(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    return _targets(value)


def _gate_edges(gate: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"target": target, "storage": "gate_route", "key": key}
        for key in ("on_pass", "on_fail", "pass_to", "fail_to")
        for target in _route_targets(gate.get(key))
    ]


def _terminal_records(source: dict[str, Any]) -> list[dict[str, Any]]:
    records = source.get("terminals", [])
    if not isinstance(records, list):
        return []
    result = []
    for item in records:
        if isinstance(item, str) and item.strip():
            result.append({"id": item})
        elif isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"].strip():
            result.append(item)
    return result


def _external_terminal_ids(source: dict[str, Any], edges: list[dict[str, str]], known_ids: set[str]) -> list[str]:
    declared: list[str] = []
    contract = source.get("graph_contract", {})
    if isinstance(contract, dict):
        declared.extend(value for value in contract.get("external_terminal_targets", []) if isinstance(value, str))
    declared.extend(item["id"] for item in source.get("outputs", []) if isinstance(item, dict) and isinstance(item.get("id"), str))
    routed = [edge["target"] for edge in edges if edge["target"] not in known_ids and not edge["target"].startswith("$")]
    return list(dict.fromkeys(identifier for identifier in [*declared, *routed] if identifier not in known_ids))


def graph_view(source: dict[str, Any]) -> dict[str, Any]:
    nodes = [node for node in source.get("nodes", []) if isinstance(node, dict) and node.get("id")]
    gates = [gate for gate in source.get("gates", []) if isinstance(gate, dict) and gate.get("id")]
    edges = [
        {"source": str(node["id"]), **edge}
        for node in nodes
        for edge in _node_edges(node)
    ] + [
        {"source": str(gate["id"]), **edge}
        for gate in gates
        for edge in _gate_edges(gate)
    ]
    terminal_records = _terminal_records(source)
    known_ids = {str(record["id"]) for record in [*nodes, *gates, *terminal_records]}
    terminals = _external_terminal_ids(source, edges, known_ids)
    return {
        "nodes": [
            {
                "id": str(node["id"]),
                "element_type": "node",
                "collection": "nodes",
                "label": str(node.get("question") or node.get("purpose") or node["id"]),
                "answer_type": node.get("answer_type") or node.get("kind", "unspecified"),
                "terminal": node.get("terminal") is True,
                "allowed_from": node.get("allowed_from", []),
                "record_yaml": dump_yaml(node),
                "sections": node_sections(node),
            }
            for node in nodes
        ] + [
            {
                "id": str(terminal["id"]),
                "element_type": "terminal",
                "collection": None,
                "label": str(terminal.get("title") or terminal.get("purpose") or terminal["id"]),
                "answer_type": "terminal",
                "terminal": True,
                "allowed_from": terminal.get("allowed_from", []),
                "record_yaml": dump_yaml(terminal),
                "sections": [],
            }
            for terminal in terminal_records
        ] + [
            {
                "id": str(gate["id"]),
                "element_type": "gate",
                "collection": "gates",
                "label": str(gate.get("condition") or gate.get("purpose") or gate["id"]),
                "answer_type": str(gate.get("method") or "gate"),
                "terminal": False,
                "allowed_from": [],
                "record_yaml": dump_yaml(gate),
                "sections": node_sections(gate),
            }
            for gate in gates
        ] + [
            {
                "id": terminal_id,
                "element_type": "terminal",
                "collection": None,
                "label": terminal_id,
                "answer_type": "external terminal",
                "terminal": True,
                "allowed_from": [],
                "record_yaml": "",
                "sections": [],
            }
            for terminal_id in terminals
        ],
        "edges": edges,
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
                collection = str(payload.get("collection", "nodes"))
                replace_record(source, collection, str(payload["old_id"]), replacement)
                _json_response(self, {"status": "passed", "node_id": replacement["id"], "source": source, "graph": graph_view(source)})
            elif self.path == "/api/update-node-sections":
                collection = str(payload.get("collection", "nodes"))
                replace_record_sections(source, collection, str(payload["old_id"]), payload["sections"])
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
