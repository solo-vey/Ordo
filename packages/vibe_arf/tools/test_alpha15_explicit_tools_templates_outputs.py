#!/usr/bin/env python3
from pathlib import Path
import json,yaml,sys
R=Path(__file__).resolve().parents[1]
d=yaml.safe_load((R/"source/program.ordo.yaml").read_text(encoding="utf-8")) or {}
nodes={n["id"]:n for n in d.get("nodes",[]) if isinstance(n,dict) and n.get("id")}
outs={o["id"]:o for o in d.get("outputs",[]) if isinstance(o,dict) and o.get("id")}
checks={}
required_nodes=[
 "N_A_BUSINESS_VIEW_TEMPLATE_BIND","N_A_PACKAGE_ASSEMBLY_CONTRACT_BIND",
 "N_VERIFY_SOURCE","N_VERIFY_STRUCTURE","N_VERIFY_ARTIFACTS","N_VERIFY_REGRESSION","N_VERIFY_RELEASE",
 "N_PI_BUSINESS_VIEW_DOCUMENT_MATERIALIZE","N_OUT_GENERATED_PACKAGE_HANDOFF"
]
checks["explicit_nodes_present"]=all(n in nodes for n in required_nodes)
checks["hybrid_execution_declared"]=bool(d.get("hybrid_execution")) and d["hybrid_execution"].get("cli_role")=="deterministic_helper"
tool_nodes=["N_A_BUSINESS_VIEW_TEMPLATE_BIND","N_A_PACKAGE_ASSEMBLY_CONTRACT_BIND",
            "N_VERIFY_SOURCE","N_VERIFY_STRUCTURE","N_VERIFY_ARTIFACTS","N_VERIFY_REGRESSION","N_VERIFY_RELEASE",
            "N_PI_BUSINESS_VIEW_DOCUMENT_MATERIALIZE","N_OUT_GENERATED_PACKAGE_HANDOFF"]
checks["runtime_tools_visible"]=all(bool((nodes[n].get("node_context") or {}).get("allowed_tools")) for n in tool_nodes)
checks["business_template_exact_ref"]="canonical_support/output_templates/BUSINESS_VIEW.template.md" in (
    (nodes["N_A_BUSINESS_VIEW_TEMPLATE_BIND"].get("node_context") or {}).get("knowledge_refs") or [])
checks["package_assembly_exact_ref"]="canonical_support/output_templates/GENERATED_PLAYBOOK_PACKAGE_ASSEMBLY_CONTRACT.json" in (
    (nodes["N_A_PACKAGE_ASSEMBLY_CONTRACT_BIND"].get("node_context") or {}).get("knowledge_refs") or [])
all_refs=set()
for nid in ["N_VERIFY_SOURCE","N_VERIFY_STRUCTURE","N_VERIFY_ARTIFACTS","N_VERIFY_REGRESSION","N_VERIFY_RELEASE"]:
    all_refs.update((nodes[nid].get("node_context") or {}).get("knowledge_refs") or [])
checks["python_verification_refs_visible"]=all(x in all_refs for x in [
    "verification_profile.json","tools/run_verification_profile.py",
    "tools/verify_execution_responsibility_map.py","tools/validate_artifact_materialization_registry.py"
])
checks["business_output_bound_to_handoff"]=outs.get("OUT_BUSINESS_VIEW",{}).get("allowed_after")in (["N_OUT_BUSINESS_VIEW_MATERIALIZE"],["N_PI_BUSINESS_VIEW_DOCUMENT_REGISTER_ARTIFACT"])
checks["package_output_bound_to_handoff"]=outs.get("OUT_GENERATED_PLAYBOOK_PACKAGE",{}).get("allowed_after")==["N_OUT_GENERATED_PACKAGE_HANDOFF"]
checks["business_template_exists"]=(R/"canonical_support/output_templates/BUSINESS_VIEW.template.md").is_file()
checks["package_contract_exists"]=(R/"canonical_support/output_templates/GENERATED_PLAYBOOK_PACKAGE_ASSEMBLY_CONTRACT.json").is_file()
status="PASS" if all(checks.values()) else "FAIL"
print(json.dumps({"status":status,"checks":checks},ensure_ascii=False,indent=2))
raise SystemExit(0 if status=="PASS" else 1)
