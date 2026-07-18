from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

PROFILES = {"step_bound", "semantic_adaptive"}
ACTIONS = ("start", "ask", "answer", "present", "correction", "finish")
FACT_STATUSES = {"confirmed", "tentative", "withdrawn", "superseded", "unavailable", "irrelevant"}
TERMINAL_STATES = {"T_COMPLETED", "T_INPUT_BLOCKED", "T_SCENARIO_EXHAUSTED", "NO_GO", "not_ready"}
DIAGNOSTIC_STATUSES = {"model_reported", "trace_corroborated", "file_corroborated", "reproduced", "rejected"}

class BlindAutomationError(ValueError):
    pass

def validate_profile(profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    kind = profile.get("execution_profile")
    if kind not in PROFILES: errors.append("unsupported execution_profile")
    if profile.get("self_scoring") is not False: errors.append("self_scoring must be false")
    if set(profile.get("driver_protocol", [])) != set(ACTIONS): errors.append("driver_protocol must contain canonical actions")
    disclosure = profile.get("disclosure_policy", {})
    if disclosure.get("over_disclosure_guard") is not True: errors.append("over_disclosure_guard must be true")
    expected_mode = "step_bound" if kind == "step_bound" else "minimal_relevant"
    if kind in PROFILES and disclosure.get("mode") != expected_mode: errors.append(f"disclosure mode must be {expected_mode}")
    if set(profile.get("terminal_state_contract", [])) != TERMINAL_STATES: errors.append("terminal_state_contract must contain canonical states")
    if set(profile.get("fact_statuses", [])) != FACT_STATUSES: errors.append("fact_statuses must contain canonical lifecycle")
    av = profile.get("artifact_versioning", {})
    if av.get("immutable_versions") is not True or av.get("approval_scope") != "artifact_version": errors.append("artifact versions must be immutable and approval version-scoped")
    ci = profile.get("correction_invalidation", {})
    for key in ("invalidate_dependents", "invalidate_approvals", "consistency_review"):
        if ci.get(key) is not True: errors.append(f"correction_invalidation.{key} must be true")
    ev = profile.get("evaluation_contract", {})
    if ev.get("independent") is not True or ev.get("separate_process_and_document_scores") is not True: errors.append("evaluation must be independent and score process/documents separately")
    dg = profile.get("diagnostic_causal_review", {})
    if dg.get("self_scoring_prohibited") is not True or dg.get("corroboration_required") is not True: errors.append("diagnostic review must prohibit self-scoring and require corroboration")
    if not set(dg.get("allowed_claim_statuses", [])).issubset(DIAGNOSTIC_STATUSES): errors.append("unknown diagnostic claim status")
    if kind == "step_bound":
        steps = profile.get("step_catalog", [])
        ids = [x.get("step_id") for x in steps if isinstance(x, dict)]
        if not ids or len(ids) != len(set(ids)): errors.append("step_bound requires unique step_catalog")
        bindings = profile.get("step_disclosure_bindings", {})
        if any(s not in bindings for s in ids): errors.append("every step requires disclosure binding")
    if kind == "semantic_adaptive":
        intents = profile.get("intent_catalog", [])
        ids = [x.get("intent_id") for x in intents if isinstance(x, dict)]
        if not ids or len(ids) != len(set(ids)): errors.append("semantic_adaptive requires unique intent_catalog")
        if not profile.get("compound_intent_policy"): errors.append("compound_intent_policy required")
        if not profile.get("ambiguity_policy"): errors.append("ambiguity_policy required")
    return errors

@dataclass
class BlindRunState:
    profile: dict[str, Any]
    facts: dict[str, dict[str, Any]] = field(default_factory=dict)
    artifacts: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    approvals: dict[tuple[str, str], str] = field(default_factory=dict)
    audit: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        errors = validate_profile(self.profile)
        if errors: raise BlindAutomationError("; ".join(errors))

    def disclose(self, requested: list[str], allowed: set[str]) -> dict[str, Any]:
        keys = [k for k in requested if k in allowed and self.facts.get(k, {}).get("status") == "confirmed"]
        result = {k: self.facts[k]["value"] for k in keys}
        self.audit.append({"action":"answer","requested":requested,"disclosed":keys})
        return result

    def set_fact(self, fact_id: str, value: Any, status: str = "confirmed") -> None:
        if status not in FACT_STATUSES: raise BlindAutomationError("unknown fact status")
        previous = self.facts.get(fact_id)
        if previous and previous.get("status") == "confirmed" and previous.get("value") != value:
            previous["status"] = "superseded"
            self.invalidate_by_fact(fact_id)
        self.facts[fact_id] = {"value":value,"status":status}
        self.audit.append({"action":"correction" if previous else "present","fact_id":fact_id,"status":status})

    def register_artifact(self, artifact_id: str, version_id: str, depends_on: list[str]) -> None:
        versions = self.artifacts.setdefault(artifact_id, [])
        if any(v["version_id"] == version_id for v in versions): raise BlindAutomationError("artifact version must be immutable")
        versions.append({"version_id":version_id,"depends_on":list(depends_on),"status":"current","validated":False})

    def validate_artifact(self, artifact_id: str, version_id: str) -> None:
        v=self._version(artifact_id,version_id)
        if v["status"] != "current": raise BlindAutomationError("cannot validate stale artifact")
        v["validated"]=True

    def approve(self, artifact_id: str, version_id: str) -> None:
        v=self._version(artifact_id,version_id)
        if v["status"] != "current" or not v["validated"]: raise BlindAutomationError("approval requires current validated version")
        self.approvals[(artifact_id,version_id)]="approved"

    def invalidate_by_fact(self, fact_id: str) -> None:
        for artifact_id, versions in self.artifacts.items():
            for v in versions:
                if v["status"] == "current" and fact_id in v["depends_on"]:
                    v["status"]="stale"
                    key=(artifact_id,v["version_id"])
                    if key in self.approvals: self.approvals[key]="invalidated"

    def finish(self, required_facts: list[str], required_artifacts: list[str]) -> str:
        if any(self.facts.get(f,{}).get("status") != "confirmed" for f in required_facts): return "not_ready"
        for aid in required_artifacts:
            current=[v for v in self.artifacts.get(aid,[]) if v["status"]=="current"]
            if not current: return "not_ready"
            v=current[-1]
            if not v["validated"] or self.approvals.get((aid,v["version_id"])) != "approved": return "not_ready"
        return "T_COMPLETED"

    def _version(self, artifact_id: str, version_id: str) -> dict[str, Any]:
        for v in self.artifacts.get(artifact_id,[]):
            if v["version_id"] == version_id: return v
        raise BlindAutomationError("unknown artifact version")

def validate_diagnostic_claim(claim: dict[str, Any]) -> list[str]:
    errors=[]
    status=claim.get("status")
    if status not in DIAGNOSTIC_STATUSES: errors.append("unknown diagnostic status")
    if status != "model_reported" and not claim.get("evidence_refs"): errors.append("corroborated status requires evidence_refs")
    required=("source_node","loaded_assets","confirmed_evidence","gate_path","suspected_component")
    for key in required:
        if key not in claim: errors.append(f"missing {key}")
    return errors
