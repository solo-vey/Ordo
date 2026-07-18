from pathlib import Path
import json
import yaml

from ordo.template_tooling import review_template_artifact, render_template


def write_contract(tmp_path: Path, *, mode='standard', required=None, forbidden=None):
    src = tmp_path/'template.md.tmpl'
    src.write_text('# Summary\n{{summary}}\n\n# Findings\n{{findings}}\n\n# Decision\n{{decision}}\n', encoding='utf-8')
    contract = {
        'template_id':'review.sample','version':'1.0.0','render_mode':'deterministic',
        'template_ref':src.name,
        'input_schema':{'required':['summary','findings','decision'],'properties':{}},
        'output_contract':{'format':'markdown','filename':'artifact.md','required_sections': required or ['Summary','Findings','Decision']},
        'review_profile':{'mode':mode,'forbidden_content': forbidden or []},
        'compatibility':{'ordo':'>=0.12.0'},
    }
    p=tmp_path/'contract.yaml'; p.write_text(yaml.safe_dump(contract,sort_keys=False),encoding='utf-8')
    inp=tmp_path/'input.yaml'; inp.write_text(yaml.safe_dump({'summary':'ok','findings':'none','decision':'PASS'}),encoding='utf-8')
    return p, inp


def test_standard_review_passes(tmp_path):
    contract, inp = write_contract(tmp_path)
    out=tmp_path/'out'; render=render_template(contract,inp,out)
    report=review_template_artifact(contract,out/'artifact.md',render_evidence_path=render['evidence_path'])
    assert report['status']=='passed'
    assert report['decision']=='approve'
    assert report['schema_version']=='ordo.template.review_evidence.v1'


def test_missing_required_section_fails(tmp_path):
    contract, inp = write_contract(tmp_path, required=['Summary','Missing'])
    out=tmp_path/'out'; render=render_template(contract,inp,out)
    report=review_template_artifact(contract,out/'artifact.md',render_evidence_path=render['evidence_path'])
    assert report['status']=='failed'
    assert any(x['code']=='TEMPLATE_REVIEW_REQUIRED_SECTION_MISSING' for x in report['findings'])


def test_forbidden_content_fails(tmp_path):
    contract, inp = write_contract(tmp_path, forbidden=['PASS'])
    out=tmp_path/'out'; render=render_template(contract,inp,out)
    report=review_template_artifact(contract,out/'artifact.md',render_evidence_path=render['evidence_path'])
    assert report['status']=='failed'
    assert any(x['code']=='TEMPLATE_REVIEW_FORBIDDEN_CONTENT' for x in report['findings'])


def test_strict_requires_render_evidence(tmp_path):
    contract, inp = write_contract(tmp_path, mode='strict')
    out=tmp_path/'out'; render_template(contract,inp,out)
    report=review_template_artifact(contract,out/'artifact.md')
    assert report['status']=='failed'
    assert any(x['code']=='TEMPLATE_REVIEW_RENDER_EVIDENCE_REQUIRED' for x in report['findings'])


def test_provenance_mismatch_fails(tmp_path):
    contract, inp = write_contract(tmp_path)
    out=tmp_path/'out'; render=render_template(contract,inp,out)
    ev=Path(render['evidence_path'])
    data=json.loads(ev.read_text()); data['provenance']['contract_sha256']='0'*64; ev.write_text(json.dumps(data))
    report=review_template_artifact(contract,out/'artifact.md',render_evidence_path=ev)
    assert report['status']=='failed'
    assert any(x['code']=='TEMPLATE_REVIEW_CONTRACT_PROVENANCE_MISMATCH' for x in report['findings'])
