from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

ROUTE_DENY_KEYS = {"id", "incoming_from", "allowed_from"}
UPDATE_STATE_KEYS = {"update_state", "on_pass_update_state", "on_fail_update_state"}
RESOURCE_PATH_RE = re.compile(r"(?<![A-Za-z0-9_.-])([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+\.(?:yaml|yml|json|md|py))(?![A-Za-z0-9_.-])")


def canonical_state_path(value: str) -> str:
    text = str(value or "").strip()
    for prefix in ("$state.", "state."):
        if text.startswith(prefix):
            return text[len(prefix):]
    return text[1:] if text.startswith("$") else text


def walk(value: Any, path: tuple[str, ...] = ()):
    if isinstance(value, dict):
        for key, child in value.items():
            here = path + (str(key),)
            yield here, key, child
            yield from walk(child, here)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            here = path + (f"[{index}]",)
            yield here, None, child
            yield from walk(child, here)


def iter_update_state_maps(value: Any, path: tuple[str, ...] = ()):
    if isinstance(value, dict):
        for key, child in value.items():
            here = path + (str(key),)
            if key in UPDATE_STATE_KEYS and isinstance(child, dict):
                yield here, child
            yield from iter_update_state_maps(child, here)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_update_state_maps(child, path + (f"[{index}]",))


