#!/usr/bin/env python3
from pathlib import Path
import json,yaml
R=Path(__file__).resolve().parents[1]
checks={}
manifest=yaml.safe_load((R/"ordo.yml").read_text(encoding="utf-8")) or {}
source=yaml.safe_load((R/"source/program.ordo.yaml").read_text(encoding="utf-8")) or {}
lock=json.loads((R/"ordo.lock.json").read_text(encoding="utf-8"))
nodes={n["id"]:n for n in source.get("nodes",[]) if isinstance(n,dict) and n.get("id")}
manifest_version=manifest.get("version")
source_version=((source.get("ordo") or {}).get("package_version"))
lock_version=((lock.get("package") or {}).get("version"))
checks["manifest_revision_present"]=bool(manifest_version)
checks["source_revision_matches_manifest"]=source_version==manifest_version
checks["lock_revision_matches_manifest"]=lock_version==manifest_version
checks["generated_outputs_placeholder_declared_for_outputless_package"]=(R/"generated_outputs/.gitkeep").is_file()

# Change reroute may pass through mandatory capture/preprocessing nodes; prove it reaches source assimilation without looping.
cur=((nodes.get("N_C_ROUTE_PLAN",{}).get("on_answer") or {}).get("next")); seen=set(); reaches=False
for _ in range(8):
    if cur=="N_U_SOURCE_ASSIMILATION": reaches=True; break
    if not cur or cur in seen or cur not in nodes: break
    seen.add(cur); cur=((nodes[cur].get("on_answer") or {}).get("next"))
checks["change_route_is_not_dead_end"]=reaches
profile=json.loads((R/"verification_profile.json").read_text(encoding="utf-8"))
runners={c.get("runner") for c in profile.get("checks",[])}
checks["artifact_stage_names_language_checks"]=all(x in runners for x in ["ordo_validate_artifacts","ordo_consistency","ordo_validate_output"])
checks["release_stage_names_lock_checks"]=all(x in runners for x in ["ordo_validate_lock","ordo_check_conflicts","ordo_repo_check"])
checks["profile_contains_full_language_package_checks"]=all(x in runners for x in [
    "ordo_validate_artifacts","ordo_consistency","ordo_validate_output",
    "ordo_validate_lock","ordo_check_conflicts","ordo_repo_check"])
status="PASS" if all(checks.values()) else "FAIL"
print(json.dumps({"status":status,"checks":checks},ensure_ascii=False,indent=2))
raise SystemExit(0 if status=="PASS" else 1)
