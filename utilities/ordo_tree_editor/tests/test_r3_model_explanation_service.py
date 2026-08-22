import copy
import editor_service as es

def _package():
    return {'id':'p1','source':{'nodes':[{'id':'N1','purpose':'Do something','validator':'validators/check.py'}],'gates':[]},'resources':{'pkg/validators/check.py':'def validate(x):\n    return bool(x)\n'},'semantic_plan':{'interaction_contract':{'locale':'uk-UA','model_output_language':'uk'},'elements':{'N1':{'id':'N1','kind':'model_node'}}}}

def test_node_explanation_is_read_only_and_uses_playbook_language(monkeypatch):
    old=copy.deepcopy(es.PLAYBOOK_PACKAGE); olds=copy.deepcopy(es.PLAYBOOK_PACKAGES); oldsess=copy.deepcopy(es.LIVE_SESSIONS)
    try:
      pkg=_package(); es.PLAYBOOK_PACKAGE.clear(); es.PLAYBOOK_PACKAGE.update(pkg); es.PLAYBOOK_PACKAGES.clear(); es.PLAYBOOK_PACKAGES['p1']=pkg
      es.LIVE_SESSIONS['s']={'provider':'custom','base_url':'http://local/v1','model':'m','structured_output_mode':'json_object'}
      monkeypatch.setattr(es,'_provider_models',lambda *a,**k:['m'])
      seen={}
      def fake(credentials,system,context):
        seen['system']=system; seen['context']=context
        return {},{},'{"explanation":"Пояснення вузла"}',{'input_tokens':1,'output_tokens':2,'total_tokens':3,'cached_tokens':0,'reasoning_tokens':0}
      monkeypatch.setattr(es,'_provider_api_call',fake)
      before=copy.deepcopy(es.PLAYBOOK_PACKAGE)
      out=es._model_explanation({'package_id':'p1','session_id':'s','kind':'node','node_id':'N1'})
      assert out['explanation']=='Пояснення вузла'
      assert 'locale=uk-UA' in seen['system'] and seen['context']['node_id']=='N1'
      assert es.PLAYBOOK_PACKAGE==before
    finally:
      es.PLAYBOOK_PACKAGE.clear(); es.PLAYBOOK_PACKAGE.update(old); es.PLAYBOOK_PACKAGES.clear(); es.PLAYBOOK_PACKAGES.update(olds); es.LIVE_SESSIONS.clear(); es.LIVE_SESSIONS.update(oldsess)

def test_python_resource_explanation_receives_script_text(monkeypatch):
    old=copy.deepcopy(es.PLAYBOOK_PACKAGE); olds=copy.deepcopy(es.PLAYBOOK_PACKAGES); oldsess=copy.deepcopy(es.LIVE_SESSIONS)
    try:
      pkg=_package(); es.PLAYBOOK_PACKAGE.clear(); es.PLAYBOOK_PACKAGE.update(pkg); es.PLAYBOOK_PACKAGES.clear(); es.PLAYBOOK_PACKAGES['p1']=pkg
      es.LIVE_SESSIONS['s']={'provider':'custom','base_url':'http://local/v1','model':'m','structured_output_mode':'json_object'}
      monkeypatch.setattr(es,'_provider_models',lambda *a,**k:['m'])
      seen={}
      def fake(c,system,ctx):
        seen['ctx']=ctx
        return {},{},'{"explanation":"Перевіряє значення"}',{'input_tokens':1,'output_tokens':1,'total_tokens':2,'cached_tokens':0,'reasoning_tokens':0}
      monkeypatch.setattr(es,'_provider_api_call',fake)
      out=es._model_explanation({'package_id':'p1','session_id':'s','kind':'python_resource','resource_path':'validators/check.py'})
      assert out['explanation']=='Перевіряє значення'
      assert 'def validate' in seen['ctx']['python_source']
    finally:
      es.PLAYBOOK_PACKAGE.clear(); es.PLAYBOOK_PACKAGE.update(old); es.PLAYBOOK_PACKAGES.clear(); es.PLAYBOOK_PACKAGES.update(olds); es.LIVE_SESSIONS.clear(); es.LIVE_SESSIONS.update(oldsess)
