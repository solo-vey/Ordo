from pathlib import Path
import yaml
from ordo.template_tooling import diff_template_versions

BASE={
 'template_id':'qa.package','version':'1.0.0','render_mode':'model_rendered',
 'input_schema':{'required':['scope'],'properties':{'scope':{'type':'string'},'notes':{'type':'string'}}},
 'output_contract':{'format':'markdown','required_sections':['Summary']},
 'review_profile':{'mode':'standard'},'compatibility':{'ordo':'>=0.12.0'},
 'model_contract':{'prompt_ref':'prompt.qa.v1','provenance_required':True}
}
def dump(tmp_path,name,data):
 p=tmp_path/name;p.write_text(yaml.safe_dump(data,sort_keys=False));return p

def test_non_breaking_optional_input_allowed(tmp_path):
 old=BASE.copy(); new=yaml.safe_load(yaml.safe_dump(BASE));new['version']='1.1.0';new['input_schema']['properties']['title']={'type':'string'}
 r=diff_template_versions(dump(tmp_path,'o.yaml',old),dump(tmp_path,'n.yaml',new))
 assert r['status']=='passed' and r['summary']['breaking_changes']==0

def test_breaking_change_blocked_without_major_and_migration(tmp_path):
 old=yaml.safe_load(yaml.safe_dump(BASE));new=yaml.safe_load(yaml.safe_dump(BASE));new['version']='1.1.0';new['input_schema']['required'].append('notes')
 r=diff_template_versions(dump(tmp_path,'o.yaml',old),dump(tmp_path,'n.yaml',new))
 assert r['status']=='failed'; assert r['decision']=='block'

def test_breaking_change_allowed_with_major_and_migration(tmp_path):
 old=yaml.safe_load(yaml.safe_dump(BASE));new=yaml.safe_load(yaml.safe_dump(BASE));new['version']='2.0.0';new['render_mode']='hybrid';new['template_ref']='scaffold.md';new['migration']={'required':True,'guide_ref':'MIGRATION_1_TO_2.md'}
 r=diff_template_versions(dump(tmp_path,'o.yaml',old),dump(tmp_path,'n.yaml',new))
 assert r['status']=='passed'; assert r['summary']['breaking_changes']>=1

def test_format_change_is_breaking(tmp_path):
 old=yaml.safe_load(yaml.safe_dump(BASE));new=yaml.safe_load(yaml.safe_dump(BASE));new['version']='2.0.0';new['output_contract']['format']='json';new['migration']={'required':True,'guide_ref':'guide.md'}
 r=diff_template_versions(dump(tmp_path,'o.yaml',old),dump(tmp_path,'n.yaml',new))
 assert any(c['path']=='output_contract.format' and c['breaking'] for c in r['changes'])
