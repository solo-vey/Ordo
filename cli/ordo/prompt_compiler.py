from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib
import json
import yaml

COMPILER_VERSION = "0.1.0"
RETAINED_GUARANTEES = [
    "authoring_rigor",
    "single_source_of_truth",
    "explicit_process_structure",
    "state_schema_as_documentation",
    "documented_branch_and_backtrack_behavior",
]
LOST_GUARANTEES = [
    "mechanical_gate_enforcement",
    "runtime_state_validation",
    "enforced_transition_control",
    "csg_enforced_protection",
    "runtime_evidence_capture_by_default",
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _render_node(node: dict[str, Any]) -> str:
    lines = [f"### {node.get('id', 'UNNAMED_NODE')}"]
    if node.get("question"):
        lines.append(f"Ask: {node['question']}")
    if node.get("answer_type"):
        lines.append(f"Expected answer type: `{node['answer_type']}`.")
    if node.get("allowed_answers"):
        lines.append("Allowed answers: " + ", ".join(map(str, node["allowed_answers"])))
    on_answer = node.get("on_answer")
    if isinstance(on_answer, dict):
        if "next" in on_answer:
            lines.append(f"On accepted answer, continue to `{on_answer['next']}`.")
        else:
            branches=[]
            for key,val in on_answer.items():
                if isinstance(val,dict) and val.get('next'):
                    branches.append(f"`{key}` → `{val['next']}`")
            if branches:
                lines.append("Branch routing: " + "; ".join(branches) + ".")
    unmatched=node.get("on_unmatched_input") or {}
    if unmatched:
        lines.append("Invalid or unclear input: request clarification; do not invent an answer.")
        if unmatched.get("max_attempts") is not None:
            lines.append(f"Maximum clarification attempts: {unmatched['max_attempts']}.")
    return "\n\n".join(lines)


def compile_prompt_only(source_path: str|Path, out_dir: str|Path, *, playbook_version: str|None=None,
                        language_version: str|None=None, framework_version: str|None=None,
                        model_profile: str="provider-neutral", evidence_basis: dict[str,Any]|None=None) -> dict[str,Any]:
    source_path=Path(source_path).resolve(); out_dir=Path(out_dir).resolve()
    source=yaml.safe_load(source_path.read_text(encoding='utf-8')) or {}
    meta=source.get('ordo') or {}; package=meta.get('package','unnamed.package')
    out_dir.mkdir(parents=True, exist_ok=True)
    intent=source.get('intent') or {}; contract=source.get('contract') or {}; state=source.get('state') or {}
    nodes=source.get('nodes') or []; gates=source.get('gates') or []
    sections=[
        f"# Model Instructions — {package}",
        "> This artifact was compiled from an Ordo playbook for direct model use. It does **not** provide full Ordo runtime enforcement.",
        "## Purpose\n\n" + str(intent.get('description') or intent.get('id') or 'Follow the defined process.'),
        "## Operating rules\n\n- Follow nodes in order and apply explicit branches.\n- Never fabricate mandatory data, approvals, state, or evidence.\n- Ask for clarification when input is missing or invalid.\n- Do not skip gates or claim they are mechanically enforced.\n- Preserve corrections and backtracking in the conversation.\n- Stop safely when a required condition cannot be satisfied.",
        "## Required contract fields\n\n" + ("\n".join(f"- `{x}`" for x in contract.get('required',[])) or "- None declared."),
        "## State model (documentation only)\n\n```yaml\n" + yaml.safe_dump(state.get('schema',{}),sort_keys=False,allow_unicode=True).rstrip()+"\n```",
        "## Process nodes\n\n" + "\n\n".join(_render_node(n) for n in nodes),
    ]
    if gates:
        sections.append("## Gates (instructional, not mechanically enforced)\n\n"+"\n".join(f"- `{g.get('id')}`: {g.get('description') or g.get('condition') or 'Evaluate as defined in source.'}" for g in gates))
    sections.append("## Completion rule\n\nComplete only when the source-defined terminal condition is satisfied. Clearly state unresolved gaps and never overclaim Ordo runtime guarantees.")
    instructions="\n\n".join(sections)+"\n"
    instruction_path=out_dir/'MODEL_INSTRUCTIONS.md'; instruction_path.write_text(instructions,encoding='utf-8')
    source_sha=_sha256(source_path)
    manifest={
        "schema_version":"ordo.prompt_compilation_manifest.v1",
        "status":"compiled",
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "compiler":{"name":"ordo.prompt_only","version":COMPILER_VERSION},
        "compiled_from":{"playbook_id":package,"playbook_version":playbook_version or "unresolved","ordo_source_path":source_path.name,"ordo_source_sha256":source_sha},
        "versions":{"language":language_version or meta.get('version') or "unresolved","framework":framework_version or "unresolved"},
        "compilation_target":"prompt_only",
        "model_profile":model_profile,
        "guarantees_retained":RETAINED_GUARANTEES,
        "guarantees_lost":LOST_GUARANTEES,
        "equivalent_to_engine_runtime":False,
        "source_binding":{"invalidated_when":["source_sha256_changes","compiler_version_changes","compilation_policy_changes","model_profile_changes"]},
        "artifacts":{"instructions":"MODEL_INSTRUCTIONS.md","instructions_sha256":_sha256(instruction_path)},
        "evidence_basis":evidence_basis or {"status":"not_evaluated","case_ids":[],"model_profiles":[]},
    }
    _json(out_dir/'PROMPT_COMPILATION_MANIFEST.json',manifest)
    return manifest


def validate_prompt_compilation(out_dir: str|Path, *, source_path: str|Path|None=None) -> dict[str,Any]:
    out=Path(out_dir); issues=[]
    mp=out/'PROMPT_COMPILATION_MANIFEST.json'; ip=out/'MODEL_INSTRUCTIONS.md'
    if not mp.exists(): issues.append({"code":"ORDO-PROMPT-001","message":"missing prompt compilation manifest"})
    if not ip.exists(): issues.append({"code":"ORDO-PROMPT-002","message":"missing model instructions"})
    data={}
    if mp.exists():
        try: data=json.loads(mp.read_text(encoding='utf-8'))
        except Exception: issues.append({"code":"ORDO-PROMPT-003","message":"manifest is not valid JSON"})
    if data:
        if data.get('compilation_target')!='prompt_only': issues.append({"code":"ORDO-PROMPT-004","message":"invalid compilation target"})
        if not data.get('guarantees_retained') or not data.get('guarantees_lost'): issues.append({"code":"ORDO-PROMPT-005","message":"retained/lost guarantee declarations are mandatory"})
        if data.get('equivalent_to_engine_runtime') is not False: issues.append({"code":"ORDO-PROMPT-006","message":"prompt-only output must not claim runtime equivalence"})
        if ip.exists() and data.get('artifacts',{}).get('instructions_sha256')!=_sha256(ip): issues.append({"code":"ORDO-PROMPT-007","message":"instruction checksum mismatch"})
        if source_path and Path(source_path).exists() and data.get('compiled_from',{}).get('ordo_source_sha256')!=_sha256(Path(source_path)):
            issues.append({"code":"ORDO-PROMPT-008","message":"compiled prompt is stale relative to Ordo source"})
    return {"status":"passed" if not issues else "failed","issues":issues,"manifest":str(mp),"instructions":str(ip)}


def assess_runtime_route(metrics: dict[str,Any], policy: dict[str,Any]|None=None) -> dict[str,Any]:
    policy=policy or {"minimum_composite_score":90,"minimum_branch_score":85,"minimum_backtrack_score":85,"minimum_runs":3}
    blockers=[]
    runs=int(metrics.get('runs',0)); composite=float(metrics.get('composite_score',0)); branch=float(metrics.get('branch_score',0)); backtrack=float(metrics.get('backtrack_score',0))
    if runs < policy['minimum_runs']: blockers.append('insufficient_repeated_runs')
    if composite < policy['minimum_composite_score']: blockers.append('composite_score_below_threshold')
    if branch < policy['minimum_branch_score']: blockers.append('branch_score_below_threshold')
    if backtrack < policy['minimum_backtrack_score']: blockers.append('backtrack_score_below_threshold')
    route='prompt_only' if not blockers else 'engine_runtime'
    return {"status":"passed","recommended_target":route,"blocking_reasons":blockers,"metrics":metrics,"policy":policy,"revalidation_required_on":["model_provider_change","model_version_change","source_change","compiler_change","policy_change"]}
