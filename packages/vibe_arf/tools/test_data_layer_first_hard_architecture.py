#!/usr/bin/env python3
import json, subprocess, sys, tempfile, shutil
from pathlib import Path
import yaml
R=Path(__file__).resolve().parents[1]
res=[]
def ck(i,c,d=''): res.append({'id':i,'status':'PASS' if c else 'FAIL','detail':d})
pol=R/'source/data-layer-first-hard-architecture-policy.json'
ck('DLF_POLICY_EXISTS',pol.exists())
if pol.exists():
 p=json.loads(pol.read_text())
 ck('DLF_CANONICAL_SOURCE',p.get('authoring_source_of_truth')=='data_layer')
 ck('DLF_DIRECT_GRAPH_EDIT_FORBIDDEN',p.get('direct_graph_or_source_semantic_edit')=='forbidden')
 ck('DLF_WRITE_ORDER',p.get('required_write_order')==['data_layer','validate_data_layer','derive_projection','materialize_source','validate_projection_lineage'])
 ck('DLF_STALE_ON_UPSTREAM_CHANGE',p.get('upstream_change_invalidates_downstream_projection') is True)
else:
 for x in ['DLF_CANONICAL_SOURCE','DLF_DIRECT_GRAPH_EDIT_FORBIDDEN','DLF_WRITE_ORDER','DLF_STALE_ON_UPSTREAM_CHANGE']: ck(x,False)
laws=(R/'PLAYBOOK_LAWS.md').read_text(encoding='utf-8')
ck('DLF_CANONICAL_LAW','E42_DATA_LAYER_CANONICAL_SOURCE' in laws)
val=R/'tools/validate_data_layer_first_architecture.py'; mat=R/'tools/materialize_data_layer_projection_lineage.py'; editor_mat=R/'tools/materialize_editor_visible_architecture.py'
ck('DLF_VALIDATOR_EXISTS',val.exists()); ck('DLF_LINEAGE_MATERIALIZER_EXISTS',mat.exists()); ck('DLF_EDITOR_MATERIALIZER_EXISTS',editor_mat.exists())
# workflow ordering
prog=yaml.safe_load((R/'source/program.ordo.yaml').read_text()) or {}
by={x.get('id'):x for k in ('nodes','gates') for x in prog.get(k,[]) if isinstance(x,dict)}
def nxt(i): return ((by.get(i,{}).get('on_answer') or {}).get('next'))
ck('DLF_PRE_GRAPH_GATE_PRESENT','N_VERIFY_DATA_LAYER_CANONICAL' in by and 'G_DATA_LAYER_CANONICAL_READY' in by)
ck('DLF_PRE_GRAPH_ORDER',nxt('N_U_PROPOSAL_CANONICALIZATION')=='N_VERIFY_DATA_LAYER_CANONICAL' and nxt('N_VERIFY_DATA_LAYER_CANONICAL')=='G_DATA_LAYER_CANONICAL_READY' and by.get('G_DATA_LAYER_CANONICAL_READY',{}).get('on_pass')=='N_VERIFY_INFORMATION_MODEL')
# graph/process synthesis must remain downstream of information gate
ck('DLF_PROCESS_AFTER_DATA_GATE', by.get('G_INFORMATION_MODEL_READY',{}).get('on_pass')=='N_VERIFY_PATTERN_DATA_LAYER_MERGE' and nxt('N_VERIFY_PATTERN_DATA_LAYER_MERGE')=='G_PATTERN_DATA_LAYER_MERGE_VALID' and by.get('G_PATTERN_DATA_LAYER_MERGE_VALID',{}).get('on_pass')=='N_U_LEGACY_MIGRATION')
# post-source verifier explicitly enforces lineage
q=str(by.get('N_VERIFY_INFORMATION_PROJECTION',{}).get('question',''))
ck('DLF_POST_SOURCE_LINEAGE_CHECK','validate_data_layer_first_architecture.py' in q and 'projection lineage' in q.lower())
# behavioral fixture: materialize lineage then detect upstream/downstream drift
if val.exists() and mat.exists():
 with tempfile.TemporaryDirectory() as td:
  d=Path(td); shutil.copytree(R/'authoring',d/'authoring'); (d/'source').mkdir(); (d/'editor').mkdir()
  # minimal current source as projection target
  shutil.copy2(R/'source/program.ordo.yaml',d/'source/program.ordo.yaml')
  # copy policy and materialize every declared derived intermediate before lineage freeze
  (d/'source/data-layer-first-hard-architecture-policy.json').write_text(pol.read_text())
  er=subprocess.run([sys.executable,str(editor_mat),str(d)],capture_output=True,text=True)
  ck('DLF_EDITOR_INTERMEDIATE_MATERIALIZES',er.returncode==0,er.stdout[-300:]+er.stderr[-300:])
  r=subprocess.run([sys.executable,str(mat),str(d)],capture_output=True,text=True)
  ck('DLF_LINEAGE_MATERIALIZES',r.returncode==0,r.stdout[-300:]+r.stderr[-300:])
  r=subprocess.run([sys.executable,str(val),str(d)],capture_output=True,text=True)
  ck('DLF_FRESH_PROJECTION_PASSES',r.returncode==0,r.stdout[-300:])
  # upstream drift
  f=d/'authoring/information_object_catalog.yaml'; f.write_text(f.read_text()+'\n# drift\n')
  r=subprocess.run([sys.executable,str(val),str(d)],capture_output=True,text=True)
  ck('DLF_UPSTREAM_DRIFT_FAILS',r.returncode!=0 and 'UPSTREAM_STALE' in r.stdout,r.stdout[-400:])
  # restore and rematerialize, then source drift
  shutil.copy2(R/'authoring/information_object_catalog.yaml',f)
  subprocess.run([sys.executable,str(mat),str(d)],capture_output=True,text=True)
  sf=d/'source/program.ordo.yaml'; sf.write_text(sf.read_text()+'\n# direct graph edit\n')
  r=subprocess.run([sys.executable,str(val),str(d)],capture_output=True,text=True)
  ck('DLF_DIRECT_SOURCE_DRIFT_FAILS',r.returncode!=0 and 'DOWNSTREAM_DIRECT_EDIT' in r.stdout,r.stdout[-400:])
else:
 for x in ['DLF_EDITOR_INTERMEDIATE_MATERIALIZES','DLF_LINEAGE_MATERIALIZES','DLF_FRESH_PROJECTION_PASSES','DLF_UPSTREAM_DRIFT_FAILS','DLF_DIRECT_SOURCE_DRIFT_FAILS']: ck(x,False)
out={'schema_version':'1.0','suite':'data_layer_first_hard_architecture','passed':sum(x['status']=='PASS' for x in res),'failed':sum(x['status']=='FAIL' for x in res),'tests':res}
print(json.dumps(out,ensure_ascii=False,indent=2)); sys.exit(0 if out['failed']==0 else 1)
