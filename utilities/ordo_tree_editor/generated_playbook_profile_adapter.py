from __future__ import annotations

from pathlib import Path
from typing import Any

PROFILE_ID = "ordo.generated_playbook_profile/v1"
SUPPORTED_RUNTIME_EXECUTORS = {"package_tool"}


def _safe_relative_tool_ref(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip().replace("\\", "/")
    if not text:
        return None
    path = Path(text)
    if path.is_absolute() or ".." in path.parts:
        return None
    return path.as_posix()


def adapt_execution_profile(element: dict[str, Any], is_gate: bool = False) -> dict[str, Any]:
    """Map supported generated-playbook profile metadata into compiled execution semantics.

    This is intentionally an adapter layer, not canonical Ordo language semantics.
    The source object is never rewritten. The compiler may project a supported
    profile declaration into Runtime Semantic Plan execution traits/configuration;
    runtime then consumes only that compiled projection.
    """
    contract = element.get("execution_contract") if isinstance(element.get("execution_contract"), dict) else None
    if not contract or not str(contract.get("runtime_executor") or "").strip():
        return {"applied": False, "profile_id": PROFILE_ID, "diagnostics": []}

    executor = str(contract.get("runtime_executor") or "").strip()
    diagnostics: list[dict[str, Any]] = []
    if executor not in SUPPORTED_RUNTIME_EXECUTORS:
        diagnostics.append({
            "severity": "error",
            "code": "PROFILE_RUNTIME_EXECUTOR_UNSUPPORTED",
            "source_path": "execution_contract.runtime_executor",
            "value": executor,
            "detail": "generated-playbook profile executor is not supported by the Editor adapter",
        })
        return {"applied": False, "profile_id": PROFILE_ID, "diagnostics": diagnostics}

    if is_gate:
        diagnostics.append({
            "severity": "error",
            "code": "PROFILE_PACKAGE_TOOL_GATE_UNSUPPORTED",
            "source_path": "execution_contract.runtime_executor",
            "value": executor,
            "detail": "package_tool profile execution is supported for nodes, not gates",
        })
        return {"applied": False, "profile_id": PROFILE_ID, "diagnostics": diagnostics}

    owner = str(contract.get("owner") or "").strip().lower()
    if owner and owner != "deterministic":
        diagnostics.append({
            "severity": "error",
            "code": "PROFILE_EXECUTION_OWNER_CONFLICT",
            "source_path": "execution_contract.owner",
            "value": owner,
            "detail": "package_tool profile execution requires deterministic owner",
        })

    tool_ref = _safe_relative_tool_ref(element.get("tool_ref"))
    if tool_ref is None:
        diagnostics.append({
            "severity": "error",
            "code": "PROFILE_PACKAGE_TOOL_REF_INVALID",
            "source_path": "tool_ref",
            "value": element.get("tool_ref"),
            "detail": "package_tool profile requires one safe package-relative tool_ref",
        })
    elif not tool_ref.lower().endswith(".py"):
        diagnostics.append({
            "severity": "error",
            "code": "PROFILE_PACKAGE_TOOL_TYPE_UNSUPPORTED",
            "source_path": "tool_ref",
            "value": tool_ref,
            "detail": "generated-playbook package_tool adapter currently supports package-local Python tools only",
        })

    args_raw = element.get("args")
    if args_raw is None:
        args: list[str] = []
    elif isinstance(args_raw, list) and all(isinstance(x, (str, int, float, bool)) or x is None for x in args_raw):
        args = ["" if x is None else str(x) for x in args_raw]
    else:
        args = []
        diagnostics.append({
            "severity": "error",
            "code": "PROFILE_PACKAGE_TOOL_ARGS_INVALID",
            "source_path": "args",
            "value": args_raw,
            "detail": "package_tool profile args must be a flat scalar list",
        })

    errors = [d for d in diagnostics if d.get("severity") == "error"]
    if errors:
        return {"applied": False, "profile_id": PROFILE_ID, "diagnostics": diagnostics}

    declared_outputs: list[str] = []
    for candidate in (element.get("output"), ((element.get("artifact") or {}).get("expected_path") if isinstance(element.get("artifact"), dict) else None)):
        if isinstance(candidate, str) and candidate.strip():
            text = candidate.strip().replace("\\", "/")
            path = Path(text)
            if not path.is_absolute() and ".." not in path.parts:
                declared_outputs.append(path.as_posix())
    declared_outputs = list(dict.fromkeys(declared_outputs))

    return {
        "applied": True,
        "profile_id": PROFILE_ID,
        "diagnostics": diagnostics,
        "execution_traits_override": {
            "kind": "deterministic_operation",
            "requires_analyst": False,
            "model_executed": False,
            "model_executed_phases": [],
            "runtime_executor": "package_tool",
            "deterministic": True,
        },
        "execution_adapter": {
            "adapter": PROFILE_ID,
            "source_contract": "execution_contract.runtime_executor",
            "runtime_executor": "package_tool",
            "package_tool": {
                "tool_ref": tool_ref,
                "args": args,
                "result_contract": {
                    "route_key_field": "route_key",
                    "state_updates_field": "state_updates",
                    "status_field": "status",
                },
                "state_input": "runtime/state.yaml",
                "declared_outputs": declared_outputs,
            },
        },
    }


def adapt_artifact_validation_profile(element: dict[str, Any], source_doc: dict[str, Any], registry: dict[str, Any] | None = None) -> dict[str, Any]:
    """Project the generated-playbook artifact materialization profile into a deterministic gate adapter.

    Authority is structural only: mechanical+deterministic gate, exactly one declared predecessor,
    and that predecessor must declare artifact.state_path + artifact.expected_path. Optional
    verification/ARTIFACT_MATERIALIZATION_REGISTRY.json enriches the adapter with validators,
    required archive members and hashes. Natural-language condition text is never parsed to infer
    artifact semantics.
    """
    if str(element.get("method") or "").lower() != "mechanical" or str(element.get("trust_class") or "").lower() != "deterministic":
        return {"applied": False, "profile_id": PROFILE_ID, "diagnostics": []}
    incoming = element.get("allowed_from") if isinstance(element.get("allowed_from"), list) else []
    incoming = [str(x) for x in incoming if str(x).strip()]
    if len(incoming) != 1:
        return {"applied": False, "profile_id": PROFILE_ID, "diagnostics": []}
    nodes = {str(n.get("id")): n for n in (source_doc.get("nodes") or []) if isinstance(n, dict) and n.get("id")}
    producer = nodes.get(incoming[0])
    if not isinstance(producer, dict):
        return {"applied": False, "profile_id": PROFILE_ID, "diagnostics": []}
    artifact = producer.get("artifact") if isinstance(producer.get("artifact"), dict) else {}
    state_path = str(artifact.get("state_path") or "").strip()
    expected_path = str(artifact.get("expected_path") or producer.get("output") or "").strip().replace("\\", "/")
    if not state_path or not expected_path:
        return {"applied": False, "profile_id": PROFILE_ID, "diagnostics": []}
    ep = Path(expected_path)
    if ep.is_absolute() or ".." in ep.parts:
        return {"applied": False, "profile_id": PROFILE_ID, "diagnostics": [{
            "severity":"error","code":"PROFILE_ARTIFACT_EXPECTED_PATH_INVALID","source_path":"artifact.expected_path","value":expected_path,
            "detail":"generated-playbook artifact validation requires a safe package-relative expected path",
        }]}

    reg_entry = None
    if isinstance(registry, dict):
        matches=[]
        for item in registry.get("artifacts") or []:
            if not isinstance(item, dict):
                continue
            by_producer = str(item.get("materialization_node_id") or "") == incoming[0]
            by_path = str(item.get("output_path") or "").replace("\\", "/") == expected_path
            if by_producer or by_path:
                matches.append(item)
        if len(matches) == 1:
            reg_entry = matches[0]
        elif len(matches) > 1:
            return {"applied": False, "profile_id": PROFILE_ID, "diagnostics": [{
                "severity":"error","code":"PROFILE_ARTIFACT_VALIDATION_CONTRACT_AMBIGUOUS","source_path":"verification/ARTIFACT_MATERIALIZATION_REGISTRY.json",
                "value":[m.get("artifact_id") for m in matches],"detail":"multiple artifact registry entries match the same materialization producer/output",
            }]}

    content = reg_entry.get("content_contract") if isinstance(reg_entry, dict) and isinstance(reg_entry.get("content_contract"), dict) else {}
    validators = [str(x).replace("\\", "/") for x in ((reg_entry or {}).get("validators") or []) if isinstance(x, str) and x.strip()]
    required_members = [str(x).replace("\\", "/") for x in (content.get("required_members") or []) if isinstance(x, str) and x.strip()]
    forbidden_members = [str(x).replace("\\", "/") for x in (content.get("forbidden_members") or []) if isinstance(x, str) and x.strip()]
    member_hashes = content.get("member_hashes") if isinstance(content.get("member_hashes"), dict) else {}
    archive_hash = (reg_entry or {}).get("sha256") or content.get("sha256") or content.get("archive_sha256")
    output_type = str((reg_entry or {}).get("output_type") or ("archive" if expected_path.lower().endswith(".zip") else "document"))
    validation_contract_gaps: list[str] = []
    is_archive = output_type.lower() in {"archive", "package", "zip"} or expected_path.lower().endswith(".zip")
    if is_archive:
        if reg_entry is None:
            validation_contract_gaps.append("missing_artifact_materialization_registry_entry")
        if not required_members:
            validation_contract_gaps.append("archive_required_members_not_declared")
        if not member_hashes and not archive_hash:
            validation_contract_gaps.append("archive_hash_contract_not_declared")
    if isinstance(reg_entry, dict) and bool(reg_entry.get("post_materialization_validation_required")) and not validators:
        validation_contract_gaps.append("post_materialization_validator_not_declared")
    adapter_diagnostics = []
    if validation_contract_gaps:
        adapter_diagnostics.append({
            "severity":"warning",
            "code":"PROFILE_ARTIFACT_VALIDATION_CONTRACT_INCOMPLETE",
            "source_path":"verification/ARTIFACT_MATERIALIZATION_REGISTRY.json",
            "value":validation_contract_gaps,
            "detail":"deterministic native checks can run, but the generated-playbook profile does not declare enough evidence to claim the full artifact/archive validation gate; runtime will fail closed without LLM recovery",
        })
    return {
        "applied": True,
        "profile_id": PROFILE_ID,
        "diagnostics": adapter_diagnostics,
        "execution_adapter": {
            "adapter": PROFILE_ID,
            "source_contract": "producer.artifact + verification/ARTIFACT_MATERIALIZATION_REGISTRY.json",
            "runtime_executor": "artifact_validation",
            "artifact_validation": {
                "producer_id": incoming[0],
                "state_path": state_path,
                "expected_path": expected_path,
                "output_type": output_type,
                "validators": validators,
                "post_materialization_validation_required": bool((reg_entry or {}).get("post_materialization_validation_required")),
                "required_members": required_members,
                "forbidden_members": forbidden_members,
                "member_hashes": member_hashes,
                "archive_sha256": archive_hash,
                "registry_artifact_id": (reg_entry or {}).get("artifact_id"),
                "registry_contract_present": reg_entry is not None,
                "validation_contract_gaps": validation_contract_gaps,
            },
        },
    }
