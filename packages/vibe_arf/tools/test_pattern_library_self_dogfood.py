#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run_json(tool: str):
    p = subprocess.run([sys.executable, str(ROOT/'tools'/tool), str(ROOT)], capture_output=True, text=True)
    try:
        data = json.loads(p.stdout)
    except Exception:
        print(json.dumps({'status':'FAIL','reason':'non_json','tool':tool,'stdout':p.stdout[-2000:],'stderr':p.stderr[-2000:]}, indent=2))
        raise SystemExit(1)
    return p.returncode, data

fail=[]; passed=0
rc, graph = run_json('validate_pattern_graph_realization.py')
inst = {x.get('pattern_instance_id'): x for x in graph.get('instances',[])}
doc = inst.get('PI_BUSINESS_VIEW_DOCUMENT',{})
pkg = inst.get('PI_GENERATED_PLAYBOOK_PACKAGE',{})
checks = [
    ('document pattern exact graph realization', doc.get('status') == 'PASS'),
    ('package pattern exact graph realization', pkg.get('status') == 'PASS'),
]
rc, score = run_json('evaluate_pattern_reuse_opportunities.py')
qualified = {x.get('pattern_instance_id'): x for x in score.get('qualified_reuse_events',[])}
missed = {x.get('pattern_instance_id'): x for x in score.get('missed_reward_opportunities',[])}
checks += [
    ('document reward qualified', qualified.get('PI_BUSINESS_VIEW_DOCUMENT',{}).get('awarded_points') == 50),
    ('document is not a missed opportunity', 'PI_BUSINESS_VIEW_DOCUMENT' not in missed),
    ('package reward qualified', qualified.get('PI_GENERATED_PLAYBOOK_PACKAGE',{}).get('awarded_points') == 50),
    ('no selected pattern remains missed', not missed),
    ('two self patterns award +100', score.get('total_awarded_points',0) == 100),
]
for name, ok in checks:
    if ok: passed += 1
    else: fail.append(name)
print(json.dumps({'status':'PASS' if not fail else 'FAIL','passed':passed,'failed':len(fail),'failures':fail},indent=2))
raise SystemExit(0 if not fail else 1)
