#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, zipfile
from pathlib import Path
import yaml

class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

def yload(path: Path):
    value=yaml.safe_load(path.read_text(encoding='utf-8'))
    if not isinstance(value,dict):
        raise ValueError(f'{path} must contain a YAML mapping')
    return value

def ywrite(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    text=yaml.dump(value, Dumper=NoAliasDumper, sort_keys=False, allow_unicode=True, width=110)
    path.write_text(text, encoding='utf-8')

def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def label_from_id(identifier: str):
    return identifier.replace('_',' ').strip().title()

def build_variable_catalog(root: Path):
    src=yload(root/'authoring/information_object_catalog.yaml')
    variables=[]
    for obj in src.get('objects') or []:
        if not isinstance(obj,dict) or not obj.get('id'): continue
        vc=obj.get('value_contract') or {}
        lc=obj.get('lifecycle') or {}
        required=bool(vc.get('required'))
        row={
            'id': str(obj['id']),
            'label': str(obj.get('label') or label_from_id(str(obj['id']))),
            'definition_status': 'canonical_authoring_object',
            'section': str(obj.get('group_id') or 'ungrouped'),
            'data_type': str(vc.get('type') or obj.get('kind') or 'unknown'),
            'cardinality': str(vc.get('cardinality') or 'one'),
            'nullable': not required,
            'allowed_value_states': list(vc.get('value_states') or []),
            'allowed_validation_states': list(lc.get('validation_states') or []),
            'origin_modes': list(obj.get('origins') or []),
            'creation_policy': {
                'binding_status': 'bound' if obj.get('origins') else 'unbound',
                'may_be_system_inferred': any(x in {'model_derivation','deterministic_derivation','source_material'} for x in (obj.get('origins') or [])),
                'may_be_analyst_provided': 'human_input' in (obj.get('origins') or []),
            },
            'mutation_policy': {
                'mutation_invalidates_validation': bool(lc.get('invalidate_on_change', True)),
                'required_post_mutation_state': 'stale' if lc.get('invalidate_on_change', True) else 'unchanged',
            },
            'validation': {'required_gates': []},
            'provenance_required': bool(obj.get('provenance_required', False)),
            'group_id': obj.get('group_id'),
            'source_information_kind': obj.get('kind'),
            'source_authoring_object': obj,
        }
        variables.append(row)
    return {
        'schema_version':'1.0',
        'catalog_id':'vibe_arf_self_variable_catalog',
        'revision': yload(root/'ordo.yml').get('version') if (root/'ordo.yml').exists() else None,
        'status':'generated_projection',
        'purpose':'Published mini-passports for Vibe self-hosted authoring information objects. Generated from authoring/information_object_catalog.yaml.',
        'state_model':{
            'value_state':['unset','value','unknown','not_applicable'],
            'validation_state':['draft','validated','approved','stale'],
            'rule':'value_state and validation_state are independent; canonical upstream remains authoring/information_object_catalog.yaml.'
        },
        'variables':variables,
    }

def build_group_catalog(root: Path):
    src=yload(root/'authoring/information_group_catalog.yaml')
    groups=[]
    for idx,g in enumerate(src.get('groups') or [],1):
        if not isinstance(g,dict) or not g.get('id'): continue
        display=g.get('display') or {}
        interaction=g.get('interaction_policy') or {}
        validation=g.get('validation') or {}
        gates=list(validation.get('gate_ids') or [])
        groups.append({
            'id':str(g['id']),
            'label':str(display.get('title') or label_from_id(str(g['id']))),
            'order':idx,
            'purpose':str(display.get('description') or ''),
            'graph_sections':[str(g['id'])],
            'member_variables':list(g.get('members') or []),
            'shared_gate_id':gates[0] if len(gates)==1 else None,
            'shared_gate_ids':gates,
            'analyst_interaction_policy':{
                'present_as_logical_bundle':True,
                'allow_progressive_disclosure':bool(interaction.get('progressive',True)),
                'proposal_first_when_derivable':bool(interaction.get('proposal_first_when_derivable',True)),
            },
            'validation_policy':{
                'gate_scope':'group',
                'mutation_of_any_member_invalidates_group_gate':True,
            },
            'display':display,
            'source_authoring_group':g,
        })
    return {
        'schema_version':'1.0',
        'catalog_id':'vibe_arf_self_variable_group_catalog',
        'revision': yload(root/'ordo.yml').get('version') if (root/'ordo.yml').exists() else None,
        'purpose':'Published semantic-group passports generated from the Vibe self-hosted AIM.',
        'groups':groups,
    }

def build_artifact_catalog(root: Path):
    src=yload(root/'authoring/artifact_catalog.yaml')
    artifacts=[]
    for a in src.get('artifacts') or []:
        if not isinstance(a,dict) or not a.get('id'): continue
        artifacts.append({
            'id':str(a['id']),
            'filename':a.get('filename'),
            'title':str(a.get('title') or label_from_id(str(a['id']))),
            'required':bool((a.get('materialization') or {}).get('required',False)),
            'format':a.get('kind'),
            'role':a.get('kind'),
            'source_information_objects':list(a.get('inputs') or []),
            'verification_required':bool((a.get('verification') or {}).get('required',False)),
            'lifecycle':a.get('lifecycle'),
            'source_authoring_artifact':a,
        })
    return {
        'schema_version':'1.0',
        'catalog_id':'vibe_arf_self_artifact_catalog',
        'revision': yload(root/'ordo.yml').get('version') if (root/'ordo.yml').exists() else None,
        'purpose':'Published artifact passports generated from authoring/artifact_catalog.yaml.',
        'artifacts':artifacts,
    }

def build_graph(root: Path):
    graph=yload(root/'authoring/information_flow_graph.yaml')
    objects=yload(root/'authoring/information_object_catalog.yaml')
    groups=yload(root/'authoring/information_group_catalog.yaml')
    artifacts=yload(root/'authoring/artifact_catalog.yaml')
    obj_by={str(x['id']):x for x in objects.get('objects') or [] if isinstance(x,dict) and x.get('id')}
    art_by={str(x['id']):x for x in artifacts.get('artifacts') or [] if isinstance(x,dict) and x.get('id')}
    gate_to_group={}
    sections=[{'id':'SOURCES','label':'Sources','order':0}]
    for idx,g in enumerate(groups.get('groups') or [],1):
        if not isinstance(g,dict) or not g.get('id'): continue
        disp=g.get('display') or {}
        sections.append({'id':str(g['id']),'label':str(disp.get('title') or g['id']),'order':idx})
        for gid in (g.get('validation') or {}).get('gate_ids') or []:
            gate_to_group[str(gid)]=str(g['id'])
    sections.append({'id':'ARTIFACTS','label':'Artifacts / delivery','order':len(sections)+1})
    nodes=[]; logical_gates=[]
    for raw in graph.get('nodes') or []:
        if not isinstance(raw,dict) or not raw.get('id'): continue
        nid=str(raw['id']); kind=str(raw.get('kind') or '')
        row={'id':nid,'label':str(raw.get('label') or label_from_id(nid)),'source_kind':kind}
        if kind=='information':
            row['type']='variable'; row['variable_ref']=nid; row['section']=str((obj_by.get(nid) or {}).get('group_id') or 'G_INFORMATION_MODEL')
        elif kind=='artifact':
            row['type']='artifact'; row['artifact_ref']=nid; row['section']='ARTIFACTS'
        elif kind in {'validation_gate','authority_decision'}:
            row['type']='gate_fragment'; row['section']=gate_to_group.get(nid,'G_INFORMATION_MODEL')
            logical_gates.append({'id':nid,'label':row['label'],'fragments':[nid],'authority_kind':kind})
        elif kind=='source':
            row['type']='analyst_input' if nid=='S_ANALYST' else 'source'; row['section']='SOURCES'
        else:
            row['type']=kind or 'information'; row['section']='G_INFORMATION_MODEL'
        nodes.append(row)
    edges=[]
    for e in graph.get('edges') or []:
        if not isinstance(e,dict): continue
        edges.append({'from':str(e.get('from') or ''),'to':str(e.get('to') or ''),'type':str(e.get('type') or 'relation')})
    return {
        'schema_version':'1.0',
        'model_id':'vibe_arf_self_information_dependency_graph',
        'revision': yload(root/'ordo.yml').get('version') if (root/'ordo.yml').exists() else None,
        'status':'generated_publication_projection',
        'purpose':'Editor-consumable authoring data-flow projection generated deterministically from Vibe authoring/information_flow_graph.yaml.',
        'conventions':{
            'canonical_upstream':'authoring/information_flow_graph.yaml',
            'mutation_rule':'Never hand-edit this publication graph; modify canonical AIM under authoring/ and regenerate.',
            'information_object_rule':'Published variable nodes are views of canonical authoring information objects.',
            'artifact_node_rule':'Artifacts are first-class information-flow nodes.',
            'publication_semantics':'authoring_adapter_only',
        },
        'entry_nodes':list(graph.get('entry_nodes') or []),
        'terminal_nodes':list(graph.get('terminal_nodes') or []),
        'sections':sections,
        'nodes':nodes,
        'edges':edges,
        'gates':logical_gates,
    }

def build_projection(root: Path):
    src=yload(root/'authoring/ordo_projection.yaml')
    return {
        'schema_version':'1.0',
        'projection_id':'vibe_arf_self_playbook_projection',
        'revision': yload(root/'ordo.yml').get('version') if (root/'ordo.yml').exists() else None,
        'status':'generated_projection',
        'canonical_upstream':'authoring/ordo_projection.yaml',
        'source_projection_sha256':sha256(root/'authoring/ordo_projection.yaml'),
        'information_bindings':src.get('information_bindings') or [],
        'group_bindings':src.get('group_bindings') or [],
        'execution_bindings':src.get('execution_bindings') or [],
    }

def build_bundle(root: Path):
    version=yload(root/'ordo.yml').get('version') if (root/'ordo.yml').exists() else 'unknown'
    upstream_names=['information_object_catalog.yaml','information_group_catalog.yaml','information_flow_graph.yaml','artifact_catalog.yaml','ordo_projection.yaml']
    return {
        'schema_version':'1.0',
        'model_bundle_id':'vibe_arf_self_hosted_information_model',
        'revision':version,
        'generated_from':'authoring/',
        'publication_semantics':'authoring_adapter_only',
        'canonical_sources':{
            'graph':'information_dependency_graph.yaml',
            'variable_catalog':'variable_catalog.yaml',
            'variable_group_catalog':'variable_group_catalog.yaml',
            'playbook_projection':'playbook_projection.yaml',
            'artifact_catalog':'artifact_catalog.yaml',
        },
        'extended_canonical_upstream':{
            'interaction_projection':'../authoring/interaction_projection.yaml',
            'review_bundle_catalog':'../authoring/review_bundle_catalog.yaml',
            'proposal_canonicalization':'../authoring/proposal_canonicalization.yaml',
            'approval_ledger':'../authoring/approval_ledger.yaml',
            'scenario_matrix':'../authoring/scenario_matrix.yaml',
        },
        'upstream_sha256':{name:sha256(root/'authoring'/name) for name in upstream_names},
        'mutation_rule':'Edit canonical authoring YAML under authoring/, validate AIM, then regenerate this publication bundle. Never hand-edit generated design files.',
        'architecture_rule':'The Vibe self-hosted AIM under authoring/ is the single authoring source model. design/ is a deterministic Editor-facing publication projection only.',
        'verification':{
            'authoring_model_validator':'tools/validate_authoring_information_model.py',
            'projection_validator':'tools/validate_information_projection.py',
            'publication_validator':'tools/validate_self_data_flow_publication.py',
        },
        'generated_artifacts':['DATA_FLOW_PACKAGE.zip'],
    }

def deterministic_zip(design: Path, names: list[str]):
    target=design/'DATA_FLOW_PACKAGE.zip'
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted(names):
            data=(design/name).read_bytes()
            info=zipfile.ZipInfo(name)
            info.date_time=(2020,1,1,0,0,0)
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o100644 & 0xFFFF)<<16
            z.writestr(info,data)
    return target

