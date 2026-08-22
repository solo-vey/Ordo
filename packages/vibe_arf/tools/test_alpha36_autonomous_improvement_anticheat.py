from pathlib import Path
import yaml,json,sys
R=Path(__file__).resolve().parents[1]; p=yaml.safe_load((R/"source/program.ordo.yaml").read_text(encoding="utf-8"))
ids={x.get("id") for x in p.get("playbook_laws",{}).get("laws",[])}; nodes={x.get("id"):x for x in p.get("nodes",[])}
req_laws={"E25_AUTONOMOUS_APPLIED_PLAYBOOK_IMPROVEMENT","E26_IMPROVEMENT_SCOPE_FREEZE","E27_FROZEN_FIXTURE_ANTI_CHEAT","E28_HOLDOUT_EVALUATOR_SEPARATION","E29_BEST_SO_FAR_RETENTION","E30_BUDGETED_NO_ANALYST_IMPROVEMENT"}
req_nodes={"N_AI_IMPROVEMENT_INIT","N_AI_TESTSET_FREEZE","N_AI_RUN_REVISION","N_AI_EVALUATE_REVISION","N_AI_DIAGNOSE","N_AI_DECIDE","N_AI_APPLY_REPAIR","N_AI_FINALIZE"}
pol=json.loads((R/"source/autonomous-playbook-improvement-policy.json").read_text())
checks={"VERSION":str(p["ordo"]["package_version"]).startswith("0.1."),"LAWS":req_laws<=ids,"NODES":req_nodes<=set(nodes),"NO_ANALYST":all(nodes[n].get("node_context",{}).get("user_question_allowed") is False for n in req_nodes),"PASS_ROUTES_IMPROVEMENT":nodes["N_SIM_CLASSIFY"]["on_answer"]["pass"]["next"]=="N_QH_BASELINE_CAPTURE","FREEZE":pol["scope_freeze"]["vibe_revision"].startswith("read_only"),"ANTI_CHEAT":bool(pol["anti_cheat"]["freeze_before_run"]),"HOLDOUT":bool(pol["anti_cheat"]["holdout"]),"BEST":pol["best_so_far"]["required"] is True,"NO_ANALYST_POLICY":pol["analyst_interaction"]["during_improvement"]=="forbidden"}
for k,v in checks.items(): print(f"{k}: {'PASS' if v else 'FAIL'}")
sys.exit(0 if all(checks.values()) else 1)
