from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

ALLOWED_METHODS = {"mechanical", "self_verification", "self_consistency", "human"}
ALLOWED_TRUST_CLASSES = {"deterministic", "model_judgment", "repeated_model_judgment", "human_decision"}
ALLOWED_EXECUTION_MODES = {"full_runtime", "chat_internal", "freeform_only"}
ALLOWED_CONTROL_LEVELS = {"light", "standard", "strict"}
ALLOWED_ASSERTION_POLARITIES = {"must", "not"}
ALLOWED_ASSERTION_PHASES = {"runtime", "test", "debug"}
ALLOWED_FREEFORM_MATURITY = {"stable", "volatile", "candidate_for_formalization"}
ALLOWED_CSG_MODES = {"advisory", "guided_redirect", "strict_redirect", "locked_process"}
ALLOWED_CSG_COUNTER_SCOPES = {"active_node", "deviation_session", "process_run"}
ALLOWED_CSG_RESET_EVENTS = {"valid_process_answer", "node_transition", "process_resume"}

@dataclass
class LintIssue:
    severity: str
    code: str
    message: str
    location: str


def _add(issues: list[LintIssue], severity: str, code: str, message: str, location: str) -> None:
    issues.append(LintIssue(severity, code, message, location))


def lint_source(source: dict[str, Any], tests: dict[str, Any] | None = None, repo_root: str | None = None) -> dict[str, Any]:
    issues: list[LintIssue] = []
    tests = tests or {}

    ordo_meta = source.get("ordo") or {}
    if ordo_meta.get("version") != "0.12":
        _add(issues, "error", "ORDO_VERSION_REQUIRED", "ordo.version must be '0.12'.", "ordo.version")

    package = ordo_meta.get("package")
    if not package:
        _add(issues, "error", "PACKAGE_REQUIRED", "ordo.package is required.", "ordo.package")

    control_level = ordo_meta.get("control_level")
    if control_level not in ALLOWED_CONTROL_LEVELS:
        _add(issues, "error", "CONTROL_LEVEL_REQUIRED", f"control_level must be one of {sorted(ALLOWED_CONTROL_LEVELS)}.", "ordo.control_level")

    execution_mode = ordo_meta.get("execution_mode")
    if execution_mode not in ALLOWED_EXECUTION_MODES:
        _add(issues, "error", "EXECUTION_MODE_REQUIRED", f"execution_mode must be one of {sorted(ALLOWED_EXECUTION_MODES)}.", "ordo.execution_mode")

    includes = source.get("includes", []) or []
    for i, include in enumerate(includes):
        if not include.get("version"):
            _add(issues, "error", "INCLUDE_VERSION_REQUIRED", "Each include must pin a version.", f"includes[{i}].version")

    gates = source.get("gates", []) or []
    for i, gate in enumerate(gates):
        loc = f"gates[{i}]"
        if not gate.get("id"):
            _add(issues, "error", "GATE_ID_REQUIRED", "Gate id is required.", f"{loc}.id")
        method = gate.get("method")
        if method not in ALLOWED_METHODS:
            _add(issues, "error", "GATE_METHOD_REQUIRED", f"Gate method must be one of {sorted(ALLOWED_METHODS)}.", f"{loc}.method")
        trust_class = gate.get("trust_class")
        if trust_class not in ALLOWED_TRUST_CLASSES:
            _add(issues, "error", "TRUST_CLASS_REQUIRED", f"Gate trust_class must be one of {sorted(ALLOWED_TRUST_CLASSES)}.", f"{loc}.trust_class")
        if method == "mechanical" and trust_class != "deterministic":
            _add(issues, "warning", "MECHANICAL_TRUST_MISMATCH", "mechanical gate should normally use trust_class: deterministic.", f"{loc}.trust_class")
        if method == "self_verification" and trust_class != "model_judgment":
            _add(issues, "warning", "SELF_VERIFICATION_TRUST_MISMATCH", "self_verification gate should normally use trust_class: model_judgment.", f"{loc}.trust_class")
        if method == "self_consistency" and trust_class != "repeated_model_judgment":
            _add(issues, "warning", "SELF_CONSISTENCY_TRUST_MISMATCH", "self_consistency gate should normally use trust_class: repeated_model_judgment.", f"{loc}.trust_class")
        if method == "human" and trust_class != "human_decision":
            _add(issues, "warning", "HUMAN_TRUST_MISMATCH", "human gate should normally use trust_class: human_decision.", f"{loc}.trust_class")

    assertions = source.get("assertions", []) or []
    for i, assertion in enumerate(assertions):
        loc = f"assertions[{i}]"
        if not assertion.get("id"):
            _add(issues, "error", "ASSERTION_ID_REQUIRED", "Assertion id is required.", f"{loc}.id")
        if assertion.get("polarity") not in ALLOWED_ASSERTION_POLARITIES:
            _add(issues, "error", "ASSERTION_POLARITY_REQUIRED", "Assertion polarity must be 'must' or 'not'.", f"{loc}.polarity")
        phases = assertion.get("phase") or []
        if not isinstance(phases, list) or not phases:
            _add(issues, "error", "ASSERTION_PHASE_REQUIRED", "Assertion phase must be a non-empty list.", f"{loc}.phase")
        else:
            for phase in phases:
                if phase not in ALLOWED_ASSERTION_PHASES:
                    _add(issues, "error", "ASSERTION_PHASE_INVALID", f"Invalid assertion phase: {phase}.", f"{loc}.phase")
        if assertion.get("severity") not in {"block", "warn", "info"}:
            _add(issues, "error", "ASSERTION_SEVERITY_REQUIRED", "Assertion severity must be block, warn, or info.", f"{loc}.severity")

    nodes = source.get("nodes", []) or []
    for i, node in enumerate(nodes):
        loc = f"nodes[{i}]"
        if not node.get("id"):
            _add(issues, "error", "NODE_ID_REQUIRED", "Node id is required.", f"{loc}.id")
        if not node.get("on_unmatched_input") and node.get("allow_unmatched_input") is not True:
            _add(issues, "error", "NODE_UNMATCHED_INPUT_REQUIRED", "Node must define on_unmatched_input or explicitly allow unmatched input.", f"{loc}.on_unmatched_input")

    freeforms = source.get("freeform", []) or []
    for i, block in enumerate(freeforms):
        loc = f"freeform[{i}]"
        maturity = block.get("maturity")
        if maturity not in ALLOWED_FREEFORM_MATURITY:
            _add(issues, "error", "FREEFORM_MATURITY_REQUIRED", f"FREEFORM maturity must be one of {sorted(ALLOWED_FREEFORM_MATURITY)}.", f"{loc}.maturity")
        incident_count = int(block.get("incident_count", 0) or 0)
        threshold = int(block.get("incident_threshold", 3) or 3)
        if incident_count >= threshold and maturity != "candidate_for_formalization":
            _add(issues, "warning", "FREEFORM_FORMALIZATION_RECOMMENDED", "FREEFORM incident threshold reached; consider formalization.", loc)

    csg = source.get("conversation_scope_guard")
    if csg is not None:
        loc = "conversation_scope_guard"
        if not isinstance(csg, dict):
            _add(issues, "error", "CSG_DECLARATION_INVALID", "conversation_scope_guard must be an object.", loc)
        else:
            supported = csg.get("supported")
            enabled = csg.get("enabled")
            if not isinstance(supported, bool):
                _add(issues, "error", "CSG_SUPPORTED_REQUIRED", "conversation_scope_guard.supported must be boolean.", f"{loc}.supported")
            if not isinstance(enabled, bool):
                _add(issues, "error", "CSG_ENABLED_REQUIRED", "conversation_scope_guard.enabled must be boolean.", f"{loc}.enabled")
            if enabled is True and supported is not True:
                _add(issues, "error", "CSG_ENABLED_REQUIRES_SUPPORT", "enabled CSG requires supported: true.", f"{loc}.supported")
            mode = csg.get("mode")
            if enabled is True and mode is None:
                _add(issues, "error", "CSG_MODE_REQUIRED", "enabled CSG requires an explicit mode.", f"{loc}.mode")
            elif mode is not None and mode not in ALLOWED_CSG_MODES:
                _add(issues, "error", "CSG_MODE_INVALID", f"CSG mode must be one of {sorted(ALLOWED_CSG_MODES)}.", f"{loc}.mode")
            if csg.get("state_change_on_out_of_scope", False) is not False:
                _add(issues, "error", "CSG_STATE_MUTATION_FORBIDDEN", "state_change_on_out_of_scope must be false.", f"{loc}.state_change_on_out_of_scope")
            escalation = csg.get("escalation") or {}
            if escalation and not isinstance(escalation, dict):
                _add(issues, "error", "CSG_ESCALATION_INVALID", "CSG escalation must be an object.", f"{loc}.escalation")
            elif isinstance(escalation, dict):
                counter_scope = escalation.get("counter_scope")
                if counter_scope is not None and counter_scope not in ALLOWED_CSG_COUNTER_SCOPES:
                    _add(issues, "error", "CSG_COUNTER_SCOPE_INVALID", f"CSG counter_scope must be one of {sorted(ALLOWED_CSG_COUNTER_SCOPES)}.", f"{loc}.escalation.counter_scope")
                for reset_event in escalation.get("reset_on", []) or []:
                    if reset_event not in ALLOWED_CSG_RESET_EVENTS:
                        _add(issues, "error", "CSG_RESET_EVENT_INVALID", f"Invalid CSG reset event: {reset_event}.", f"{loc}.escalation.reset_on")

    from .flow_reuse_validation import validate_flow_reuse
    flow_reuse_report = validate_flow_reuse(source)
    for issue in flow_reuse_report.get("issues", []) or []:
        _add(issues, issue.get("severity", "error"), issue.get("code", "FLOW_REUSE_ERROR"), issue.get("message", "Flow reuse validation failed."), issue.get("location", "flow_reuse"))

    from .graph_validation import validate_process_graph
    graph_report = validate_process_graph(source)
    for issue in graph_report.get("issues", []) or []:
        _add(issues, issue.get("severity", "error"), issue.get("code", "GRAPH_ERROR"), issue.get("message", "Graph validation failed."), issue.get("location", "graph"))

    registry_reports: dict[str, Any] = {}
    if repo_root is not None:
        from .registry_checks import validate_source_constructs, validate_capability_registry
        registry_reports["source_registry_check"] = validate_source_constructs(source, repo_root)
        registry_reports["capability_registry_check"] = validate_capability_registry(repo_root)
        for subreport in registry_reports.values():
            for issue in subreport.get("issues", []) or []:
                _add(issues, issue.get("severity", "error"), issue.get("code", "REGISTRY_ERROR"), issue.get("message", "Registry validation failed."), issue.get("location", "registry"))

    test_cases = tests.get("test_cases", []) if isinstance(tests, dict) else []
    if control_level == "strict" and not test_cases:
        _add(issues, "error", "STRICT_REQUIRES_TESTS", "strict control_level requires test cases.", "tests.test_cases")

    errors = [asdict(i) for i in issues if i.severity == "error"]
    warnings = [asdict(i) for i in issues if i.severity == "warning"]
    infos = [asdict(i) for i in issues if i.severity == "info"]

    result = {
        "status": "passed" if not errors else "failed",
        "summary": {"errors": len(errors), "warnings": len(warnings), "infos": len(infos)},
        "issues": [asdict(i) for i in issues],
    }
    result.update(registry_reports)
    result["graph_validation"] = graph_report
    result["flow_reuse_validation"] = flow_reuse_report
    return result
