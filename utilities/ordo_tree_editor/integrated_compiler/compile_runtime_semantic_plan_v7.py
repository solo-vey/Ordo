#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json, re
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict, deque
from typing import Any
import yaml

from generated_playbook_profile_adapter import adapt_execution_profile, adapt_artifact_validation_profile
from ordo_yaml_semantics import (
    routes as shared_routes,
    declared_routes as shared_declared_routes,
    declared_writes as shared_declared_writes,
    classify as shared_classify,
    resource_refs as shared_resource_refs,
)

COMPILER_VERSION = 'ordo-runtime-semantic-compiler/0.7.15.7-r3dev-gate-state-contract-analysis'
RELEASE1_APPEND_ONLY_COLLECTION_PATHS={'functional_test_catalog.rows','unit_test_catalog.rows','edge_case_catalog.rows'}
REGION_ELEMENT_BUDGET = 24
FORMAT = 'ordo.runtime_semantic_plan'
FORMAT_VERSION = '1.4-alpha20'
STATE_REF_RE = re.compile(r'(?<![A-Za-z0-9_])(?:state\.|\$state\.)([A-Za-z_][A-Za-z0-9_.]*)')
DOLLAR_REF_RE = re.compile(r'\$([A-Za-z_][A-Za-z0-9_.]*)')
PATHISH_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$')
RUNTIME_TOKENS = ('runtime.', 'runtime_')

INPUT_CONTEXT_CLASSES = {
    'runtime': {
        'current_state','active_node','checkpoints','current_run_evidence','node_path','run_id',
    },
    'interaction': {
        'active_question','analyst_review_comments','accepted_decisions',
    },
    'recovery': {
        'last_validation_feedback','last_failed_gate','last_validation_report','missing_artifact_context',
        'blockers','discrepancies','readiness_status',
    },
    'metadata': {
        'graph_dependency_map','playbook_metadata',
    },
}
INPUT_CONTEXT_INDEX = {name: cls for cls, names in INPUT_CONTEXT_CLASSES.items() for name in names}


def classify_declared_input(path: str, schema_paths: set[str]) -> str | None:
    if path_exists_or_parent(path, schema_paths):
        return 'state'
    root = path.split('.', 1)[0]
    if root in INPUT_CONTEXT_INDEX:
        return INPUT_CONTEXT_INDEX[root]
    if root == 'runtime' or path.startswith('runtime.'):
        return 'runtime'
    return None


