#!/usr/bin/env python3
import json,subprocess,sys,tempfile,shutil,yaml
from pathlib import Path
R=Path(__file__).resolve().parents[1]; tool=R/'tools/analyze_data_layer_architecture.py'
def run(root):
 with tempfile.TemporaryDirectory() as td:
  o=Path(td)/'o.json'; cp=subprocess.run([sys.executable,str(tool),str(root),'--output',str(o)],capture_output=True,text=True); assert cp.returncode==0,cp.stderr; return json.loads(o.read_text())
d=run(R); assert d['score_effect']==0; assert d['summary']=={'SINGLE_RESPONSIBILITY':0,'RUN_TO_GATE':0,'DETERMINISTIC_FIRST_EXECUTION':0},d
# negative SR fixture
with tempfile.TemporaryDirectory() as td:
 t=Path(td); (t/'authoring').mkdir(); shutil.copy2(R/'authoring/information_object_catalog.yaml',t/'authoring/information_object_catalog.yaml'); shutil.copy2(R/'authoring/information_flow_graph.yaml',t/'authoring/information_flow_graph.yaml')
 g=yaml.safe_load((t/'authoring/information_flow_graph.yaml').read_text()); gate=next(x for x in g['nodes'] if x.get('id')=='IG_INFORMATION_MODEL'); gate['covers'].append('I_PATTERN_EXECUTION_PROJECTION'); g['edges'].append({'from':'I_PATTERN_EXECUTION_PROJECTION','to':'IG_INFORMATION_MODEL','type':'validated_by'}); (t/'authoring/information_flow_graph.yaml').write_text(yaml.safe_dump(g,sort_keys=False))
 x=run(t); assert x['summary']['SINGLE_RESPONSIBILITY']>=1
print('ALPHA42 DATA LAYER ARCHITECTURE DETECTORS: PASS')
