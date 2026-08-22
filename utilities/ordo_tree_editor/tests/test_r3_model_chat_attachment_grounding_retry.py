import importlib.util, tempfile
from pathlib import Path

spec=importlib.util.spec_from_file_location('editor_service_attachment_retry',Path('editor_service.py'))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

with tempfile.TemporaryDirectory() as td:
    root=Path(td)
    (root/'uploads').mkdir(); (root/'extracted'/'SECOND').mkdir(parents=True); (root/'generated').mkdir(); (root/'tmp').mkdir()
    (root/'uploads'/'SECOND.zip').write_bytes(b'zip')
    (root/'extracted'/'SECOND'/'source.md').write_text('payload',encoding='utf-8')
    history=m._ModelChatHistory([],current_attachments=[{
        'filename':'SECOND.zip','media_type':'application/zip','size_bytes':3,
        'workspace_path':'uploads/SECOND.zip','extracted_to':'extracted/SECOND'
    }])
    calls=[]
    def fake_provider(credentials,system,context):
        calls.append((system,context))
        if len(calls)==1:
            return {},{},'{"type":"final","message":"Please upload the file."}',{}
        if len(calls)==2:
            # Reproduce the .149 live failure: provider ignores deterministic
            # grounding and repeats the false final.
            assert context.get('attachment_grounding')
            assert context.get('attachment_contract',{}).get('final_allowed') is False
            return {},{},'{"type":"final","message":"The documents are not attached."}',{}
        if len(calls)==3:
            contract=context.get('attachment_contract') or {}
            assert contract.get('rejected_final_count')==2
            assert 'workspace.list/search/read/stat' in contract.get('required_next_action','')
            return {},{},'{"type":"tool","tool":{"name":"workspace.list","arguments":{"path":"extracted/SECOND"}}}',{}
        contract=context.get('attachment_contract') or {}
        assert contract.get('model_inspection_satisfied') is True
        assert contract.get('final_allowed') is True
        return {},{},'{"type":"final","message":"Attachment is present; proceeding."}',{}
    m._provider_api_call=fake_provider
    answer,trace,usage,activities=m._model_chat_agent_loop(
        {'model':'x'},root,'use the attached file',history,max_iterations=6
    )
    assert answer=='Attachment is present; proceeding.'
    assert len(calls)==4
    guards=[x.get('runtime_guard') for x in trace if isinstance(x,dict) and x.get('runtime_guard')]
    assert len(guards)==2 and guards[-1]['rejection_count']==2
    assert any(a.get('label')=='Grounding attached file' for a in activities)
    assert any(a.get('label')=='Attached file grounded' for a in activities)
    assert any(a.get('name')=='workspace.list' and a.get('label')=='Inspecting workspace files' for a in activities)
print('PASS repeated false finals are rejected until model inspects current attachment')