def declared_writes(element: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Return every declared state write with source provenance.

    This is intentionally recursive so branch-specific on_answer.<value>.update_state
    and on_answer.branch.<value>.update_state cannot disappear in one consumer but not another.
    """
    result: dict[str, list[dict[str, Any]]] = {}

    def add(path: str, source: str, value: Any = None) -> None:
        clean = canonical_state_path(path)
        if not clean:
            return
        result.setdefault(clean, []).append({"source": source, "value": copy.deepcopy(value)})

    raw = element.get("writes")
    if isinstance(raw, str):
        add(raw, "writes")
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, str):
                add(item, "writes")
    elif isinstance(raw, dict):
        for path, value in raw.items():
            add(str(path), "writes", value)

    for source_path, mapping in iter_update_state_maps(element):
        source = ".".join(source_path)
        for path, value in mapping.items():
            add(str(path), source, value)

    for path, key, child in walk(element):
        if key in {"target_state", "state_path"} and isinstance(child, str):
            add(child, ".".join(path), child)

    return result


def route_kind(source_path: tuple[str, ...]) -> str:
    joined = ".".join(source_path)
    if "declared_dynamic_routes" in joined:
        return "dynamic"
    if "navigation_contract" in joined:
        return "navigation"
    if "artifact" in joined or "missing_artifact_behavior" in joined:
        return "exception"
    return "canonical"


def routes(element: dict[str, Any], known_targets: set[str]) -> list[dict[str, str]]:
    """Return only formally declared executable routes.

    Arbitrary strings in payload/resource/tool fields are data, not control-flow.
    Route authority comes from the canonical route-bearing structures handled by
    ``declared_routes``; matching a known node id inside e.g. ``args`` must never
    manufacture an execution edge.
    """
    is_gate = bool(
        any(key in element for key in ("on_pass", "on_fail", "pass_to", "fail_to"))
        or str(element.get("method") or "").strip()
        or str(element.get("trust_class") or "").strip()
    )
    return [
        copy.deepcopy(route)
        for route in declared_routes(element, is_gate=is_gate)
        if route.get("target") in known_targets
    ]


def _contains_ai_operation(value: Any) -> bool:
    if isinstance(value, str):
        return bool(re.search(r"(?:^|[^A-Za-z0-9_])AI\.[A-Z0-9_]+", value))
    if isinstance(value, dict):
        return any(_contains_ai_operation(v) for v in value.values())
    if isinstance(value, list):
        return any(_contains_ai_operation(v) for v in value)
    return False



def _assistant_response_synthesis_element(element: dict[str, Any]) -> bool:
    if not isinstance(element, dict):
        return False
    question = str(element.get("question") or "").strip()
    if not question or question.endswith("?"):
        return False
    answer_type = str(element.get("answer_type") or "").strip().lower()
    if answer_type not in {"structured_record", "structured", "json", "object", "text"}:
        return False
    on_answer = element.get("on_answer")
    if not isinstance(on_answer, dict) or not (on_answer.get("next") or on_answer.get("update_state")):
        return False
    if isinstance(element.get("allowed_values"), list) and element.get("allowed_values"):
        return False
    node_context = element.get("node_context") if isinstance(element.get("node_context"), dict) else {}
    refs = node_context.get("knowledge_refs") if isinstance(node_context.get("knowledge_refs"), list) else []
    if not refs:
        return False
    normalized = " ".join(question.lower().split())
    patterns = (
        r"\b(?:summari[sz]e|present|report|explain|respond|reply|give|provide)\b.*\b(?:analyst|user)\b",
        r"\b(?:дай|надай|покажи|поясни|сформуй|повідом)\b.*\b(?:аналітик\w*|користувач\w*)\b",
        r"\b(?:дай|предоставь|покажи|объясни|сформируй|сообщи)\b.*\b(?:аналитик\w*|пользовател\w*)\b",
    )
    return any(re.search(pattern, normalized, re.IGNORECASE) for pattern in patterns)


def classify(element: dict[str, Any], is_gate: bool) -> dict[str, Any]:
    """Orthogonal execution traits with phase-aware model execution.

    A single element may be human/deterministic on enter and model-executed on
    respond.  This is common for analyst questions whose interpretation_policy
    or on_answer.normalize contains AI.* transforms.
    """
    issues: list[str] = []
    action = str(element.get("action") or "")
    upper_action = action.upper()
    lower_type = str(element.get("type") or "").lower()
    # Presentation fields alone do not own execution.  Explicit model execution
    # remains model-owned unless the source also declares an answer-handling
    # contract for an analyst response.
    presentation_interaction = element.get("answer_type") is not None or element.get("question") is not None
    on_answer_declared = isinstance(element.get("on_answer"), dict)
    explicit_model_execution = bool(
        upper_action.startswith("AI.")
        or lower_type == "automatic"
        or any(key in element for key in ("generate", "proposal_generation", "draft_generation", "ai", "model"))
    )
    requires_analyst = bool(presentation_interaction and (not explicit_model_execution or on_answer_declared))
    assistant_response_synthesis = _assistant_response_synthesis_element(element)
    if assistant_response_synthesis:
        requires_analyst = False
    renders_artifact = upper_action.startswith(("DOCUMENT.", "ARTIFACT.")) or all(k in element for k in ("template", "bindings", "output"))

    phases: set[str] = set()
    if upper_action.startswith("AI.") or lower_type == "automatic" or any(key in element for key in ("generate", "proposal_generation", "draft_generation", "ai", "model")):
        phases.add("enter")
    on_answer = element.get("on_answer") if isinstance(element.get("on_answer"), dict) else {}
    normalize_spec = on_answer.get("normalize")
    if _contains_ai_operation(element.get("interpretation_policy")) or _contains_ai_operation(normalize_spec):
        phases.add("respond")

    answer_type = str(element.get("answer_type") or "").lower()
    semantic_answer_types = {
        "structured", "structured_dialog", "dynamic_route_selection",
        "table_confirmation_or_correction", "enum_with_revision_details",
    }
    # If enter is model-generated and an analyst then responds, the respond phase
    # must remain model-executed so confirmations/corrections are interpreted
    # against the proposal instead of falling into a non-semantic direct path.
    if requires_analyst and "enter" in phases:
        phases.add("respond")
    if requires_analyst and answer_type in semantic_answer_types:
        phases.add("respond")

    # A normalize rule that references named $answer.<field> values requires
    # semantic decomposition of free analyst text even when it contains no AI.*
    # opcode literal.
    if isinstance(normalize_spec, (dict, list, str)) and re.search(r"\$answer\.[A-Za-z_][A-Za-z0-9_.]*", json.dumps(normalize_spec, ensure_ascii=False, default=str)):
        phases.add("respond")

    # Some automatic nodes use AI.* only in nested rules rather than the action field.
    if _contains_ai_operation(element) and not requires_analyst:
        phases.add("enter")
    if assistant_response_synthesis:
        phases.add("enter")

    deterministic = False
    runtime_executor = None

    node_context = element.get("node_context") if isinstance(element.get("node_context"), dict) else {}
    allowed_tools = node_context.get("allowed_tools") if isinstance(node_context.get("allowed_tools"), list) else []
    package_tool_paths = [str(x).strip() for x in allowed_tools if isinstance(x, str) and str(x).strip()]
    package_tool_declared = bool(
        package_tool_paths
        and answer_type in {"structured_record", "structured", "json", "object"}
        and isinstance(element.get("on_answer"), dict)
        and any(str(path).lower().endswith((".py", ".js", ".sh")) for path in package_tool_paths)
    )

    if is_gate:
        trust = str(element.get("trust_class") or "").lower()
        method = str(element.get("method") or "").lower()
        if trust == "human_decision" or method == "human":
            kind = "human_gate"; requires_analyst = True; phases.clear(); runtime_executor = "human_gate"
        elif trust == "deterministic" or method in {"mechanical", "deterministic", "python"}:
            kind = "deterministic_gate"; phases.clear(); deterministic = True; runtime_executor = "deterministic_gate"
        else:
            kind = "model_gate"; phases.update({"enter"}); runtime_executor = "semantic_model"
    elif element.get("terminal") is True or lower_type == "terminal":
        kind = "terminal"; phases.clear(); deterministic = True; runtime_executor = "terminal"
    elif package_tool_declared:
        # A structured result produced by an explicitly allowed package-local tool
        # is machine evidence, not an analyst answer. The question field may be
        # explanatory prose describing the deterministic invocation.
        kind = "deterministic_operation"; requires_analyst = False; phases.clear(); deterministic = True; runtime_executor = "package_tool"
    elif requires_analyst:
        kind = "interactive_node"; runtime_executor = "human_interaction"
        # A presentation action describes what happens before asking; it does not
        # make the analyst decision deterministic.
        deterministic = False
    elif upper_action == "DOCUMENT.GENERATE" or all(k in element for k in ("template", "bindings", "output")):
        kind = "document_generate"; phases.clear(); deterministic = True; runtime_executor = "document_generate"
    elif phases:
        kind = "model_node"; runtime_executor = "semantic_model"
    elif upper_action.startswith("ARTIFACT.PRESENT"):
        kind = "deterministic_operation"; deterministic = True; runtime_executor = "artifact_presenter"
    elif upper_action.startswith(("PACKAGE.", "EVIDENCE.", "DOCUMENT.FINALIZE", "IMPLEMENTATION.")):
        # These operations are explicitly delegated to the semantic model until a
        # dedicated deterministic executor exists. This is not a YAML fallback.
        kind = "model_node"; phases.add("enter"); runtime_executor = "semantic_model"
    elif action:
        # A pure declared update can be executed mechanically from patch_template.
        if any(True for _ in iter_update_state_maps(element)):
            kind = "deterministic_operation"; deterministic = True; runtime_executor = "state_patch_template"
        else:
            kind = "unknown_node"; issues.append("action has no registered runtime executor")
    else:
        kind = "unknown_node"; issues.append("no execution classification evidence")

    return {
        "kind": kind,
        "requires_analyst": bool(requires_analyst),
        "model_executed": bool(phases),
        "model_executed_phases": sorted(phases),
        "runtime_executor": runtime_executor,
        "renders_artifact": bool(renders_artifact),
        "deterministic": bool(deterministic),
        "issues": issues,
    }


def resource_refs(value: Any, package_root: Path) -> list[str]:
    refs: set[str] = set()
    root = package_root.resolve()
    for path, key, child in walk(value):
        if not isinstance(child, str):
            continue
        candidates: list[str] = []
        if key in {"validator", "specification", "template", "schema", "resource", "path", "bindings", "reference"}:
            candidates.append(child)
        candidates.extend(m.group(1) for m in RESOURCE_PATH_RE.finditer(child))
        if "/" in child and len(child) < 240 and not child.startswith(("http://", "https://")):
            candidates.append(child)
        for candidate in candidates:
            clean = candidate.strip().split("#", 1)[0]
            resolved = (package_root / clean).resolve()
            try:
                resolved.relative_to(root)
            except Exception:
                continue
            if resolved.is_file():
                refs.add(clean)
    return sorted(refs)


def declared_routes(element: dict[str, Any], is_gate: bool = False) -> list[dict[str, str]]:
    """Canonical route interpretation shared by compiler and editor.

    Unlike the independent verifier's generic target scan, this function preserves
    analyst-facing route keys (next/on_pass/branch values) used by runtime dispatch.
    """
    out: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    def add(key: Any, target: Any, kind: str = "canonical", source_path: str | None = None) -> None:
        if not isinstance(target, str) or not target or target.startswith("$"):
            return
        item = (str(key), target, source_path or str(key))
        if item in seen:
            return
        seen.add(item)
        out.append({"key": str(key), "target": target, "kind": kind, "source_path": source_path or str(key)})

    def add_nested(value: Any, prefix: str = "", source_prefix: str = "") -> None:
        if not isinstance(value, dict):
            return
        direct = value.get("next") or value.get("to")
        if isinstance(direct, str):
            add(prefix or "next", direct, "dynamic" if "declared_dynamic_routes" in source_prefix else "canonical", f"{source_prefix}.next".strip("."))
        for key, child in value.items():
            if key in {"next", "to", "update_state", "analysis", "action", "strategy", "on_exhausted"}:
                continue
            child_source = f"{source_prefix}.{key}".strip(".")
            if isinstance(child, dict):
                child_prefix = str(key) if not prefix or prefix in {"branch", "routes"} else f"{prefix}.{key}"
                add_nested(child, child_prefix, child_source)
            elif isinstance(child, str) and key != "reason":
                add(str(key), child, "dynamic" if "declared_dynamic_routes" in source_prefix else "canonical", child_source)

    if isinstance(element.get("next"), str):
        add("next", element.get("next"), source_path="next")
    if is_gate:
        if isinstance(element.get("on_pass"), str): add("on_pass", element.get("on_pass"), source_path="on_pass")
        if isinstance(element.get("pass_to"), str): add("on_pass", element.get("pass_to"), source_path="pass_to")
        if isinstance(element.get("on_fail"), str): add("on_fail", element.get("on_fail"), source_path="on_fail")
        if isinstance(element.get("fail_to"), str): add("on_fail", element.get("fail_to"), source_path="fail_to")

    on_answer = element.get("on_answer")
    if isinstance(on_answer, dict):
        if isinstance(on_answer.get("next"), str):
            add("next", on_answer.get("next"), source_path="on_answer.next")
        non_route = {"normalize", "update_state", "state_updates", "analysis", "transform", "interpret", "interpretation", "bindings", "outputs", "result", "results"}
        for key, value in on_answer.items():
            if key == "next" or key in non_route:
                continue
            if isinstance(value, str):
                add(key, value, source_path=f"on_answer.{key}")
            elif isinstance(value, dict):
                direct = value.get("next") or value.get("to")
                if isinstance(direct, str):
                    add(key, direct, source_path=f"on_answer.{key}.next")
                elif key in {"branch", "branches", "routes", "route", "transitions"}:
                    add_nested(value, str(key), f"on_answer.{key}")

    transitions = element.get("transitions")
    if isinstance(transitions, dict):
        for key, value in transitions.items():
            if isinstance(value, str):
                add(key, value, source_path=f"transitions.{key}")
            elif isinstance(value, dict):
                add(key, value.get("to") or value.get("next"), source_path=f"transitions.{key}.to")
    elif isinstance(transitions, list):
        for index, value in enumerate(transitions):
            if isinstance(value, dict):
                key = value.get("id") or value.get("outcome") or value.get("when") or f"transition_{index+1}"
                add(key, value.get("to") or value.get("next"), source_path=f"transitions.[{index}].to")

    nav = element.get("navigation_contract")
    if isinstance(nav, dict) and isinstance(nav.get("allowed_to"), list):
        for index, target in enumerate(nav["allowed_to"]):
            add(target, target, "navigation", f"navigation_contract.allowed_to.[{index}]")

    declared = element.get("declared_dynamic_routes")
    if isinstance(declared, dict):
        for key, value in declared.items():
            if isinstance(value, str):
                add(key, value, "dynamic", f"declared_dynamic_routes.{key}")
            else:
                add_nested(value, str(key), f"declared_dynamic_routes.{key}")

    artifact = element.get("artifact")
    if isinstance(artifact, dict):
        missing = artifact.get("missing_artifact_behavior")
        if isinstance(missing, str):
            add("missing_artifact", missing, "exception", "artifact.missing_artifact_behavior")
        elif isinstance(missing, dict):
            add_nested(missing, "missing_artifact", "artifact.missing_artifact_behavior")
    return out