def sha256_bytes(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def sha256_file(p: Path) -> str: return sha256_bytes(p.read_bytes())

def walk(v: Any):
    if isinstance(v, dict):
        for k, x in v.items():
            yield k, x
            yield from walk(x)
    elif isinstance(v, list):
        for x in v:
            yield None, x
            yield from walk(x)


def flatten_state_schema(schema: dict) -> list[str]:
    out=[]
    def rec(prefix:str, v:Any):
        if prefix: out.append(prefix)
        if isinstance(v, dict):
            for k,x in v.items(): rec(f'{prefix}.{k}' if prefix else str(k), x)
    for k,v in (schema or {}).items(): rec(str(k),v)
    return sorted(set(out))



def _state_default_at_path(schema: dict[str, Any], path: str) -> tuple[bool, Any]:
    cur: Any = schema
    for part in str(path).split('.'):
        if not isinstance(cur, dict) or part not in cur:
            return False, None
        cur = cur[part]
    return True, cur

def _schema_from_default(value: Any) -> dict[str, Any] | None:
    if isinstance(value, bool): return {'type':'boolean'}
    if isinstance(value, int) and not isinstance(value, bool): return {'type':'integer'}
    if isinstance(value, float): return {'type':'number'}
    if isinstance(value, str): return {'type':'string'}
    if isinstance(value, list): return {'type':'array'}
    if isinstance(value, dict): return {'type':'object'}
    return None

def _schema_from_declared_type(value: Any) -> dict[str, Any] | None:
    if isinstance(value, str):
        raw=value.strip().lower()
        if raw in {'string','integer','number','boolean','object','array'}: return {'type':raw}
        if raw in {'datetime','date-time','timestamp'}: return {'type':'string','format':'date-time'}
    if isinstance(value, dict) and isinstance(value.get('type'), (str,list)):
        return copy.deepcopy(value)
    return None

def _load_declared_state_types(package_root: Path) -> dict[str, dict[str, Any]]:
    """Discover state type registries by content, never by domain filename.

    Any YAML resource under the package may declare ``variables`` rows containing
    ``path`` plus ``type``/``value_schema``. Multiple registries are merged; exact
    path conflicts fail closed so package ordering cannot change semantics.
    """
    out: dict[str, dict[str, Any]] = {}
    conflicts: list[str] = []
    for reg in sorted(package_root.rglob('*.yaml')) + sorted(package_root.rglob('*.yml')):
        try:
            data=yaml.safe_load(reg.read_text(encoding='utf-8')) or {}
        except Exception:
            continue
        rows=data.get('variables') if isinstance(data,dict) else None
        if not isinstance(rows,list):
            continue
        for row in rows:
            if not isinstance(row,dict) or not row.get('path'):
                continue
            schema=_schema_from_declared_type(row.get('value_schema') if 'value_schema' in row else row.get('type'))
            if schema and row.get('nullable') is True:
                t=schema.get('type')
                if isinstance(t,str): schema['type']=[t,'null']
                elif isinstance(t,list) and 'null' not in t: schema['type']=list(t)+['null']
            if not schema:
                continue
            path=str(row['path'])
            if path in out and out[path] != schema:
                conflicts.append(path)
            else:
                out[path]=schema
    if conflicts:
        raise ValueError('Conflicting declared state type schemas for: '+', '.join(sorted(set(conflicts))))
    return out

def _declared_schema_for_path(path: str, declared: dict[str,dict[str,Any]]) -> dict[str,Any] | None:
    # Type declarations are path-exact. A child string declaration must never
    # type its parent object (e.g. business_meaning.definition -> business_meaning).
    return copy.deepcopy(declared[path]) if path in declared else None

def canonical_path(s:str) -> str:
    s=s.strip()
    for p in ('$state.','state.'):
        if s.startswith(p): return s[len(p):]
    return s[1:] if s.startswith('$') else s


def path_exists_or_parent(path:str, schema_paths:set[str]) -> bool:
    return path in schema_paths or any(q.startswith(path+'.') for q in schema_paths) or any(path.startswith(q+'.') for q in schema_paths)


def extract_declared_input_paths(el:dict) -> set[str]:
    out=set()
    for key in ('reads','inputs','required_inputs'):
        vals=el.get(key)
        vals=vals if isinstance(vals,list) else ([vals] if vals is not None else [])
        for item in vals:
            if isinstance(item,str):
                p=canonical_path(item)
                if PATHISH_RE.match(p): out.add(p)
    return out


def extract_explicit_reads(v:Any, schema_paths:set[str]) -> set[str]:
    out=set()
    for k,x in walk(v):
        if isinstance(x,str):
            for m in STATE_REF_RE.finditer(x): out.add(m.group(1))
            for m in DOLLAR_REF_RE.finditer(x):
                p=m.group(1)
                if p.startswith(('answer','proposal','normalized','derived','runtime','correction_plan')): continue
                if p in schema_paths or any(q.startswith(p+'.') for q in schema_paths): out.add(p)
        if k in ('reads','inputs','required_inputs'):
            vals=x if isinstance(x,list) else [x]
            for item in vals:
                if isinstance(item,str):
                    p=canonical_path(item)
                    if PATHISH_RE.match(p): out.add(p)
    return out


def iter_update_state_maps(v: Any, path: tuple[str,...]=()):
    """Yield every update-state mapping at any nesting depth with its source path."""
    if isinstance(v, dict):
        for k, x in v.items():
            here=path+(str(k),)
            if k in ('update_state','on_pass_update_state','on_fail_update_state') and isinstance(x,dict):
                yield here, x
            yield from iter_update_state_maps(x, here)
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from iter_update_state_maps(x, path+(f'[{i}]',))


def extract_writes(el:dict) -> set[str]:
    return set(shared_declared_writes(el))

def collect_bare_update_expressions(v: Any) -> set[str]:
    out:set[str]=set()
    for _path,mapping in iter_update_state_maps(v):
        for value in mapping.values():
            if isinstance(value,str) and re.fullmatch(r'\$[A-Za-z_][\w.]*',value.strip()): out.add(value.strip())
    return out

def normalize_update_state(el:dict) -> list[dict]:
    """Compile all nested update_state mappings into patch semantics, retaining branch provenance."""
    ops=[]; seen=set()
    for source_path, mapping in iter_update_state_maps(el):
        for raw_path, value in mapping.items():
            path=canonical_path(str(raw_path))
            signature=(source_path,path,json.dumps(value,ensure_ascii=False,sort_keys=True,default=str))
            if signature in seen: continue
            seen.add(signature)
            item={'op':'set','path':path,'declared_at':'.'.join(source_path)}
            if isinstance(value,str) and (value == '$answer' or value.startswith('$answer.')):
                item.update({'source_class':'analyst_answer','source':value})
            elif isinstance(value,str) and value.startswith('$runtime.'):
                item.update({'source_class':'runtime_value','source':value,'runtime_injected':True})
            elif isinstance(value,str) and value.startswith('$state.'):
                item.update({'source_class':'confirmed_state','source':value})
            else:
                item.update({'source_class':'constant','value':copy.deepcopy(value)})
            ops.append(item)
    return ops


ROUTE_DENY_KEYS={'id','incoming_from','allowed_from'}
def _route_kind(path:tuple[str,...]) -> str:
    joined='.'.join(path)
    if 'declared_dynamic_routes' in joined: return 'dynamic'
    if 'navigation_contract' in joined: return 'navigation'
    if 'artifact' in joined or 'missing_artifact_behavior' in joined: return 'exception'
    return 'canonical'


def extract_route_evidence(el:dict, known_targets:set[str]) -> list[dict]:
    return [r for r in shared_routes(el, known_targets) if r.get('target') in known_targets]


def extract_routes(el:dict, known_targets:set[str], is_gate:bool=False) -> list[dict]:
    out=[]; seen_pairs=set(); seen_targets=set()
    for r in shared_declared_routes(el, is_gate=is_gate):
        if r.get('target') not in known_targets: continue
        sig=(r.get('key'),r.get('target'))
        if sig in seen_pairs: continue
        seen_pairs.add(sig); seen_targets.add(r.get('target')); out.append(r)
    # Generic scan is a safety net for route-bearing structures the normalized parser
    # has never seen. Do not duplicate already represented targets.
    for r in extract_route_evidence(el,known_targets):
        if r.get('target') in seen_targets: continue
        sig=(r.get('key'),r.get('target'))
        if sig in seen_pairs: continue
        seen_pairs.add(sig); seen_targets.add(r.get('target')); out.append(r)
    return out

def execution_profile_adaptation(el:dict, is_gate:bool) -> dict:
    return adapt_execution_profile(el, is_gate=is_gate)

def compiled_execution_traits(el:dict, is_gate:bool) -> dict:
    traits = dict(shared_classify(el, is_gate))
    adaptation = execution_profile_adaptation(el, is_gate)
    if adaptation.get('applied'):
        traits.update(adaptation.get('execution_traits_override') or {})
    return traits

def classify(el:dict, is_gate:bool) -> tuple[str,list[str]]:
    traits = compiled_execution_traits(el, is_gate)
    issues = list(traits.get('issues') or [])
    adaptation = execution_profile_adaptation(el, is_gate)
    for diag in adaptation.get('diagnostics') or []:
        if diag.get('severity') == 'error':
            issues.append(str(diag.get('code') or 'PROFILE_ADAPTER_ERROR'))
    return str(traits['kind']), issues

def semantic_state_mentions(el:dict, top_level_state:set[str]) -> set[str]:
    out=set()
    for _,x in walk(el):
        if not isinstance(x,str): continue
        for name in top_level_state:
            if re.search(r'(?<![A-Za-z0-9_])'+re.escape(name)+r'(?![A-Za-z0-9_])', x): out.add(name)
    return out


RESOURCE_PATH_RE=re.compile(r'(?<![A-Za-z0-9_.-])([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+\.(?:yaml|yml|json|md|py))(?![A-Za-z0-9_.-])')
def collect_existing_resource_refs(el:dict, package_root:Path) -> list[str]:
    return shared_resource_refs(el, package_root)

def load_structured_resource(path:Path) -> Any:
    try:
        if path.suffix.lower() in ('.yaml','.yml'):
            return yaml.safe_load(path.read_text(encoding='utf-8'))
        if path.suffix.lower()=='.json':
            return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None
    return None


def collect_resource_closure(seed:Any, package_root:Path) -> tuple[list[str],dict[str,Any]]:
    refs=set(collect_existing_resource_refs(seed,package_root)); content={}
    q=deque(sorted(refs)); seen=set()
    while q:
        r=q.popleft()
        if r in seen: continue
        seen.add(r); rp=package_root/r
        structured=load_structured_resource(rp)
        if structured is not None:
            content[r]=structured
            for rr in collect_existing_resource_refs(structured,package_root):
                if rr not in seen: refs.add(rr); q.append(rr)
    return sorted(refs),content


def table_schema_bindings(resource_content:dict[str,Any]) -> dict[str,dict]:
    out={}
    for _,data in resource_content.items():
        if not isinstance(data,dict) or not isinstance(data.get('tables'),dict): continue
        for _,spec in data['tables'].items():
            if not isinstance(spec,dict) or not isinstance(spec.get('collection'),str): continue
            path=canonical_path(spec['collection'])
            cols=spec.get('columns') or []
            if not isinstance(cols,list): continue
            props={}; required=[]
            for col in cols:
                if not isinstance(col,dict) or not col.get('key'): continue
                k=str(col['key'])
                if col.get('type') == 'array':
                    item_schema=copy.deepcopy(col.get('items')) if isinstance(col.get('items'),dict) else {'type':['string','number','integer','boolean','null']}
                    props[k]={'type':'array','items':item_schema}
                elif col.get('type') == 'string':
                    props[k]={'type':'string'}
                    if isinstance(col.get('enum'),list): props[k]['enum']=copy.deepcopy(col['enum'])
                else:
                    props[k]={'type':['string','number','integer','boolean','null']}
                if col.get('required',True): required.append(k)
            if props:
                out[path]={'type':'array','items':{'type':'object','properties':props,'required':required,'additionalProperties':False}}
    return out


def semantic_payload(el:dict) -> dict: return copy.deepcopy(el)


def build_graph(elements:dict[str,dict], *, include_navigation: bool=False) -> tuple[dict[str,set[str]],dict[str,set[str]]]:
    """Build executable control-flow graph.

    R2 invariant: navigation_contract.allowed_to is a permission surface, not an
    executable transition.  Navigation routes remain in element contracts for UI/runtime
    permission checks but are excluded from dominance, reachability, SCC and dependency
    analysis unless a caller explicitly asks for them.
    """
    out=defaultdict(set); inc=defaultdict(set)
    for eid,e in elements.items():
        for r in e['routes']:
            if not include_navigation and r.get('kind')=='navigation':
                continue
            t=r['target']
            if t in elements: out[eid].add(t); inc[t].add(eid)
    return out,inc


def transitive_dependents(seed:set[str], graph_out:dict[str,set[str]], limit=500) -> set[str]:
    seen=set(seed); q=deque(seed)
    while q and len(seen)<limit:
        x=q.popleft()
        for y in graph_out.get(x,set()):
            if y not in seen: seen.add(y); q.append(y)
    return seen-seed


def reachable_from(start:str, graph_out:dict[str,set[str]]) -> set[str]:
    if not start: return set()
    seen={start}; q=deque([start])
    while q:
        x=q.popleft()
        for y in graph_out.get(x,set()):
            if y not in seen: seen.add(y); q.append(y)
    return seen


def gate_check_ids(external_spec:Any) -> list[str]:
    ids=[]
    if not isinstance(external_spec,dict): return ids
    for key in ('checks','assertions'):
        vals=external_spec.get(key) or []
        if isinstance(vals,list):
            for item in vals:
                if isinstance(item,dict):
                    cid=item.get('check_id') or item.get('id')
                    if cid: ids.append(str(cid))
    return sorted(set(ids))




STRICT_SCHEMA_ALLOWED_KEYWORDS = {
    'type','properties','required','additionalProperties','items','enum','const',
    'anyOf','description','minItems','maxItems','minLength','maxLength','minimum','maximum'
}

def _strict_compatible_schema(schema: Any) -> bool:
    """Conservative strict-subset check for schemas emitted by the compiler.

    Runtime remains authoritative because provider capabilities are runtime data.
    Unsupported/unknown schema keywords fail closed instead of being treated as safe.
    """
    if not isinstance(schema, dict):
        return True
    if any(k not in STRICT_SCHEMA_ALLOWED_KEYWORDS for k in schema):
        return False
    if schema.get('type') == 'object' and isinstance(schema.get('properties'), dict):
        props=set(schema['properties'])
        required=set(schema.get('required') or [])
        if schema.get('additionalProperties') is not False or props != required:
            return False
    props=schema.get('properties')
    if isinstance(props, dict) and not all(_strict_compatible_schema(v) for v in props.values()):
        return False
    items=schema.get('items')
    if isinstance(items, dict) and not _strict_compatible_schema(items):
        return False
    any_of=schema.get('anyOf')
    if isinstance(any_of, list) and not all(_strict_compatible_schema(v) for v in any_of):
        return False
    return True

def element_output_contract(kind:str, writes:list[str], check_ids:list[str], table_bindings:dict[str,dict] | None=None) -> dict:
    table_bindings = table_bindings or {}
    if kind in ('model_gate','deterministic_gate','human_gate'):
        check_id_schema={'type':'string'}
        if check_ids: check_id_schema['enum']=check_ids
        failed_check_item={'type':'object','additionalProperties':False,'required':['check_id','summary','severity'],'properties':{'check_id':check_id_schema,'summary':{'type':'string'},'severity':{'type':['string','null']}}}
        check_result_item={
            'type':'object','additionalProperties':False,
            'required':['check_id','status','evidence','remediation','not_run_reason'],
            'properties':{
                'check_id':check_id_schema,
                'status':{'enum':['pass','fail','not_run']},
                'evidence':{'type':'array','maxItems':2,'items':{'type':'string','maxLength':320}},
                'remediation':{'type':['string','null'],'maxLength':320},
                'not_run_reason':{'type':['string','null'],'maxLength':320},
            },
        }
        missing_info_item={'type':'object','additionalProperties':False,'required':['path','needed','why_needed'],'properties':{'path':{'type':'string'},'needed':{'type':'string'},'why_needed':{'type':['string','null']}}}
        return {
            'contract':'GateFailureOrPass','strict':True,
            'required':['status','gate_id','check_results'],
            'declared_check_ids':list(check_ids),
            'failure_schema':{
                'type':'object','additionalProperties':False,
                'required':['status','gate_id','check_results','failed_checks','invalid_state','missing_information','missing_coverage','affected_state','evidence'],
                'properties':{
                    'status':{'const':'failed'}, 'gate_id':{'type':'string'},
                    'check_results':{'type':'array','items':check_result_item},
                    'failed_checks':{'type':'array','items':failed_check_item},
                    'invalid_state':{'type':'array','items':{'type':'string'}},'missing_information':{'type':'array','items':missing_info_item},'missing_coverage':{'type':'array','items':{'type':'string'}},'affected_state':{'type':'array','items':{'type':'string'}},'evidence':{'type':'array','items':{'type':'string'}}
                }
            },
            'pass_shape':{'status':'passed','gate_id':'<current gate>','check_results':'<one explicit verdict per declared check; [] when none declared>'},
            'json_schema':{
                'type':'object','additionalProperties':False,'required':['status','gate_id','assistant_message','route_key','check_results','failed_checks','invalid_state','missing_information','missing_coverage','affected_state','evidence'],
                'properties':{
                    'status':{'enum':['passed','pass','failed','fail']}, 'gate_id':{'type':'string'},
                    'assistant_message':{'type':'string'}, 'route_key':{'type':['string','null']},
                    'check_results':{'type':'array','items':check_result_item},
                    'failed_checks':{'type':'array','items':failed_check_item}, 'invalid_state':{'type':'array','items':{'type':'string'}},
                    'missing_information':{'type':'array','items':missing_info_item}, 'missing_coverage':{'type':'array','items':{'type':'string'}},
                    'affected_state':{'type':'array','items':{'type':'string'}}, 'evidence':{'type':'array','items':{'type':'string'}}
                }
            }
        }
    path_schema={'type':'string'}
    if writes: path_schema['enum']=writes
    value_schema={'type':['string','number','integer','boolean','object','array','null']}
    op_variants=[]
    bound_paths=set()
    base_props={
        'basis':{'type':['string','null'],'enum':['analyst_input','confirmed_state','derived','generated','recovery','legacy_unknown',None]},
        'reason':{'type':['string','null']},
        'row_key':{'type':['string','null']},
        'row_match':{'type':['string','number','integer','boolean','null']},
    }
    for path in writes:
        bound=table_bindings.get(path)
        if not bound:
            continue
        bound_paths.add(path)
        if isinstance(bound,dict) and bound.get('type')=='array' and isinstance(bound.get('items'),dict):
            row_schema=copy.deepcopy(bound['items'])
            append_props={'op':{'const':'append'},'path':{'const':path},'value':row_schema,**copy.deepcopy(base_props)}
            op_variants.append({'type':'object','required':['op','path','value','basis','reason','row_key','row_match'],'properties':append_props,'additionalProperties':False})
            merge_props={'op':{'const':'merge_row'},'path':{'const':path},'value':copy.deepcopy(row_schema),**copy.deepcopy(base_props)}
            merge_props['row_key']={'type':'string','minLength':1}
            merge_props['row_match']={'type':['string','number','integer','boolean']}
            op_variants.append({'type':'object','required':['op','path','value','basis','reason','row_key','row_match'],'properties':merge_props,'additionalProperties':False})
            if path not in RELEASE1_APPEND_ONLY_COLLECTION_PATHS:
                set_props={'op':{'enum':['set','replace']},'path':{'const':path},'value':copy.deepcopy(bound),**copy.deepcopy(base_props)}
                op_variants.append({'type':'object','required':['op','path','value','basis','reason','row_key','row_match'],'properties':set_props,'additionalProperties':False})
        else:
            props={'op':{'enum':['set','replace','append','merge','merge_deep','merge_row']},'path':{'const':path},'value':copy.deepcopy(bound),**copy.deepcopy(base_props)}
            op_variants.append({'type':'object','required':['op','path','value','basis','reason','row_key','row_match'],'properties':props,'additionalProperties':False})
    unbound=[p for p in writes if p not in bound_paths]
    if unbound:
        props={'op':{'enum':['set','replace','append','merge','merge_deep','merge_row']},'path':{'enum':unbound},'value':value_schema,**copy.deepcopy(base_props)}
        op_variants.append({'type':'object','required':['op','path','value','basis','reason','row_key','row_match'],'properties':props,'additionalProperties':False})
    item={'anyOf':op_variants} if op_variants else {'type':'object','required':['op','path','value','basis','reason','row_key','row_match'],'properties':{'op':{'enum':['set','replace','append','merge','merge_deep','merge_row']},'path':path_schema,'value':value_schema,**copy.deepcopy(base_props)},'additionalProperties':False}
    state_patch_schema={'type':'object','additionalProperties':False,'required':['operations'],'properties':{'base_revision':{'type':'integer','minimum':0,'description':'runtime-owned; model value is ignored when present'},'operations':{'type':'array','items':item}}}
    json_schema={
        'type':'object','additionalProperties':False,
        'required':['assistant_message','state_patch','route_key','needs_analyst','next_intent','rationale_short','action'],
        'properties':{
            'assistant_message':{'type':'string'}, 'state_patch':state_patch_schema,
            'route_key':{'type':['string','null']}, 'needs_analyst':{'type':'boolean'},
            'next_intent':{'type':'string'}, 'rationale_short':{'type':['string','null']},
            'action':{'type':['string','null']},
        }
    }
    return {
        'contract':'NodeExecutionResult','strict':True,
        'required':['assistant_message','state_patch','route_key','needs_analyst','next_intent','rationale_short','action'],
        'state_patch':{'base_revision_owner':'runtime','operations':{'type':'array','items':item}},
        'json_schema':json_schema,
    }


def _interaction_contract(doc: dict) -> dict:
    im = doc.get('interaction_model') if isinstance(doc.get('interaction_model'), dict) else {}
    locale = str(im.get('locale') or im.get('interaction_locale') or '').strip()
    language = str(im.get('model_output_language') or im.get('language') or '').strip()
    if not locale:
        # Compatibility inference only. Explicit interaction_model remains authoritative.
        # Sample analyst-facing prose across the playbook instead of technical IDs/keys.
        chunks=[json.dumps(im,ensure_ascii=False), json.dumps(doc.get('intent') or {},ensure_ascii=False)]
        for record in [*(doc.get('nodes') or []),*(doc.get('gates') or [])]:
            if not isinstance(record,dict): continue
            for key in ('title','purpose','description','question','assistant_message','condition','prompt'):
                value=record.get(key)
                if isinstance(value,str): chunks.append(value)
        sample='\n'.join(chunks)[:120000]
        uk_specific=len(re.findall(r'[іїєґІЇЄҐ]',sample))
        cyrillic=len(re.findall(r'[а-яА-ЯіїєґІЇЄҐ]',sample))
        latin=len(re.findall(r'[A-Za-z]',sample))
        if uk_specific>0:
            locale='uk-UA'
        elif cyrillic>max(24,latin):
            locale='ru-RU'
        else:
            locale='en-US'
    if not language:
        language = 'uk' if locale.lower().startswith('uk') else ('en' if locale.lower().startswith('en') else locale.split('-',1)[0])
    return {
        'locale': locale,
        'model_output_language': language,
        'analyst_facing_text_policy': 'all analyst-facing model messages and runtime/editor explanations use interaction locale; technical IDs and machine keys remain unchanged',
        'source': 'interaction_model' if (im.get('locale') or im.get('interaction_locale') or im.get('model_output_language') or im.get('language')) else 'compatibility_inference',
    }




def _path_write_covers(write_path: str, read_path: str) -> bool:
    """A whole-root/ancestor write can provide a descendant read; descendant writes
    do not prove a whole-parent read."""
    return write_path == read_path or read_path.startswith(write_path + '.')


def _tarjan_scc(graph_out: dict[str, list[str]], nodes: set[str]) -> tuple[list[list[str]], dict[str, int]]:
    index=0; stack=[]; on_stack=set(); indices={}; low={}; comps=[]
    def strong(v: str):
        nonlocal index
        indices[v]=low[v]=index; index += 1; stack.append(v); on_stack.add(v)
        for w in graph_out.get(v, []):
            if w not in nodes: continue
            if w not in indices:
                strong(w); low[v]=min(low[v], low[w])
            elif w in on_stack:
                low[v]=min(low[v], indices[w])
        if low[v] == indices[v]:
            comp=[]
            while True:
                w=stack.pop(); on_stack.remove(w); comp.append(w)
                if w == v: break
            comps.append(sorted(comp))
    for v in sorted(nodes):
        if v not in indices: strong(v)
    by_node={n:i for i,c in enumerate(comps) for n in c}
    return comps, by_node


def _dominators(entry: str, graph_out: dict[str, list[str]], reachable: set[str]) -> dict[str, set[str]]:
    pred={n:set() for n in reachable}
    for a in reachable:
        for b in graph_out.get(a,[]):
            if b in reachable: pred[b].add(a)
    dom={n:({n} if n==entry else set(reachable)) for n in reachable}
    changed=True
    while changed:
        changed=False
        for n in sorted(reachable):
            if n == entry: continue
            ps=pred[n]
            common=set.intersection(*(dom[p] for p in ps)) if ps else set()
            new={n}|common
            if new != dom[n]: dom[n]=new; changed=True
    return dom


def _gate_state_contract_analysis(doc: dict, elements: dict, graph_out: dict[str, list[str]], state_schema: dict) -> dict:
    """Audit deterministic gate state inputs against upstream producer contracts.

    This is an Editor/compiler conformance diagnostic, not new Ordo semantics.  Gate
    inputs are derived only from explicit state references already present in the
    source/compiled read hints.  A model/package-tool write allowlist proves that a
    path *may* be written, not that every valid result must write it.  Static patch
    templates and non-empty initial defaults are the only guarantees recognized here.
    """
    gc=doc.get('graph_contract') or {}
    strictness=str(gc.get('dependency_strictness') or 'advisory').strip().lower()
    if strictness not in {'advisory','strict'}: strictness='advisory'
    entry=str(gc.get('entry_node') or '')
    reachable=reachable_from(entry,graph_out) if entry in elements else set(elements)
    dom=_dominators(entry,graph_out,reachable) if entry in reachable else {n:{n} for n in reachable}
    schema_paths=set(flatten_state_schema(state_schema))
    writers=defaultdict(list)
    for pid,pe in elements.items():
        for w in (pe.get('state_contract') or {}).get('writes') or []:
            writers[str(w)].append(pid)

    def guaranteed_by(pid: str, path: str) -> bool:
        pe=elements.get(pid) or {}
        for op in (pe.get('state_contract') or {}).get('patch_template') or []:
            if isinstance(op,dict) and str(op.get('path') or '') == path and op.get('source_class') in {'constant','confirmed_state','runtime_value'}:
                return True
        return False

    gate_inputs=[]; findings=[]
    for gid,ge in elements.items():
        if ge.get('kind') != 'deterministic_gate' or gid not in reachable:
            continue
        sc=ge.get('state_contract') or {}
        explicit=set(str(x) for x in ((sc.get('declared_inputs_by_class') or {}).get('state') or []))
        # reads_hint contains explicit state.* / $state.* references collected from
        # gate condition/assert/source. Restrict to canonical state schema paths so
        # prose/resource mentions never become producer-consumer contracts.
        hinted=set(str(x) for x in (sc.get('reads_hint') or []) if path_exists_or_parent(str(x),schema_paths))
        inputs=sorted(explicit | hinted)
        for path in inputs:
            has_default,default_value=_state_default_at_path(state_schema,path)
            usable_default=has_default and default_value not in (None,'',[],{})
            exact=[]; ancestor=[]; descendant=[]
            for wp,pids in writers.items():
                for pid in pids:
                    if pid==gid or pid not in reachable or gid not in reachable_from(pid,graph_out):
                        continue
                    item={'producer':pid,'write_path':wp,'dominates_gate':pid in dom.get(gid,set()),'guaranteed':guaranteed_by(pid,path)}
                    if wp == path: exact.append(item)
                    elif path.startswith(wp+'.'): ancestor.append(item)
                    elif wp.startswith(path+'.'): descendant.append(item)
            dom_exact=[x for x in exact if x['dominates_gate']]
            guaranteed=[x for x in dom_exact if x['guaranteed']]
            dom_ancestor=[x for x in ancestor if x['dominates_gate']]
            if usable_default:
                status='initial_default'; guarantee='guaranteed'
            elif guaranteed:
                status='guaranteed'; guarantee='guaranteed'
            elif dom_exact:
                status='declared_not_guaranteed'; guarantee='allowed_write_only'
                findings.append({'severity':'error' if strictness=='strict' else 'warning','code':'GATE_INPUT_PRODUCER_NOT_GUARANTEED','element_id':gid,'path':path,'producers':sorted({x['producer'] for x in dom_exact}),'detail':'deterministic gate input is an allowed upstream write but the producer contract does not require every valid result to materialize this exact path; offline fixtures can hide a live-model shape dependency'})
            elif dom_ancestor:
                status='ancestor_write_only'; guarantee='object_shape_not_proven'
                findings.append({'severity':'warning','code':'GATE_INPUT_ONLY_ANCESTOR_WRITE','element_id':gid,'path':path,'producers':sorted({x['producer'] for x in dom_ancestor}),'ancestor_write_paths':sorted({x['write_path'] for x in dom_ancestor}),'detail':'deterministic gate consumes a leaf path but upstream contracts only declare an ancestor/object write; the required leaf shape is not statically guaranteed'})
            elif exact:
                status='branch_dependent'; guarantee='not_dominating'
                findings.append({'severity':'warning','code':'GATE_INPUT_PRODUCER_NOT_DOMINATING','element_id':gid,'path':path,'producers':sorted({x['producer'] for x in exact}),'detail':'deterministic gate input has a producer on some path, but no exact producer dominates the gate'})
            else:
                status='unproduced'; guarantee='none'
                findings.append({'severity':'warning','code':'GATE_INPUT_HAS_NO_UPSTREAM_PRODUCER','element_id':gid,'path':path,'detail':'deterministic gate consumes a state path with no exact upstream producer/default; do not satisfy this only through fixture-specific convenience state'})
            gate_inputs.append({
                'gate_id':gid,'path':path,'status':status,'guarantee':guarantee,
                'exact_upstream_producers':sorted({x['producer'] for x in exact}),
                'dominating_exact_producers':sorted({x['producer'] for x in dom_exact}),
                'ancestor_upstream_producers':sorted({x['producer'] for x in ancestor}),
                'descendant_upstream_producers':sorted({x['producer'] for x in descendant}),
                'initial_default_present':bool(usable_default),
            })
    return {
        'contract':'editor.gate_state_contract_analysis/v1',
        'invariant':'GATE_PRODUCER_CONSUMER_STATIC_ALIGNMENT',
        'strictness':strictness,
        'gate_inputs':gate_inputs,
        'findings':findings,
        'summary':{
            'gate_inputs':len(gate_inputs),
            'guaranteed':sum(x['guarantee']=='guaranteed' for x in gate_inputs),
            'risks':sum(x['guarantee']!='guaranteed' for x in gate_inputs),
        },
    }


def _r2_dependency_analysis(doc: dict, elements: dict, graph_out: dict[str, list[str]], state_schema: dict) -> dict:
    """R2-A producer/consumer inventory and conservative dominance proof.

    The analysis is advisory by default for legacy packages.  It becomes blocking only
    when graph_contract.dependency_strictness=strict.  Explicit optional dependencies
    are declarations, not synthetic producers.
    """
    gc=doc.get('graph_contract') or {}
    strictness=str(gc.get('dependency_strictness') or 'advisory').strip().lower()
    if strictness not in {'advisory','strict'}: strictness='advisory'
    optional={}
    for item in gc.get('explicit_optional_dependencies') or []:
        if isinstance(item,dict) and item.get('consumer') and item.get('path'):
            optional[(str(item['consumer']),str(item['path']))]=str(item.get('reason') or '')
    entry=str(gc.get('entry_node') or '')
    reachable=reachable_from(entry,graph_out) if entry in elements else set(elements)
    dom=_dominators(entry,graph_out,reachable) if entry in reachable else {n:{n} for n in reachable}
    graph_in=defaultdict(set)
    for _a,_targets in graph_out.items():
        for _b in _targets:
            if _a in reachable and _b in reachable: graph_in[_b].add(_a)
    sccs,scc_by=_tarjan_scc(graph_out,reachable)
    cyclic=[c for c in sccs if len(c)>1 or (len(c)==1 and c[0] in graph_out.get(c[0],[]))]
    writers=defaultdict(set)
    readers=defaultdict(set)
    for eid,e in elements.items():
        for w in (e.get('state_contract') or {}).get('writes') or []: writers[str(w)].add(eid)
        state_inputs=((e.get('state_contract') or {}).get('declared_inputs_by_class') or {}).get('state') or []
        for r in state_inputs: readers[str(r)].add(eid)
    paths=sorted(set(writers)|set(readers))
    inventory={}
    consumer_proofs=[]
    findings=[]
    for path in paths:
        has_default,default_value=_state_default_at_path(state_schema,path)
        usable_default=has_default and default_value not in (None,'',[],{})
        inventory[path]={
            'writers':sorted(writers.get(path,set())),
            'readers':sorted(readers.get(path,set())),
            'required_at':sorted(readers.get(path,set())),
            'optional_at':sorted(c for c,p in optional if p==path),
            'default_source':'state.schema' if has_default else None,
            'default_value_present':bool(has_default),
            'default_satisfies_required_input':bool(usable_default),
            'external_source':None,
        }
    for consumer,e in elements.items():
        if consumer not in reachable: continue
        state_inputs=((e.get('state_contract') or {}).get('declared_inputs_by_class') or {}).get('state') or []
        for path in state_inputs:
            path=str(path)
            has_default,default_value=_state_default_at_path(state_schema,path)
            usable_default=has_default and default_value not in (None,'',[],{})
            candidates=[]
            descendant_candidates=[]
            for wp,owners in writers.items():
                if _path_write_covers(str(wp),path):
                    candidates.extend((o,str(wp)) for o in owners if o in reachable and o!=consumer)
                elif str(wp).startswith(path+'.'):
                    descendant_candidates.extend((o,str(wp)) for o in owners if o in reachable and o!=consumer)
            dominating=[(o,wp) for o,wp in candidates if o in dom.get(consumer,set())]
            dominating_descendants=[(o,wp) for o,wp in descendant_candidates if o in dom.get(consumer,set())]
            # A direct predecessor gate can establish a state precondition even when the
            # value came from an external/preloaded state or a recovery producer that does
            # not dominate the gate. This is a proof only for the gate's on_pass successor.
            validating_gates=[]
            for pred in graph_in.get(consumer,set()):
                pe=elements.get(pred) or {}
                if pe.get('kind') not in {'model_gate','deterministic_gate','human_gate'}: continue
                if not any(r.get('key')=='on_pass' and r.get('target')==consumer for r in pe.get('routes') or []): continue
                pins=((pe.get('state_contract') or {}).get('declared_inputs_by_class') or {}).get('state') or []
                if path in {str(x) for x in pins}: validating_gates.append(pred)
            # Dominance is well-defined on cyclic CFGs.  SCC membership is retained as
            # cycle evidence, but must not downgrade a real entry-dominance proof to
            # "revisit": if P dominates C, every first path from entry to C crosses P.
            same_scc=[o for o,wp in dominating if scc_by.get(o)==scc_by.get(consumer)]
            relevant_exits={}
            for o,_wp in dominating:
                exits=[]
                for target in graph_out.get(o,[]):
                    if target==consumer or consumer in reachable_from(target,graph_out): exits.append(target)
                relevant_exits[o]=sorted(set(exits))
            explicit=(consumer,path) in optional
            if usable_default:
                guarantee='guaranteed_before_first_visit'
                evidence='initial_state_default'
            elif dominating:
                guarantee='guaranteed_before_first_visit'; evidence='dominating_producer'
            elif validating_gates:
                guarantee='guaranteed_before_first_visit'; evidence='validated_by_predecessor_gate'
            elif dominating_descendants:
                guarantee='guaranteed_before_first_visit'; evidence='structured_root_initialized_by_dominating_descendant_write'
            elif explicit:
                guarantee='optional'; evidence='explicit_optional_dependency'
            else:
                guarantee='may_exist'; evidence='no_dominating_producer'
            proof={
                'consumer':consumer,'path':path,
                'candidate_writers':sorted(set(o for o,_ in candidates)),
                'dominating_writers':sorted(set(o for o,_ in dominating)),
                'dominating_descendant_writers':sorted(set(o for o,_ in dominating_descendants)),
                'validating_predecessor_gates':sorted(set(validating_gates)),
                'dominating_writers_in_consumer_scc':sorted(set(same_scc)),
                'relevant_exits':relevant_exits,
                'relevant_exit_definition':'producer exits whose target can reach the consumer; StatePatch commit precedes route selection',
                'guarantee':guarantee,'evidence':evidence,
                'explicit_optional_reason':optional.get((consumer,path)),
            }
            consumer_proofs.append(proof)
            if guarantee=='may_exist':
                findings.append({
                    'severity':'error' if strictness=='strict' else 'warning',
                    'code':'MISSING_DOMINATING_PRODUCER','element_id':consumer,'path':path,
                    'detail':'required state input has no initial default, dominating producer, or explicit optional dependency',
                    'dependency_strictness':strictness,
                })
    return {
        'dependency_strictness':strictness,
        'entry_node':entry,
        'reachable_elements':len(reachable),
        'scc_count':len(sccs),
        'cyclic_scc_count':len(cyclic),
        'cyclic_sccs':cyclic,
        'inventory':inventory,
        'consumer_proofs':consumer_proofs,
        'summary':{
            'required_consumers':len(consumer_proofs),
            'guaranteed_before_first_visit':sum(x['guarantee']=='guaranteed_before_first_visit' for x in consumer_proofs),
            'guaranteed_before_revisit':sum(x['guarantee']=='guaranteed_before_revisit' for x in consumer_proofs),
            'optional':sum(x['guarantee']=='optional' for x in consumer_proofs),
            'may_exist':sum(x['guarantee']=='may_exist' for x in consumer_proofs),
        },
        'findings':findings,
    }


def _variant_allowed_ops(variant: dict) -> set[str]:
    props=(variant or {}).get('properties') or {}
    op=(props.get('op') or {}) if isinstance(props,dict) else {}
    if not isinstance(op,dict): return set()
    if 'const' in op: return {str(op['const'])}
    vals=op.get('enum')
    return {str(x) for x in vals} if isinstance(vals,list) else set()

def _variant_paths(variant: dict) -> set[str]:
    props=(variant or {}).get('properties') or {}
    ps=(props.get('path') or {}) if isinstance(props,dict) else {}
    if not isinstance(ps,dict): return set()
    if 'const' in ps: return {str(ps['const'])}
    vals=ps.get('enum')
    return {str(x) for x in vals} if isinstance(vals,list) else set()

def _variant_value_schema(variant: dict) -> dict:
    props=(variant or {}).get('properties') or {}
    value=(props.get('value') or {}) if isinstance(props,dict) else {}
    return value if isinstance(value,dict) else {}


def _schema_types(schema: dict) -> set[str]:
    if not isinstance(schema,dict): return set()
    t=schema.get('type')
    if isinstance(t,str): return {t}
    if isinstance(t,list): return {str(x) for x in t}
    if isinstance(schema.get('properties'),dict): return {'object'}
    return set()


def _schema_excludes_null(schema: dict) -> bool:
    if not isinstance(schema,dict): return False
    if schema.get('const', object()) is None: return False
    if isinstance(schema.get('enum'),list) and None in schema.get('enum'): return False
    types=_schema_types(schema)
    return bool(types) and 'null' not in types


def _schema_guarantees_descendant(schema: dict, parts: list[str]) -> bool:
    """True only when every value valid against schema contains a populated path."""
    if not parts:
        return _schema_excludes_null(schema)
    if not isinstance(schema,dict): return False
    types=_schema_types(schema)
    if types and 'object' not in types: return False
    props=schema.get('properties')
    if not isinstance(props,dict): return False
    key=parts[0]
    if key not in set(schema.get('required') or []) or key not in props:
        return False
    return _schema_guarantees_descendant(props[key],parts[1:])


def _schema_shallow_merge_preserves(schema: dict, parts: list[str]) -> bool:
    """A shallow merge is safe iff any allowed overwrite of the relevant branch preserves it."""
    if not parts:
        return True  # runtime merge keeps the target object itself populated
    if not isinstance(schema,dict): return False
    props=schema.get('properties')
    key=parts[0]
    if not isinstance(props,dict) or key not in props:
        # additionalProperties=False means the relevant branch cannot be overwritten.
        return schema.get('additionalProperties') is False
    child=props[key]
    if len(parts)==1:
        return _schema_excludes_null(child)
    # shallow dict.update replaces the whole direct child; that replacement must
    # therefore guarantee the remaining required descendant.
    return _schema_guarantees_descendant(child,parts[1:])


def _schema_deep_merge_preserves(schema: dict, parts: list[str]) -> bool:
    """A deep merge preserves omitted keys, but an allowed scalar/null branch may replace them."""
    if not parts:
        return True
    if not isinstance(schema,dict): return False
    props=schema.get('properties')
    key=parts[0]
    if not isinstance(props,dict) or key not in props:
        return schema.get('additionalProperties') is False
    child=props[key]
    if len(parts)==1:
        return _schema_excludes_null(child)
    child_types=_schema_types(child)
    if child_types and child_types != {'object'}:
        return False
    if not child_types and not isinstance(child.get('properties'),dict):
        return False
    # The key itself is optional for merge semantics (omission preserves existing
    # state). If present as an object, recurse to prove any nested overwrite safe.
    return _schema_deep_merge_preserves(child,parts[1:])


def _destructive_ops_for_required_path(variant: dict, write_path: str, required_path: str) -> set[str]:
    if not (required_path==write_path or required_path.startswith(write_path+'.')):
        return set()
    rel=required_path[len(write_path):].lstrip('.')
    parts=[x for x in rel.split('.') if x]
    schema=_variant_value_schema(variant)
    destructive=set()
    for op in _variant_allowed_ops(variant):
        if op=='remove':
            destructive.add(op); continue
        if op in {'set','replace'}:
            if not _schema_guarantees_descendant(schema,parts): destructive.add(op)
        elif op=='merge':
            if not _schema_shallow_merge_preserves(schema,parts): destructive.add(op)
        elif op=='merge_deep':
            if not _schema_deep_merge_preserves(schema,parts): destructive.add(op)
        # append / merge_row cannot replace an ancestor object under their runtime
        # contract, so they are not subtree-destructive here.
    return destructive


def _r3_required_path_survivability(elements: dict, dependency_analysis: dict, graph_out: dict[str,list[str]]) -> dict:
    """Prove required state remains available across reachable revisits.

    Earlier revisions checked only ``remove``.  A revisit can also destroy a required
    descendant by ``set``/``replace`` of an ancestor or by an insufficiently-shaped
    shallow/deep merge.  This analysis is operation- and schema-aware and only treats
    a writer as a revisit risk when the consumer can reach the writer and the writer
    can reach the consumer again.
    """
    proofs=[p for p in (dependency_analysis.get('consumer_proofs') or []) if p.get('path') and p.get('consumer') and p.get('guarantee')!='optional']
    required=sorted({str(p.get('path')) for p in proofs})
    strictness=str(dependency_analysis.get('dependency_strictness') or 'advisory')
    reach_cache={}
    def reaches(a:str,b:str) -> bool:
        key=(a,b)
        if key not in reach_cache:
            reach_cache[key]= b in reachable_from(a,graph_out)
        return reach_cache[key]

    removable=[]
    destructive=[]
    for proof in proofs:
        consumer=str(proof['consumer']); rp=str(proof['path'])
        for eid,e in elements.items():
            if eid==consumer: continue
            # Only a writer that can occur between two visits to this consumer can
            # invalidate a previously-established required subtree on revisit.
            if not (reaches(consumer,eid) and reaches(eid,consumer)):
                continue
            variants=((((e.get('output_contract') or {}).get('state_patch') or {}).get('operation_variants')) or [])
            for v in variants:
                for wp in _variant_paths(v):
                    if not (rp==wp or rp.startswith(wp+'.')): continue
                    ops=_destructive_ops_for_required_path(v,wp,rp)
                    if not ops: continue
                    row={'consumer':consumer,'element_id':eid,'write_path':wp,'required_path':rp,'destructive_ops':sorted(ops)}
                    if 'remove' in ops:
                        removable.append(row)
                    ancestor_ops=ops-{'remove'}
                    if ancestor_ops and wp!=rp and rp.startswith(wp+'.'):
                        destructive.append({**row,'destructive_ops':sorted(ancestor_ops)})

    # Deduplicate because operation schemas can be projected through more than one
    # equivalent variant.
    def dedupe(rows):
        out={}
        for r in rows:
            key=(r['consumer'],r['element_id'],r['write_path'],r['required_path'])
            if key not in out: out[key]=dict(r)
            else: out[key]['destructive_ops']=sorted(set(out[key]['destructive_ops'])|set(r['destructive_ops']))
        return list(out.values())
    removable=dedupe(removable); destructive=dedupe(destructive)

    findings=[]
    for row in removable:
        findings.append({
            'severity':'error','code':'REQUIRED_PATH_REMOVABLE','element_id':row['element_id'],
            'consumer':row['consumer'],'path':row['write_path'],'affected_required_paths':[row['required_path']],
            'destructive_ops':row['destructive_ops'],
            'detail':'reachable revisit writer may remove state required by a consumer; first-visit dominance is not sufficient for revisit safety',
        })
    for row in destructive:
        findings.append({
            'severity':'error' if strictness=='strict' else 'warning',
            'code':'REQUIRED_PATH_ANCESTOR_DESTRUCTIVE_OVERWRITE','element_id':row['element_id'],
            'consumer':row['consumer'],'path':row['write_path'],'affected_required_paths':[row['required_path']],
            'destructive_ops':row['destructive_ops'],
            'detail':'reachable revisit writer may set/replace/merge an ancestor object without proving preservation of a required descendant',
            'dependency_strictness':strictness,
        })
    return {
        'status':'PASS' if not findings else ('FAIL' if any(x.get('severity')=='error' for x in findings) else 'WARNING'),
        'required_path_count':len(required),
        'removable_authorizations':removable,
        'destructive_overwrite_authorizations':destructive,
        'findings':findings,
        'invariant':'required consumer paths must survive every reachable revisit writer; remove and destructive ancestor overwrite/merge are forbidden unless the operation schema proves preservation',
    }

def _r3_state_ownership_contract(elements: dict) -> dict:
    paths=defaultdict(lambda:{'writers':set(),'readers':set()})
    for eid,e in elements.items():
        sc=e.get('state_contract') or {}
        for p in sc.get('writes') or []: paths[str(p)]['writers'].add(eid)
        for p in ((sc.get('declared_inputs_by_class') or {}).get('state') or []): paths[str(p)]['readers'].add(eid)
    return {
        'write_authority':'per-element allowlist enforced by runtime StatePatch validation',
        'paths':{p:{'writers':sorted(v['writers']),'readers':sorted(v['readers'])} for p,v in sorted(paths.items())},
    }

def compile_plan(program_path:Path, package_root:Path) -> dict:
    raw=program_path.read_bytes(); doc=yaml.safe_load(raw)
    state_schema=(doc.get('state') or {}).get('schema') or {}
    schema_paths=set(flatten_state_schema(state_schema)); top_level_state=set(state_schema)
    declared_state_types=_load_declared_state_types(package_root)
    untyped_write_paths:set[str]=set()
    raw_elements=[(False,el) for el in (doc.get('nodes') or [])]+[(True,el) for el in (doc.get('gates') or [])]
    element_ids={str(el.get('id')) for _,el in raw_elements if el.get('id')}
    ext_targets=set((doc.get('graph_contract') or {}).get('external_terminal_targets') or [])
    known_targets=element_ids|ext_targets
    elements={}
    artifact_registry = None
    artifact_registry_path = package_root / "verification" / "ARTIFACT_MATERIALIZATION_REGISTRY.json"
    if artifact_registry_path.is_file():
        try:
            loaded_registry = json.loads(artifact_registry_path.read_text(encoding="utf-8"))
            if isinstance(loaded_registry, dict):
                artifact_registry = loaded_registry
        except Exception as exc:
            compilation_issues = [{"severity":"error","code":"PROFILE_ARTIFACT_REGISTRY_INVALID","detail":str(exc)}]
        else:
            compilation_issues = []
    else:
        compilation_issues = []
    interaction_contract = _interaction_contract(doc)
    if interaction_contract.get('source') == 'compatibility_inference':
        compilation_issues.append({'severity':'warning','code':'INTERACTION_LOCALE_INFERRED','detail':'interaction_model.locale/model_output_language were inferred; explicit declaration is preferred','locale':interaction_contract.get('locale'),'model_output_language':interaction_contract.get('model_output_language')})

    for is_gate,el in raw_elements:
        eid=el['id']; kind,class_issues=classify(el,is_gate)
        for msg in class_issues:
            compilation_issues.append({'severity':'error','code':'CLASSIFICATION_CONFLICT' if kind!='unknown_node' else 'UNKNOWN_ELEMENT_KIND','element_id':eid,'detail':msg})
        external_spec=None
        if is_gate:
            spec_path=el.get('specification')
            if isinstance(spec_path,str):
                sp=(package_root/spec_path)
                if sp.is_file():
                    try: external_spec=yaml.safe_load(sp.read_text(encoding='utf-8'))
                    except Exception: external_spec={'raw_text':sp.read_text(encoding='utf-8',errors='replace')}
        resource_seed={'element':el,'external_specification':external_spec}
        resource_refs,resource_content=collect_resource_closure(resource_seed,package_root)
        reads=set(extract_explicit_reads(el,schema_paths)); semantic_mentions=set(semantic_state_mentions(el,top_level_state))
        if external_spec is not None:
            reads |= extract_explicit_reads(external_spec,schema_paths); semantic_mentions |= semantic_state_mentions(external_spec,top_level_state)
        for data in resource_content.values():
            reads |= extract_explicit_reads(data,schema_paths); semantic_mentions |= semantic_state_mentions(data,top_level_state)
        writes=sorted(extract_writes(el)); reads=sorted(reads); semantic_mentions=sorted(semantic_mentions)
        # R3: a human-decision node that declares canonical writes must also declare
        # how analyst input is bound into those writes. Otherwise runtime can choose
        # a route while leaving downstream required state unchanged, producing an
        # unrecoverable/no-progress loop. This is a generic source-contract invariant.
        if str(el.get('type') or '') == 'human_decision' and writes:
            bound_paths=set()
            def _collect_human_write_bindings(value):
                if isinstance(value, dict):
                    upd=value.get('update_state')
                    if isinstance(upd, dict):
                        bound_paths.update(str(k) for k in upd.keys())
                    # Explicit structured-input contracts can bind canonical paths
                    # directly; support common generic field descriptors without
                    # coupling the compiler to a particular playbook domain.
                    for key in ('field_bindings','answer_bindings','capture_bindings'):
                        mapping=value.get(key)
                        if isinstance(mapping, dict):
                            bound_paths.update(str(k) for k in mapping.keys())
                    for child in value.values():
                        _collect_human_write_bindings(child)
                elif isinstance(value, list):
                    for child in value:
                        _collect_human_write_bindings(child)
            _collect_human_write_bindings(el.get('on_answer'))
            unbound=[w for w in writes if w not in bound_paths]
            if unbound:
                compilation_issues.append({
                    'severity':'error',
                    'code':'HUMAN_WRITE_WITHOUT_BINDING',
                    'element_id':eid,
                    'paths':unbound,
                    'detail':'human_decision declares writable state paths but no on_answer/update_state or explicit answer binding can populate them'
                })
        # R3 authority contract: if a model node declares that some outputs must be
        # derived from already-confirmed canonical state, the compiler must prove that
        # the node actually has write authority for those targets and read authority
        # for every declared source. This prevents a playbook from saying "reuse
        # confirmed state" while structurally forcing the model to ask the analyst for
        # values it should have derived itself.
        authority=el.get('authority_contract') if isinstance(el.get('authority_contract'),dict) else None
        if authority is not None:
            derived=authority.get('derived_targets') if isinstance(authority.get('derived_targets'),dict) else {}
            clarification=[str(x) for x in (authority.get('clarification_only_fields') or []) if isinstance(x,str)]
            open_questions_path=str(authority.get('open_questions_path') or '').strip()
            write_set=set(writes)
            input_set=set(extract_declared_input_paths(el))
            for target,spec in derived.items():
                target=str(target)
                if target not in write_set:
                    compilation_issues.append({
                        'severity':'error','code':'AUTHORITY_DERIVED_TARGET_NOT_WRITABLE',
                        'element_id':eid,'path':target,
                        'detail':'authority_contract derived target is not declared writable by the element'
                    })
                sources=[]
                if isinstance(spec,dict):
                    sources=[str(x) for x in (spec.get('sources') or []) if isinstance(x,str)]
                for source in sources:
                    if source not in input_set:
                        compilation_issues.append({
                            'severity':'error','code':'AUTHORITY_SOURCE_NOT_DECLARED_INPUT',
                            'element_id':eid,'target':target,'source':source,
                            'detail':'authority_contract source must be a declared input of the deriving element'
                        })
                selectors=[str(x) for x in (spec.get('must_include_from') or []) if isinstance(x,str)] if isinstance(spec,dict) else []
                for selector in selectors:
                    root=selector.split('.',1)[0]
                    if root not in input_set:
                        compilation_issues.append({
                            'severity':'error','code':'AUTHORITY_LITERAL_SOURCE_NOT_DECLARED_INPUT',
                            'element_id':eid,'target':target,'selector':selector,
                            'detail':'must_include_from selector root must be a declared input of the deriving element'
                        })
            for path in clarification:
                if path in derived:
                    compilation_issues.append({
                        'severity':'error','code':'AUTHORITY_ROLE_OVERLAP',
                        'element_id':eid,'path':path,
                        'detail':'a path cannot be both authority-derived and clarification-only'
                    })
                if path in write_set:
                    compilation_issues.append({
                        'severity':'error','code':'AUTHORITY_CLARIFICATION_FIELD_WRITABLE',
                        'element_id':eid,'path':path,
                        'detail':'clarification-only fields must not be writable by the derivation node'
                    })
                if path not in input_set:
                    compilation_issues.append({
                        'severity':'error','code':'AUTHORITY_CLARIFICATION_FIELD_NOT_INPUT',
                        'element_id':eid,'path':path,
                        'detail':'clarification-only field must be visible as an input so missingness can be evaluated'
                    })
            if open_questions_path and open_questions_path not in write_set:
                compilation_issues.append({
                    'severity':'error','code':'AUTHORITY_OPEN_QUESTIONS_NOT_WRITABLE',
                    'element_id':eid,'path':open_questions_path,
                    'detail':'authority_contract open_questions_path must be writable by the derivation node'
                })

        for expr in sorted(collect_bare_update_expressions(el)):
            symbol=expr[1:]
            root=symbol.split('.',1)[0]
            known = expr in {'$answer','$runtime.timestamp','$runtime.now','$runtime.datetime','$increment'} or root in {'answer','normalized','generated','derived','resolved','gate'} or symbol in schema_paths
            if not known:
                compilation_issues.append({'severity':'warning','code':'UNRESOLVED_UPDATE_EXPRESSION_POTENTIAL','element_id':eid,'expression':expr,'detail':'bare $ expression in update_state is not a canonical state path or known runtime resolver; runtime will fail closed if it reaches commit unresolved'})
        declared_inputs=sorted(extract_declared_input_paths(el))
        declared_inputs_by_class={'state':[], 'runtime':[], 'interaction':[], 'recovery':[], 'metadata':[]}
        unknown_declared=[]
        for pth in declared_inputs:
            cls=classify_declared_input(pth,schema_paths)
            if cls is None:
                unknown_declared.append(pth)
            else:
                declared_inputs_by_class[cls].append(pth)
        for pth in unknown_declared:
            compilation_issues.append({'severity':'error','code':'DECLARED_INPUT_NOT_IN_CONTEXT_CONTRACT','element_id':eid,'path':pth,'detail':'declared input is neither canonical state nor a reserved runtime/session/recovery/metadata input'})
        base={
            'id':eid,'kind':kind,'title':el.get('title'),'semantic_source':semantic_payload(el),
            'semantic_fidelity':{'mode':'structural_preservation','source_keys':sorted(el.keys()),'source_sha256':sha256_bytes(json.dumps(el,ensure_ascii=False,sort_keys=True,default=str).encode())},
            'state_contract':{'reads_hint':reads,'declared_inputs':declared_inputs,'declared_inputs_by_class':declared_inputs_by_class,'external_context_inputs':sorted([p for cls in ('runtime','interaction','recovery','metadata') for p in declared_inputs_by_class[cls]]),'semantic_objects':semantic_mentions,'writes':writes,'write_policy':'runtime_validated_state_patch','context_policy':'semantic_objects_not_minimal_leaf_projection','patch_template':normalize_update_state(el)},
            'routes':extract_routes(el,known_targets,is_gate),'route_evidence':extract_route_evidence(el,known_targets),'resources':resource_refs,
            'analyst_interaction':{'question':el.get('question'),'answer_type':el.get('answer_type'),'on_unmatched_input':copy.deepcopy(el.get('on_unmatched_input')),'expected_fields':copy.deepcopy(el.get('expected_fields')),'revisit_policy':'preserve_previous_answer_and_ask_only_delta'},
            'execution_traits':{k:v for k,v in compiled_execution_traits(el,is_gate).items() if k in ('requires_analyst','model_executed','model_executed_phases','runtime_executor','renders_artifact','deterministic')},
            'recovery':{'callable':True,'modes':['revisit'] + (['auto_regenerate'] if kind in ('model_node','document_generate','deterministic_operation') else []),'writes':writes,'requires_analyst_on_revisit':'conditional'},
        }
        profile_adaptation = execution_profile_adaptation(el, is_gate)
        artifact_gate_adaptation = adapt_artifact_validation_profile(el, doc, artifact_registry) if is_gate else {"applied": False, "diagnostics": []}
        if profile_adaptation.get('applied'):
            base['profile_adapter'] = {
                'profile_id': profile_adaptation.get('profile_id'),
                'status': 'applied',
                'source_contract': ((profile_adaptation.get('execution_adapter') or {}).get('source_contract')),
            }
            base['execution_adapter'] = copy.deepcopy(profile_adaptation.get('execution_adapter') or {})
        if artifact_gate_adaptation.get('applied'):
            base['profile_adapter'] = {
                'profile_id': artifact_gate_adaptation.get('profile_id'),
                'status': 'applied',
                'source_contract': ((artifact_gate_adaptation.get('execution_adapter') or {}).get('source_contract')),
            }
            base['execution_adapter'] = copy.deepcopy(artifact_gate_adaptation.get('execution_adapter') or {})
            base['execution_traits']['runtime_executor'] = 'artifact_validation'
            base['execution_traits']['deterministic'] = True
        for _diag in artifact_gate_adaptation.get('diagnostics') or []:
            compilation_issues.append({
                'severity': _diag.get('severity') or 'warning',
                'code': _diag.get('code') or 'PROFILE_ADAPTER_DIAGNOSTIC',
                'element_id': eid,
                'source_path': _diag.get('source_path'),
                'value': copy.deepcopy(_diag.get('value')),
                'detail': _diag.get('detail'),
                'adapter': artifact_gate_adaptation.get('profile_id'),
            })
        for _diag in profile_adaptation.get('diagnostics') or []:
            compilation_issues.append({
                'severity': _diag.get('severity') or 'warning',
                'code': _diag.get('code') or 'PROFILE_ADAPTER_DIAGNOSTIC',
                'element_id': eid,
                'source_path': _diag.get('source_path'),
                'value': copy.deepcopy(_diag.get('value')),
                'detail': _diag.get('detail'),
                'adapter': profile_adaptation.get('profile_id'),
            })

        if kind=='human_gate':
            base['analyst_interaction']['question']=el.get('question') or f"Confirm whether this criterion is satisfied: {el.get('condition') or el.get('title') or eid}"
            base['analyst_interaction']['criterion']=copy.deepcopy(el.get('condition'))
        if is_gate:
            checks=[]
            if isinstance(external_spec,dict):
                for ck in external_spec.get('checks') or external_spec.get('assertions') or []:
                    if isinstance(ck,dict): checks.append(copy.deepcopy({k:v for k,v in ck.items() if k in ('id','check_id','name','severity','assertion','remediation')}))
            base['gate_contract']={'condition':el.get('condition'),'assert':el.get('assert'),'source':el.get('source'),'method':el.get('method'),'trust_class':el.get('trust_class'),'validator':el.get('validator'),'result_contract':copy.deepcopy(el.get('result_contract')) or (copy.deepcopy(external_spec.get('result_contract')) if isinstance(external_spec,dict) else None),'external_specification':external_spec,'checks_inline':checks,'on_fail_feedback':copy.deepcopy(el.get('on_fail_feedback') or el.get('validation_feedback')),'failure_output':'GateFailure','local_patch_allowed':True}
        base['output_contract']=element_output_contract(kind,writes,gate_check_ids(external_spec),table_schema_bindings(resource_content))
        elements[eid]=base

    graph_out,graph_in=build_graph(elements)
    r2_dependency_analysis=_r2_dependency_analysis(doc,elements,graph_out,state_schema)
    compilation_issues.extend(copy.deepcopy(r2_dependency_analysis.get('findings') or []))
    gate_state_contract_analysis=_gate_state_contract_analysis(doc,elements,graph_out,state_schema)
    compilation_issues.extend(copy.deepcopy(gate_state_contract_analysis.get('findings') or []))
    owners=defaultdict(set); readers=defaultdict(set)
    for eid,e in elements.items():
        for p in e['state_contract']['writes']: owners[p].add(eid)
        for p in e['state_contract']['reads_hint']: readers[p].add(eid)
    # Release 1: V7-native projection defaults for schema-default roots that have
    # no writer anywhere in the graph. These defaults are execution-projection only;
    # runtime must never commit them into canonical state. Dominance-based refinement
    # is intentionally deferred to Release 2.
    top_level_writers=defaultdict(set)
    for _eid,_e in elements.items():
        for _w in _e['state_contract']['writes']:
            top_level_writers[str(_w).split('.')[0]].add(_eid)
    for _eid,_e in elements.items():
        sc=_e.get('state_contract') or {}
        preload_roots=set(str(x).split('.')[0] for x in (sc.get('semantic_objects') or []) if isinstance(x,str))
        preload_roots.update(str(x).split('.')[0] for x in (sc.get('reads_hint') or []) if isinstance(x,str))
        defaults={}
        for _root in sorted(preload_roots):
            if _root not in state_schema:
                continue
            _default=state_schema.get(_root)
            if _default is None:
                continue
            if top_level_writers.get(_root):
                continue
            defaults[_root]=copy.deepcopy(_default)
        if defaults:
            sc.setdefault('projection_defaults',{})['enter']=defaults
            if 'respond' in (_e.get('execution_traits') or {}).get('model_executed_phases',[]):
                sc.setdefault('projection_defaults',{})['respond']=copy.deepcopy(defaults)

    all_state=set(schema_paths)|set(owners)|set(readers); depmap={}
    for p in sorted(all_state):
        os=set(owners.get(p,set())); rs=set(readers.get(p,set())); deps=transitive_dependents(os,graph_out) if os else set()
        downstream_writes=sorted({w for d in deps if d in elements for w in elements[d]['state_contract']['writes']})
        prov='analyst_confirmed' if any(elements[o]['kind'] in ('interactive_node','human_gate') for o in os) else ('generated' if os else 'external_or_initial')
        depmap[p]={'owners':sorted(os),'readers':sorted(rs),'downstream_dependents':sorted(deps),'downstream_writes':downstream_writes,'provenance_class':prov}

    # Derive recovery targets from state ownership, not hand-maintained lists.
    for eid,e in elements.items():
        if not e['kind'].endswith('_gate'): continue
        affected=set(e['state_contract']['reads_hint'])
        gc=e.get('gate_contract') or {}; ext=gc.get('external_specification')
        if isinstance(ext,dict):
            affected |= extract_explicit_reads(ext,schema_paths)
        targets=set()
        for p in affected:
            candidates=[p]
            # include parent/child ownership relations
            candidates += [q for q in depmap if q.startswith(p+'.') or p.startswith(q+'.')]
            for q in candidates: targets.update((depmap.get(q) or {}).get('owners') or [])
        # A canonical failure route is itself grounded recovery evidence even when
        # the gate has no state reads (common for deterministic/human routers).
        for route in e.get('routes') or []:
            if isinstance(route,dict) and str(route.get('key') or '').lower() in {'on_fail','fail','failed','revise'} and route.get('target') in elements:
                targets.add(route.get('target'))
        targets.discard(eid)
        e['recovery']['derived_allowed_targets']=sorted(targets)
        e['recovery']['affected_state_basis']=sorted(affected)

    regions=[]; membership=defaultdict(list)
    for r in (doc.get('graph_contract') or {}).get('allowed_cycle_regions',[]) or []:
        rid=r.get('id'); nodes=[x for x in (r.get('nodes') or []) if x in elements]
        for n in nodes: membership[n].append(rid)
        region_state=set(); resources=set()
        for n in nodes:
            e=elements[n]; region_state.update(e['state_contract']['reads_hint']); region_state.update(e['state_contract']['writes']); region_state.update(e['state_contract'].get('semantic_objects') or []); resources.update(e['resources'])
        internal_edges=sum(1 for n in nodes for t in graph_out.get(n,[]) if t in set(nodes))
        possible_internal_edges=len(nodes)*(len(nodes)-1) if len(nodes)>1 else 0
        region_metrics={
            'element_count':len(nodes),
            'delegation_budget':REGION_ELEMENT_BUDGET,
            'over_budget_by':max(0,len(nodes)-REGION_ELEMENT_BUDGET),
            'internal_edge_count':internal_edges,
            'internal_edge_density':round(internal_edges/possible_internal_edges,6) if possible_internal_edges else 0.0,
        }
        regions.append({'id':rid,'purpose':r.get('purpose'),'element_ids':nodes,'dynamic_return_targets_policy':r.get('dynamic_return_targets_policy'),'semantic_context':{'state_objects':sorted({p.split('.')[0] for p in region_state}),'resources':sorted(resources),'history_policy':'persistent_region_thread'},'metrics':region_metrics,'delegation':{'mode':'model_region_candidate' if len(nodes)<=REGION_ELEMENT_BUDGET else 'not_delegatable_budget_exceeded','eligible':len(nodes)<=REGION_ELEMENT_BUDGET,'canonical_graph_remains_authoritative':True,'runtime_validates_every_state_patch':True}})
    for eid in elements: elements[eid]['region_ids']=sorted(membership.get(eid,[]))

    assertions=copy.deepcopy(doc.get('assertions') or [])
    all_resource_refs=sorted({r for e in elements.values() for r in e.get('resources',[])})
    resource_catalog={}
    for r in all_resource_refs:
        rp=package_root/r; item={'path':r,'sha256':sha256_file(rp),'bytes':rp.stat().st_size}
        if rp.suffix.lower() in ('.yaml','.yml'):
            try: item['structured_content']=yaml.safe_load(rp.read_text(encoding='utf-8'))
            except Exception: pass
        elif rp.suffix.lower()=='.json':
            try: item['structured_content']=json.loads(rp.read_text(encoding='utf-8'))
            except Exception: pass
        resource_catalog[r]=item

    # Bind canonical collection schemas into per-element output contracts.
    table_bindings=table_schema_bindings({k:v.get('structured_content') for k,v in resource_catalog.items() if v.get('structured_content') is not None})
    for eid,e in elements.items():
        if e.get('kind','').endswith('_gate'): continue
        oc=e.get('output_contract') or {}; sp=oc.get('state_patch') or {}; operations=sp.get('operations') or {}; items=operations.get('items') or {}
        by_path={}
        variants=[]
        for w in e['state_contract']['writes']:
            schema=None
            for tp,ts in table_bindings.items():
                if w==tp or w.startswith(tp+'.') or tp.startswith(w+'.'):
                    schema=copy.deepcopy(ts); break
            if schema is not None:
                by_path[w]=schema
                base_props={'basis':{'type':['string','null'],'enum':['analyst_input','confirmed_state','derived','generated','recovery','legacy_unknown',None]},'reason':{'type':['string','null']},'row_key':{'type':['string','null']},'row_match':{'type':['string','number','integer','boolean','null']}}
                if isinstance(schema, dict) and schema.get('type') == 'array' and isinstance(schema.get('items'), dict):
                    row_schema=copy.deepcopy(schema['items'])
                    append_props={'op':{'const':'append'},'path':{'const':w},'value':row_schema,**copy.deepcopy(base_props)}
                    variants.append({'type':'object','required':['op','path','value','basis','reason','row_key','row_match'],'properties':append_props,'additionalProperties':False})
                    merge_props={'op':{'const':'merge_row'},'path':{'const':w},'value':copy.deepcopy(row_schema),**copy.deepcopy(base_props)}
                    merge_props['row_key']={'type':'string','minLength':1}
                    merge_props['row_match']={'type':['string','number','integer','boolean']}
                    variants.append({'type':'object','required':['op','path','value','basis','reason','row_key','row_match'],'properties':merge_props,'additionalProperties':False})
                    if w not in RELEASE1_APPEND_ONLY_COLLECTION_PATHS:
                        set_props={'op':{'enum':['set','replace']},'path':{'const':w},'value':copy.deepcopy(schema),**copy.deepcopy(base_props)}
                        variants.append({'type':'object','required':['op','path','value','basis','reason','row_key','row_match'],'properties':set_props,'additionalProperties':False})
                else:
                    props={'op':{'enum':['set','replace','append','merge','merge_deep','merge_row','remove']},'path':{'const':w},'value':schema,**copy.deepcopy(base_props)}
                    variants.append({'type':'object','required':['op','path','value','basis','reason','row_key','row_match'],'properties':props,'additionalProperties':False})
        # Do not let global resource binding erase writes that have no canonical
        # table schema.  Mixed bound/unbound elements must preserve a complete
        # StatePatch contract for every declared write.  Unbound values retain the
        # generic value shape already used by the base node contract; runtime may
        # validate more strongly only when the compiler actually declares it.
        generic_value_schema={'type':['string','number','integer','boolean','object','array','null']}
        base_props={'basis':{'type':['string','null'],'enum':['analyst_input','confirmed_state','derived','generated','recovery','legacy_unknown',None]},'reason':{'type':['string','null']},'row_key':{'type':['string','null']},'row_match':{'type':['string','number','integer','boolean','null']}}
        for w in e['state_contract']['writes']:
            if w in by_path:
                continue
            schema=_declared_schema_for_path(w,declared_state_types)
            if schema is None:
                ok,default=_state_default_at_path(state_schema,w)
                if ok: schema=_schema_from_default(default)
            if schema is None:
                schema=copy.deepcopy(generic_value_schema)
                untyped_write_paths.add(w)
            by_path[w]=copy.deepcopy(schema)
            props={'op':{'enum':['set','replace','append','merge','merge_deep','merge_row']},'path':{'const':w},'value':copy.deepcopy(schema),**copy.deepcopy(base_props)}
            variants.append({'type':'object','required':['op','path','value','basis','reason','row_key','row_match'],'properties':props,'additionalProperties':False})

        if e['state_contract']['writes']:
            oc['state_patch']['value_schema_by_path']=by_path
            oc['state_patch']['operation_variants']=variants
            # Bind the same operation-aware shapes into the provider response JSON
            # schema. Runtime and provider schema therefore share one complete
            # operation_variants contract, including unbound declared writes.
            try:
                op_container=oc['json_schema']['properties']['state_patch']['properties']['operations']
                op_container['items']={'anyOf':copy.deepcopy(variants)}
            except Exception:
                pass

    for _path in sorted(untyped_write_paths):
        compilation_issues.append({'severity':'warning','code':'UNTYPED_WRITE_PATH','path':_path,'detail':'write path has no canonical table schema, registry value_schema/type, or inferable non-null state default; runtime value validation remains generic'})

    r3_required_path_survivability=_r3_required_path_survivability(elements,r2_dependency_analysis,graph_out)
    compilation_issues.extend(copy.deepcopy(r3_required_path_survivability.get('findings') or []))
    r3_state_ownership=_r3_state_ownership_contract(elements)

    # Compiler-level graph integrity evidence; independent verifier performs YAML↔plan equality.
    entry=(doc.get('graph_contract') or {}).get('entry_node')
    reachable=reachable_from(entry,graph_out) if entry in elements else set()
    if len(reachable)!=len(elements):
        compilation_issues.append({'severity':'error','code':'GRAPH_NOT_FULLY_REACHABLE','reachable':len(reachable),'total':len(elements),'unreachable':sorted(set(elements)-reachable)})
    for eid,e in elements.items():
        if e['kind']!='terminal' and not e.get('routes'):
            compilation_issues.append({'severity':'error','code':'NONTERMINAL_WITHOUT_ROUTE','element_id':eid})
    for reg in regions:
        metrics=reg.get('metrics') or {}
        if metrics.get('element_count',0)>REGION_ELEMENT_BUDGET:
            compilation_issues.append({
                'severity':'warning',
                'code':'REGION_ELEMENT_BUDGET_EXCEEDED',
                'region_id':reg.get('id'),
                'message':'large semantic region detected; review recommended, execution remains valid',
                'element_count':metrics.get('element_count'),
                'budget':REGION_ELEMENT_BUDGET,
                'over_budget_by':metrics.get('over_budget_by'),
                'internal_edge_count':metrics.get('internal_edge_count'),
                'internal_edge_density':metrics.get('internal_edge_density'),
                'effect':'region_not_delegatable_as_single_model_region',
            })

    plan={
        'format':FORMAT,'format_version':FORMAT_VERSION,'compiler_version':COMPILER_VERSION,'yaml_semantics_contract':'ordo_yaml_semantics/v1','generated_at':datetime.now(timezone.utc).isoformat(),
        'source':{'program':str(program_path.relative_to(package_root)),'sha256':sha256_bytes(raw)},
        'validation':{'structural_status':'PASS' if not any(i.get('severity')=='error' and i.get('code') in {'GRAPH_NOT_FULLY_REACHABLE','NONTERMINAL_WITHOUT_ROUTE','UNKNOWN_ELEMENT_KIND','CLASSIFICATION_CONFLICT'} for i in compilation_issues) else 'FAIL','semantic_status':'FAIL' if any(i.get('severity')=='error' and i.get('code') not in {'GRAPH_NOT_FULLY_REACHABLE','NONTERMINAL_WITHOUT_ROUTE','UNKNOWN_ELEMENT_KIND','CLASSIFICATION_CONFLICT'} for i in compilation_issues) else 'PASS','blocking_issue_codes':['CLASSIFICATION_CONFLICT','UNKNOWN_ELEMENT_KIND'],'compilation_issues':compilation_issues},
        'runtime_model':{'architecture':'model-heavy-semantics-code-heavy-guarantees','graph_role':'guidance_and_authority_boundary_not_rigid_replay_corridor','normal_model_context':'broad_semantic_objects','normal_yaml_fallback':False,'semantic_repair_heuristics':False,'model_output_commit':'state_patch_only_after_runtime_validation','recovery':'GateFailure -> RecoveryPlan -> local repair/clarification/detour -> revalidate origin gate'},
        'interaction_contract':interaction_contract,
        'runtime_execution_contract':{'instruction_assembler':'runtime_semantic_v1','semantic_task_source':'elements.*.semantic_source','strip_runtime_graph_mechanics':True,'state_context':'broad_semantic_objects_or_full_canonical','result_adapter':'alpha20_node_gate_result_v1','no_silent_yaml_llm_fallback':True,'input_context_contract':{'state':'canonical state.schema','runtime':'execution/run context','interaction':'analyst/session context','recovery':'gate/recovery context','metadata':'playbook/engine metadata','reserved_roots':{k:sorted(v) for k,v in INPUT_CONTEXT_CLASSES.items()}}},
        'runtime_tools':{'read_state':{'enabled':True,'write':False},'read_resource':{'enabled':True,'write':False},'propose_state_patch':{'enabled':True,'validated':True},'ask_analyst':{'enabled':True},'request_route':{'enabled':True,'validated_against_element_routes':True},'report_gate_failure':{'enabled':True,'schema':'GateFailure'}},
        'graph':{'entry_node':(doc.get('graph_contract') or {}).get('entry_node'),'external_terminal_targets':copy.deepcopy((doc.get('graph_contract') or {}).get('external_terminal_targets') or []),'alias_policy':copy.deepcopy((doc.get('graph_contract') or {}).get('alias_policy')),'regions':regions},
        'state':{'schema':copy.deepcopy(state_schema),'schema_paths':sorted(schema_paths),'dependency_map':depmap,'r2_dependency_analysis':r2_dependency_analysis,'gate_state_contract_analysis':gate_state_contract_analysis,'r3_required_path_survivability':r3_required_path_survivability,'r3_state_ownership':r3_state_ownership,'provenance_policy':'confirmed analyst data must retain provenance and must not be silently overwritten'},
        'elements':elements,'resources':resource_catalog,'assertions':assertions,
        'contracts':{'NodeExecutionResult':'schemas/NodeExecutionResult.schema.json','StatePatch':'schemas/StatePatch.schema.json','GateFailure':'schemas/GateFailure.schema.json','RecoveryPlan':'schemas/RecoveryPlan.schema.json','RevisitContext':'schemas/RevisitContext.schema.json','RecoverySession':'schemas/RecoverySession.schema.json'}
    }
    return plan


def main():
    ap=argparse.ArgumentParser(description='Compile Ordo YAML into alpha.20 Runtime Semantic Plan V7.12')
    ap.add_argument('input',help='program.ordo.yaml or playbook package directory'); ap.add_argument('-o','--output',required=True); args=ap.parse_args()
    inp=Path(args.input).resolve()
    if inp.is_dir():
        candidates=list(inp.rglob('program.ordo.yaml'))
        if len(candidates)!=1: raise SystemExit(f'Expected exactly one program.ordo.yaml, found {len(candidates)}')
        program=candidates[0]; package_root=inp
    else:
        program=inp; package_root=program.parent.parent if program.parent.name=='source' else program.parent
    plan=compile_plan(program,package_root); out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','output':str(out),'elements':len(plan['elements']),'regions':len(plan['graph']['regions']),'state_paths':len(plan['state']['dependency_map']),'compilation_issues':len(plan['validation']['compilation_issues'])},ensure_ascii=False))
if __name__=='__main__': main()
