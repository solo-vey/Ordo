#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

MODEL_START=['START_HERE_MODEL_MODE.md','START_PROMPT_MODEL_MODE.md']
AUTHORING_PREFIXES=('authoring/','authoring_templates/','design/','verification/','tests/')

def size(p:Path)->int:
    try:return p.stat().st_size if p.is_file() else 0
    except OSError:return 0

def classify(rel:str)->str:
    if rel.startswith(('authoring/','authoring_templates/','design/')): return 'authoring_editor_only'
    if rel.startswith(('verification/','tests/','reports/')): return 'release_validation_only'
    if rel.startswith(('cli_embedded/','compiled/')): return 'strict_cli_runtime'
    if rel.startswith('tools/'):
        return 'release_validation_only' if Path(rel).name.startswith(('test_','validate_','verify_')) else 'deterministic_runtime'
    if rel.startswith(('knowledge/','canonical_support/guides/')): return 'model_runtime_lazy'
    if rel in MODEL_START or rel=='source/program.ordo.yaml' or rel=='ordo.yml': return 'model_runtime_required'
    return 'model_runtime_lazy'

def audit(root:Path, startup_read_log:Path|None=None, active_node:str|None=None)->dict:
    root=root.resolve(); files=[p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.pyc')]
    rows=[]; totals={}
    for p in files:
        rel=p.relative_to(root).as_posix(); c=classify(rel); b=size(p); totals[c]=totals.get(c,0)+b; rows.append((rel,c,b))
    source=root/'source/program.ordo.yaml'; static_source_bytes=size(source)
    startup_loaded_bytes=sum(size(root/x) for x in MODEL_START)
    node_prompt_loaded_bytes=None; node_knowledge_loaded_bytes=None; declared_prompt_ref_bytes=0; declared_knowledge_ref_bytes=0; active_prompt_bytes=0; active_knowledge_bytes=0; inline_prompt_bytes=0; large_inline=[]
    if source.is_file():
        d=yaml.safe_load(source.read_text(encoding='utf-8')) or {}
        for rec in list(d.get('nodes') or [])+list(d.get('gates') or []):
            if not isinstance(rec,dict): continue
            for k in ('question','purpose','description'):
                v=rec.get(k)
                if isinstance(v,str):
                    n=len(v.encode('utf-8')); inline_prompt_bytes+=n
                    if n>=4096: large_inline.append({'id':rec.get('id'),'field':k,'bytes':n})
            ctx=rec.get('node_context') or {}
            for ref in ctx.get('knowledge_refs') or []:
                p=root/str(ref)
                if p.is_file():
                    declared_knowledge_ref_bytes+=size(p)
                    if active_node and rec.get('id')==active_node: active_knowledge_bytes+=size(p)
            pref=ctx.get('prompt_ref')
            if pref and (root/str(pref)).is_file():
                declared_prompt_ref_bytes+=size(root/str(pref))
                if active_node and rec.get('id')==active_node: active_prompt_bytes+=size(root/str(pref))
        if active_node:
            node_prompt_loaded_bytes=active_prompt_bytes
            node_knowledge_loaded_bytes=active_knowledge_bytes
    startup_audit={'status':'NOT_OBSERVED','loaded_files':[],'loaded_bytes':None,'forbidden_reads':[]}
    if startup_read_log and startup_read_log.is_file():
        loaded=[]; forb=[]; total=0
        for line in startup_read_log.read_text(encoding='utf-8',errors='ignore').splitlines():
            try:r=json.loads(line)
            except Exception:continue
            if not r.get('loaded_into_model_context',r.get('model_visible',False)): continue
            rel=str(r.get('path','')); b=int(r.get('bytes',0) or 0); loaded.append(rel); total+=b
            if rel.startswith(AUTHORING_PREFIXES): forb.append(rel)
        startup_audit={'status':'OBSERVED','loaded_files':loaded,'loaded_bytes':total,'forbidden_reads':sorted(set(forb))}
    pkg=sum(x[2] for x in rows)
    metrics={
        'static_source_bytes':static_source_bytes,
        'startup_loaded_bytes':startup_loaded_bytes if startup_audit['loaded_bytes'] is None else startup_audit['loaded_bytes'],
        'node_prompt_loaded_bytes':node_prompt_loaded_bytes,
        'node_knowledge_loaded_bytes':node_knowledge_loaded_bytes,
        'model_visible_tool_output_bytes':None,
        'package_bytes':pkg,
        'platform_overhead_tokens':None,
        'inline_prompt_bytes':inline_prompt_bytes,
        'declared_prompt_reference_bytes':declared_prompt_ref_bytes,
        'declared_knowledge_reference_bytes':declared_knowledge_ref_bytes,
        'active_node':active_node,
        'estimated_static_source_tokens':round(static_source_bytes/4),
        'token_count_source':'ESTIMATED_UTF8_BYTES_DIV_4'
    }
    report={'status':'PASS','metrics':metrics,'asset_bytes_by_consumer':totals,'startup_read_audit':startup_audit,'large_inline_prompt_opportunities':large_inline,'score_effect':0}
    updates={'context_runtime_efficiency_evidence':report,'context_runtime_asset_classification':totals,'context_runtime_startup_read_audit':startup_audit}
    return {'schema_version':'state_updates_v1','report':report,'state_updates':updates}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--startup-read-log'); ap.add_argument('--active-node'); ap.add_argument('--out'); a=ap.parse_args()
    result=audit(Path(a.root),Path(a.startup_read_log) if a.startup_read_log else None,a.active_node)
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if a.out: Path(a.out).write_text(text,encoding='utf-8')
    print(text,end=''); return 0
if __name__=='__main__': raise SystemExit(main())
