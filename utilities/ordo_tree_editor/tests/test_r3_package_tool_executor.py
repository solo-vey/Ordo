from pathlib import Path
import json, zipfile

from utilities.ordo_tree_editor import editor_service as es
from utilities.ordo_tree_editor.ordo_yaml_semantics import classify


def _record():
    return {
        'id':'N_TOOL',
        'question':'Run `python tools/check.py <actual state.input_path> --contract contracts/c.json --output reports/out.json` as deterministic helper. Do not imitate result.',
        'answer_type':'structured_record',
        'node_context':{'allowed_tools':['tools/check.py'],'knowledge_refs':['contracts/c.json'],'output_contract':{'state_diff':'required','next_node':'explicit'}},
        'on_answer':{'update_state':{'status':'$answer.status','report_ref':'$answer.report_ref'},'next':'G_NEXT'},
    }


def test_classifier_prefers_package_tool_over_human_interaction():
    c=classify(_record(),False)
    assert c['kind']=='deterministic_operation'
    assert c['runtime_executor']=='package_tool'
    assert c['requires_analyst'] is False
    assert c['deterministic'] is True


def test_file_ref_uses_single_stored_attachment_path():
    rec={'answer_type':'file_ref'}
    assert es._effective_file_ref_answer(rec,'node','respond','',[{'stored_path':'analyst_attachments/s/a.json'}]) == 'analyst_attachments/s/a.json'
    assert es._effective_file_ref_answer(rec,'node','respond','explicit.json',[{'stored_path':'ignored'}]) == 'explicit.json'


def test_package_tool_executes_machine_result_and_commits(tmp_path):
    package_root=tmp_path/'pkg'; (package_root/'tools').mkdir(parents=True); (package_root/'contracts').mkdir()
    (package_root/'contracts/c.json').write_text('{}',encoding='utf-8')
    (package_root/'tools/check.py').write_text('''import argparse,json\nfrom pathlib import Path\np=argparse.ArgumentParser();p.add_argument("input");p.add_argument("--contract");p.add_argument("--output");a=p.parse_args();r={"status":"VALID"};Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(r));print(json.dumps(r))\n''',encoding='utf-8')
    (package_root/'program.ordo.yaml').write_text('nodes: []\n',encoding='utf-8')
    zip_path=tmp_path/'p.zip'
    with zipfile.ZipFile(zip_path,'w') as z:
        for p in package_root.rglob('*'):
            if p.is_file(): z.write(p,p.relative_to(package_root).as_posix())
    raw=zip_path.read_bytes()
    package={'id':'pkgtest','raw_zip':raw,'source':{},'semantic_plan':{}}
    pt=es._ACTIVE_PLAYBOOK_PACKAGE.set(package); rt=es._ACTIVE_RUN_CONTEXT.set({'package_id':'pkgtest','session_id':'s','run_id':'r'})
    try:
        ws=es._runtime_workspace(); inp=ws/'analyst_attachments/s/input.json'; inp.parent.mkdir(parents=True,exist_ok=True); inp.write_text('{}')
        rec=_record(); routes=[{'key':'next','target':'G_NEXT'}]
        out=es._execute_package_tool({},rec,'N_TOOL','node','enter',{'input_path':str(inp.relative_to(ws))},routes,0)
        assert out['await_analyst'] is False
        assert out['next_id']=='G_NEXT'
        assert out['state']['status']=='VALID'
        assert out['state']['report_ref']=='reports/out.json'
        assert out['debug']['runtime']['runtime_executor']=='package_tool'
        assert (ws/'package_tool_outputs/reports/out.json').is_file()
    finally:
        es._ACTIVE_RUN_CONTEXT.reset(rt); es._ACTIVE_PLAYBOOK_PACKAGE.reset(pt)


def test_live_dispatch_does_not_reclassify_package_tool_as_human(tmp_path, monkeypatch):
    root=tmp_path/'pkg2'; (root/'tools').mkdir(parents=True); (root/'contracts').mkdir()
    (root/'contracts/c.json').write_text('{}')
    (root/'tools/check.py').write_text('import argparse,json\nfrom pathlib import Path\np=argparse.ArgumentParser();p.add_argument("input");p.add_argument("--contract");p.add_argument("--output");a=p.parse_args();Path(a.output).parent.mkdir(parents=True,exist_ok=True);print(json.dumps({"status":"VALID"}))\n')
    source={'graph_contract':{'entry_node':'N_TOOL'},'state':{'schema':{'input_path':None,'status':None,'report_ref':None}},'nodes':[_record()], 'gates':[]}
    import yaml
    (root/'program.ordo.yaml').write_text(yaml.safe_dump(source,sort_keys=False),encoding='utf-8')
    buf=tmp_path/'pkg2.zip'
    with zipfile.ZipFile(buf,'w') as z:
        for f in root.rglob('*'):
            if f.is_file(): z.write(f,f.relative_to(root).as_posix())
    # Use a minimal in-memory package with a compiled semantic element.
    package={'id':'livepkg','raw_zip':buf.read_bytes(),'source':source,'semantic_plan':{'elements':{'N_TOOL':{'execution_traits':{'runtime_executor':'package_tool','model_executed':False,'model_executed_phases':[]},'state_contract':{}}}}}
    es.PLAYBOOK_PACKAGES['livepkg']=package
    monkeypatch.setattr(es,'_live_credentials',lambda payload:{'provider':'test','model':'none','base_url':'local'})
    pt=es._ACTIVE_PLAYBOOK_PACKAGE.set(package); rt=es._ACTIVE_RUN_CONTEXT.set({'package_id':'livepkg','session_id':'s','run_id':'r'})
    try:
        ws=es._runtime_workspace(); inp=ws/'analyst_attachments/s/input.json'; inp.parent.mkdir(parents=True,exist_ok=True); inp.write_text('{}')
        rel=str(inp.relative_to(ws))
    finally:
        es._ACTIVE_RUN_CONTEXT.reset(rt); es._ACTIVE_PLAYBOOK_PACKAGE.reset(pt)
    out=es._call_openai_live({'package_id':'livepkg','session_id':'s','run_id':'r','source':source,'current_id':'N_TOOL','phase':'enter','state':{'input_path':rel},'state_revision':0,'history':[]})
    assert out['await_analyst'] is False
    assert out['debug']['runtime']['runtime_executor']=='package_tool'
