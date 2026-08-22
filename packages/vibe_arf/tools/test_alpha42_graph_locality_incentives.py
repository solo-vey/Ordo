#!/usr/bin/env python3
import json, subprocess, tempfile, textwrap
from pathlib import Path
R=Path(__file__).resolve().parents[1]
TOOL=R/'tools/analyze_graph_locality.py'
errs=[]
def ck(x,m):
    if not x: errs.append(m)

def run_fixture(src):
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'graph.yaml'; p.write_text(textwrap.dedent(src))
        out=Path(td)/'out.json'
        cp=subprocess.run(['python3',str(TOOL),'--graph',str(p),'--output',str(out)],text=True,capture_output=True)
        ck(cp.returncode==0,'analyzer failed: '+cp.stderr+cp.stdout)
        return json.loads(out.read_text()) if out.exists() else {}

ck(TOOL.exists(),'graph locality analyzer missing')
if TOOL.exists():
    direct=run_fixture('''
    schema_version: '1.0'
    nodes:
      - {id: I_X, kind: information}
      - {id: G_X, kind: validation_gate, covers: [I_X]}
      - {id: I_Y, kind: information}
    edges:
      - {from: I_X, to: G_X, type: validated_by}
      - {from: G_X, to: I_Y, type: depends_on}
    ''')
    m=direct.get('variables',{}).get('I_X',{})
    ck(m.get('validation_latency')==1,'direct latency must be 1')
    ck(m.get('unvalidated_exposure_count')==0,'direct exposure must be 0')
    ck(m.get('rollback_span')==0,'direct rollback must be 0')

    delayed=run_fixture('''
    schema_version: '1.0'
    nodes:
      - {id: I_X, kind: information}
      - {id: I_A, kind: information}
      - {id: I_B, kind: information}
      - {id: A_C, kind: artifact}
      - {id: G_X, kind: validation_gate, covers: [I_X]}
      - {id: I_AFTER, kind: information}
    edges:
      - {from: I_X, to: I_A, type: derived_from}
      - {from: I_A, to: I_B, type: derived_from}
      - {from: I_B, to: G_X, type: validated_by}
      - {from: I_A, to: A_C, type: materializes}
      - {from: G_X, to: I_AFTER, type: depends_on}
    ''')
    m=delayed.get('variables',{}).get('I_X',{})
    ck(m.get('validation_latency')==3,'delayed latency must be 3')
    ck(m.get('unvalidated_exposure_count')==3,'exposure must include I_A,I_B,A_C')
    ck(m.get('rollback_span')==3,'rollback span must match affected pre-gate info/artifact nodes')
    ck(set(m.get('unvalidated_exposure_nodes',[]))=={'I_A','I_B','A_C'},'wrong exposure nodes')

    multi=run_fixture('''
    schema_version: '1.0'
    nodes:
      - {id: I_X, kind: information}
      - {id: I_A, kind: information}
      - {id: G_FAST, kind: validation_gate, covers: [I_X]}
      - {id: G_SLOW, kind: validation_gate, covers: [I_X]}
    edges:
      - {from: I_X, to: G_FAST, type: validated_by}
      - {from: I_X, to: I_A, type: derived_from}
      - {from: I_A, to: G_SLOW, type: validated_by}
    ''')
    m=multi.get('variables',{}).get('I_X',{})
    ck(m.get('validation_latency')==1,'nearest validating gate must win')
    ck(m.get('validating_gate')=='G_FAST','wrong nearest gate')
    ck(m.get('unvalidated_exposure_count')==0,'nodes after earliest validation are not exposure')

reg=json.loads((R/'source/design_rule_incentive_registry.v1.json').read_text())
by={x['id']:x for x in reg['rules']}
for rid in ['VALIDATION_LATENCY','UNVALIDATED_EXPOSURE','ROLLBACK_SPAN']:
    ck(rid in by,rid+' registry rule missing')
    if rid in by:
        ck(by[rid].get('enforcement')=='OPPORTUNITY',rid+' must remain OPPORTUNITY')
        ck(by[rid].get('score_effect')==0,rid+' score must remain zero before calibration')
        ck(by[rid].get('regression_asset')=='tools/test_alpha42_graph_locality_incentives.py',rid+' regression asset mismatch')

if errs:
    print('ALPHA42 GRAPH LOCALITY INCENTIVES: FAIL')
    [print('-',e) for e in errs]
    raise SystemExit(1)
print('ALPHA42 GRAPH LOCALITY INCENTIVES: PASS')
