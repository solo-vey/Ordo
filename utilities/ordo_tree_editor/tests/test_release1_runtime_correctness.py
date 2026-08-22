from __future__ import annotations
import importlib.util, json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import alpha20_runtime as rt
import release1_runtime as r1

ROW={'type':'object','additionalProperties':False,'required':['id'],'properties':{'id':{'type':'string'}}}
VS={'catalog.rows':{'type':'array','items':ROW}}

def test_operation_aware_collection_schema():
    good={'base_revision':0,'operations':[{'op':'append','path':'catalog.rows','value':{'id':'x'},'basis':'generated'}]}
    bad={'base_revision':0,'operations':[{'op':'append','path':'catalog.rows','value':[{'id':'x'}],'basis':'generated'}]}
    assert rt.validate_state_patch(good,allowed_paths=['catalog.rows'],current_revision=0,value_schemas=VS)['valid']
    assert not rt.validate_state_patch(bad,allowed_paths=['catalog.rows'],current_revision=0,value_schemas=VS)['valid']
    mg={'base_revision':0,'operations':[{'op':'merge_row','path':'catalog.rows','value':{'id':'x'},'basis':'generated','row_key':'id','row_match':'x'}]}
    mb={'base_revision':0,'operations':[{'op':'merge_row','path':'catalog.rows','value':[{'id':'x'}],'basis':'generated','row_key':'id','row_match':'x'}]}
    assert rt.validate_state_patch(mg,allowed_paths=['catalog.rows'],current_revision=0,value_schemas=VS)['valid']
    assert not rt.validate_state_patch(mb,allowed_paths=['catalog.rows'],current_revision=0,value_schemas=VS)['valid']

def test_legacy_normalizer():
    state={'catalog':{'rows':[[{'id':'a'}],[{'id':'b'},{'id':'c'}]]}}
    normalized, report=r1.normalize_legacy_collections(state,VS)
    assert report['status']=='PASS'
    assert normalized['catalog']['rows']==[{'id':'a'},{'id':'b'},{'id':'c'}]
    assert r1.scan_collection_shapes(normalized,VS)['status']=='PASS'

def test_touched_path_commit_invariant():
    state={'catalog':{'rows':[{'id':'a'}]},'unrelated':{'rows':[[{'x':1}]]}}
    patch={'base_revision':0,'operations':[{'op':'append','path':'catalog.rows','value':{'id':'b'},'basis':'generated'}]}
    new, commit=rt.apply_state_patch_atomic(state,patch,allowed_paths=['catalog.rows'],current_revision=0,value_schemas=VS)
    assert commit['committed']
    assert new['unrelated']['rows']==[[{'x':1}]]
