import copy, importlib.util
from pathlib import Path
P=Path(__file__).parents[2]/'tools/apf_semantic_equivalence.py'
s=importlib.util.spec_from_file_location('eq',P); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
BASE={"ordo_version":"0.11","package":"x","compiled_at":"a","security":{"canary_secret":"a"},"ops":[{"op":"NODE.DEF","id":"x.N","question":"q"},{"op":"NODE.DEF","id":"x.C","question":"secret","canary":True}]}
def test_volatile_data_ignored():
 b=copy.deepcopy(BASE); b['compiled_at']='b'; b['security']={'canary_secret':'b'}; b['ops'][1]['question']='other'
 assert m.compare(BASE,b)['equivalent']
def test_changed_operation_fails():
 b=copy.deepcopy(BASE); b['ops'][0]['question']='changed'
 r=m.compare(BASE,b); assert not r['equivalent']; assert r['changed_ops']==['NODE.DEF::x.N']
def test_order_ignored():
 b=copy.deepcopy(BASE); b['ops'].reverse(); assert m.compare(BASE,b)['equivalent']