def publish(root: Path):
    design=root/'design'; design.mkdir(parents=True,exist_ok=True)
    outputs={
        'variable_catalog.yaml':build_variable_catalog(root),
        'variable_group_catalog.yaml':build_group_catalog(root),
        'artifact_catalog.yaml':build_artifact_catalog(root),
        'information_dependency_graph.yaml':build_graph(root),
        'playbook_projection.yaml':build_projection(root),
    }
    for name,data in outputs.items(): ywrite(design/name,data)
    ywrite(design/'MODEL_BUNDLE.yaml',build_bundle(root))
    names=['MODEL_BUNDLE.yaml',*outputs.keys()]
    target=deterministic_zip(design,names)
    return {'status':'passed','design_dir':str(design),'data_flow_package':str(target),'files':names,'sha256':sha256(target)}

def main():
    ap=argparse.ArgumentParser(description='Publish an Editor-facing authoring data-flow bundle from a canonical Vibe AIM.')
    ap.add_argument('root',nargs='?',default='.')
    ap.add_argument('--json',action='store_true')
    args=ap.parse_args(); result=publish(Path(args.root).resolve())
    print(json.dumps(result,indent=2,sort_keys=True) if args.json else f"PASS published {result['data_flow_package']} {result['sha256']}")
    return 0
if __name__=='__main__': raise SystemExit(main())
