import io, json, zipfile, hashlib, sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import editor_service as es

def _zip_fixture():
    ledger=[
      {'run_id':'r1','sequence':1,'element_id':'N_A','element_kind':'node','started_at':'2026-01-01T00:00:00+00:00','finished_at':'2026-01-01T00:00:01+00:00','duration_ms':1000,'route':'human','to_node':'N_A','status':'WAITING_FOR_HUMAN','ledger_sha256':'h1'},
      {'run_id':'r1','sequence':2,'element_id':'N_A','element_kind':'node','started_at':'2026-01-01T00:00:02+00:00','finished_at':'2026-01-01T00:00:03+00:00','duration_ms':1000,'route':'next','to_node':'N_B','status':'PASS','ledger_sha256':'h2'},
    ]
    trace=[
      {'sequence':1,'event_type':'MODEL_ACTION','execution_sequence':1,'element_id':'N_A','action_type':'HUMAN_INPUT_REQUEST','action_summary':'ask','changed_paths':[],'decision_ids':[],'state_patch':{},'structured_result':{},'status':'WAITING_FOR_HUMAN'},
      {'sequence':2,'event_type':'ASSISTANT_MESSAGE','element_id':'N_A','text':'Question','visibility':'USER_VISIBLE','timestamp':'2026-01-01T00:00:01+00:00'},
      {'sequence':3,'event_type':'ANALYST_MESSAGE','element_id':'N_A','text':'Answer','visibility':'USER_VISIBLE','timestamp':'2026-01-01T00:00:02.1+00:00'},
      {'sequence':4,'event_type':'MODEL_ACTION','execution_sequence':2,'element_id':'N_A','action_type':'STATE_TRANSITION','action_summary':'apply','changed_paths':['x'],'decision_ids':['D1'],'state_patch':{'x':1},'structured_result':{'ok':True},'status':'PASS'},
    ]
    telemetry=[
      {'sequence':1,'element_id':'N_A','canonical_ledger_sha256':'h1','duration_ms':1100,'token_equivalent_estimate_input':100,'token_equivalent_estimate_output':20,'token_count_source':'RUNTIME_OBSERVABLE_ESTIMATE'},
      {'sequence':2,'element_id':'N_A','canonical_ledger_sha256':'h2','duration_ms':1200,'token_equivalent_estimate_input':200,'token_equivalent_estimate_output':40,'exact_host_input_tokens':222,'exact_host_output_tokens':44,'token_count_source':'HOST_EXACT'},
    ]
    receipts=[{'sequence':1,'canonical_ledger_sha256':'h1','receipt_sha256':'r1','status':'PASS'},{'sequence':2,'canonical_ledger_sha256':'h2','receipt_sha256':'r2','status':'PASS'}]
    filetrace=[{'element_id':'N_A','event':'filesystem_command_observed','started_at':'2026-01-01T00:00:02.2+00:00','command':['cat','a.txt'],'coverage_mode':'FILE_SIZE_ONLY','sum_file_size_bytes_for_read_files':12}]
    artifacts=[{'run_id':'r1','element_id':'N_A','path':'/tmp/out.md','role':'final','bytes':5,'sha256':'x','registered_at':'2026-01-01T00:00:03+00:00'}]
    payloads={
      'debug_handoff/working/evidence/MODEL_EXECUTION_LEDGER.jsonl':'\n'.join(json.dumps(x) for x in ledger)+'\n',
      'debug_handoff/working/evidence/INTERACTION_AND_ACTION_TRACE.jsonl':'\n'.join(json.dumps(x) for x in trace)+'\n',
      'debug_handoff/working/evidence/PER_NODE_TELEMETRY.jsonl':'\n'.join(json.dumps(x) for x in telemetry)+'\n',
      'debug_handoff/working/evidence/EXECUTION_RECEIPTS.jsonl':'\n'.join(json.dumps(x) for x in receipts)+'\n',
      'debug_handoff/working/evidence/DEBUG_FILE_ACCESS_TRACE.jsonl':'\n'.join(json.dumps(x) for x in filetrace)+'\n',
      'debug_handoff/working/evidence/ARTIFACT_LINEAGE.jsonl':'\n'.join(json.dumps(x) for x in artifacts)+'\n',
      'debug_handoff/working/evidence/TIMING_SUMMARY.json':json.dumps({'status':'PASS','run_id':'r1','total_duration_ms':2300}),
      'debug_handoff/working/evidence/TOKEN_USAGE_SUMMARY.json':json.dumps({'status':'PASS','exact_host_tokens':{'input_tokens':222,'output_tokens':44,'rows_with_exact_input':1,'rows_with_exact_output':1},'token_equivalent_estimates':{'input':300,'output':60}}),
      'debug_handoff/working/evidence/PROCESS_QUALITY_REPORT.json':json.dumps({'status':'PASS','canonical_execution_count':2,'telemetry_rows':2}),
      'debug_handoff/working/evidence/ARTIFACT_QUALITY_REPORT.json':json.dumps({'status':'PASS'}),
      'debug_handoff/working/DEBUG_RUN_INDEX.json':json.dumps({'run_id':'r1','status':'COMPLETE','mode':'model'}),
      'debug_handoff/working/artifacts/out.md':'hello',
    }
    manifest={'files':[{'path':k,'sha256':hashlib.sha256(v.encode()).hexdigest()} for k,v in payloads.items()]}
    payloads['debug_handoff/working/DEBUG_BUNDLE_MANIFEST.json']=json.dumps(manifest)
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w') as z:
      for k,v in payloads.items(): z.writestr(k,v)
    return out.getvalue()

def test_canonical_debug_replay_preserves_repeated_executions_and_evidence():
    raw=_zip_fixture(); r=es.parse_replay_package('canonical.zip',raw)
    assert r['format']=='canonical_debug_handoff'
    assert [s['id'] for s in r['steps']]==['N_A','N_A']
    assert [s['execution_sequence'] for s in r['steps']]==[1,2]
    assert any(x['event_type']=='ASSISTANT_MESSAGE' and x['text']=='Question' for x in r['steps'][0]['chronology'])
    assert any(x['event_type']=='ANALYST_MESSAGE' and x['text']=='Answer' for x in r['steps'][1]['chronology'])
    assert r['steps'][1]['model_actions'][0]['changed_paths']==['x']
    assert r['steps'][1]['telemetry']['estimated_input_tokens']==200
    assert r['steps'][1]['telemetry']['exact_host_input_tokens']==222
    assert r['steps'][1]['file_actions'][0]['coverage_class']=='FILE_SIZE_ONLY'
    assert r['steps'][1]['receipt']['receipt_sha256']=='r2'
    assert r['artifact_quality']['status']=='PASS'
    assert r['integrity']['status']=='PASS'
    assert r['summary']['runtime_observable_input_tokens']==300
    assert r['summary']['exact_host_input_tokens']==222
    assert es._replay_auto_answers(r)=={'N_A':['Answer']}

def test_legacy_replay_inputs_are_rejected():
    with pytest.raises(ValueError,match='only canonical debug handoff ZIP'):
      es.parse_replay_package('run_trace.json',b'{}')
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w') as z:z.writestr('run_trace.json','{}')
    with pytest.raises(ValueError,match='Expected canonical'):
      es.parse_replay_package('legacy.zip',out.getvalue())
