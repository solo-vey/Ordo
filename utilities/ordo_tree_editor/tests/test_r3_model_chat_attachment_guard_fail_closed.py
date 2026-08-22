import importlib.util, tempfile
from pathlib import Path

spec=importlib.util.spec_from_file_location('editor_service_attachment_fail_closed',Path('editor_service.py'))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

with tempfile.TemporaryDirectory() as td:
    root=Path(td)
    (root/'uploads').mkdir(); (root/'extracted'/'A').mkdir(parents=True); (root/'generated').mkdir(); (root/'tmp').mkdir()
    (root/'uploads'/'A.zip').write_bytes(b'zip')
    (root/'extracted'/'A'/'doc.md').write_text('payload',encoding='utf-8')
    history=m._ModelChatHistory([],current_attachments=[{
        'filename':'A.zip','workspace_path':'uploads/A.zip','extracted_to':'extracted/A'
    }])
    m._provider_api_call=lambda *args,**kwargs: ({},{},'{"type":"final","message":"Upload it again."}',{})
    answer,trace,usage,activities=m._model_chat_agent_loop({'model':'x'},root,'process it',history,max_iterations=3)
    assert 'A.zip' in answer
    assert 'did not inspect it' in answer
    assert 'does not need to be uploaded again' in answer
    assert sum(1 for x in trace if isinstance(x,dict) and x.get('runtime_guard'))==3
print('PASS attachment guard fails closed instead of surfacing false re-upload claim')
