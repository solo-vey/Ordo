#!/usr/bin/env python3
from pathlib import Path
import yaml,json,sys
R=Path(__file__).resolve().parents[1]
d=yaml.safe_load((R/"source/program.ordo.yaml").read_text(encoding="utf-8")) or {}
nodes={n["id"]:n for n in d.get("nodes",[]) if isinstance(n,dict) and n.get("id")}
required=["N_VERIFY_SOURCE","N_VERIFY_STRUCTURE","N_VERIFY_ARTIFACTS","N_VERIFY_REGRESSION","N_VERIFY_RELEASE"]
checks={}
checks["five_visible_stages_present"]=all(x in nodes for x in required)
checks["old_abstract_stage_absent"]="N_TOOL_EXECUTABLE_VERIFICATION" not in nodes
checks["all_have_allowed_tools"]=all(bool((nodes[x].get("node_context") or {}).get("allowed_tools")) for x in required)
checks["all_have_knowledge_refs"]=all(bool((nodes[x].get("node_context") or {}).get("knowledge_refs")) for x in required)
checks["verification_nodes_have_explicit_tool_contracts"]=all(
    bool((nodes[x].get("node_context") or {}).get("allowed_tools")) for x in required
)
# exact RUN -> GATE -> RUN chain
gates={g["id"]:g for g in d.get("gates",[]) if isinstance(g,dict) and g.get("id")}
def nxt(n):
    oa=n.get("on_answer") or {}
    return oa.get("next") if isinstance(oa,dict) else n.get("next")
run_gate_chain=[
 ("N_B_SOURCE_MATERIALIZE","N_VERIFY_SOURCE","G_SOURCE_VERIFICATION_PASS","N_VERIFY_STRUCTURE"),
 ("N_VERIFY_STRUCTURE",None,"G_STRUCTURE_VERIFICATION_PASS","N_VERIFY_ARTIFACTS"),
 ("N_VERIFY_ARTIFACTS",None,"G_ARTIFACT_VERIFICATION_PASS","N_VERIFY_REGRESSION"),
 ("N_VERIFY_REGRESSION",None,"G_REGRESSION_VERIFICATION_PASS","N_VERIFY_RELEASE"),
 ("N_VERIFY_RELEASE",None,"G_RELEASE_VERIFICATION_PASS","N_B_ORDO_LANGUAGE_GROUNDING_CHECK")
]
checks["verification_chain_is_real"]=(
    nxt(nodes["N_B_SOURCE_MATERIALIZE"])=="N_VERIFY_PATTERN_GRAPH_REALIZATION"
    and nxt(nodes["N_VERIFY_PATTERN_GRAPH_REALIZATION"])=="G_PATTERN_GRAPH_REALIZATION_VALID"
    and gates["G_PATTERN_GRAPH_REALIZATION_VALID"].get("on_pass")=="N_VERIFY_SOURCE"
    and nxt(nodes["N_VERIFY_SOURCE"])=="G_SOURCE_VERIFICATION_PASS"
    and gates["G_SOURCE_VERIFICATION_PASS"].get("on_pass")=="N_VERIFY_INFORMATION_PROJECTION"
    and nxt(nodes["N_VERIFY_INFORMATION_PROJECTION"])=="G_INFORMATION_PROJECTION_PASS"
    and gates["G_INFORMATION_PROJECTION_PASS"].get("on_pass")=="N_VERIFY_STRUCTURE"
    and nxt(nodes["N_VERIFY_STRUCTURE"])=="G_STRUCTURE_VERIFICATION_PASS"
    and gates["G_STRUCTURE_VERIFICATION_PASS"].get("on_pass")=="N_VERIFY_ARTIFACTS"
    and nxt(nodes["N_VERIFY_ARTIFACTS"])=="G_ARTIFACT_VERIFICATION_PASS"
    and gates["G_ARTIFACT_VERIFICATION_PASS"].get("on_pass")=="N_VERIFY_REGRESSION"
    and nxt(nodes["N_VERIFY_REGRESSION"])=="G_REGRESSION_VERIFICATION_PASS"
    and gates["G_REGRESSION_VERIFICATION_PASS"].get("on_pass")=="N_VERIFY_RELEASE"
    and nxt(nodes["N_VERIFY_RELEASE"])=="G_RELEASE_VERIFICATION_PASS"
    and gates["G_RELEASE_VERIFICATION_PASS"].get("on_pass")=="N_B_ORDO_LANGUAGE_GROUNDING_CHECK"
)
checks["verification_gates_are_deterministic"]=all(
    gates[g].get("trust_class")=="deterministic" and gates[g].get("method")=="mechanical"
    for g in ["G_SOURCE_VERIFICATION_PASS","G_STRUCTURE_VERIFICATION_PASS","G_ARTIFACT_VERIFICATION_PASS",
              "G_REGRESSION_VERIFICATION_PASS","G_RELEASE_VERIFICATION_PASS"]
)
# responsibility map
rm=json.loads((R/"verification/EXECUTION_RESPONSIBILITY_MAP.json").read_text(encoding="utf-8"))
by={e.get("element_id"):e for e in rm.get("entries",[]) if isinstance(e,dict)}
checks["all_five_classified_deterministic"]=all(by.get(x,{}).get("class")=="deterministic" for x in required)
checks["all_five_have_tool_refs"]=all(bool(by.get(x,{}).get("tool_or_validator_refs")) for x in required)
status="PASS" if all(checks.values()) else "FAIL"
print(json.dumps({"status":status,"checks":checks},ensure_ascii=False,indent=2))
raise SystemExit(0 if status=="PASS" else 1)
