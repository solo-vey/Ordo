#!/usr/bin/env python3
from __future__ import annotations
import argparse,re
from pathlib import Path
from _alpha26_validation_common import load_json,source_program,emit

def safe_rel(s:str)->bool:
    if not s: return False
    p=Path(s)
    return (not p.is_absolute()) and ('..' not in p.parts)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('package'); a=ap.parse_args(); root=Path(a.package)
    program=source_program(root) or {}; errors=[]; warnings=[]
    nodes={str(x.get('id')):x for x in (program.get('nodes') or []) if isinstance(x,dict) and x.get('id')}
    reg=load_json(root/'verification/ARTIFACT_MATERIALIZATION_REGISTRY.json')
    outputs=[x for x in (program.get('outputs') or []) if isinstance(x,dict) and x.get('id')]
    registry_required=bool(outputs) or any(isinstance(n.get('artifact'),dict) or str(n.get('action') or '').upper().startswith(('PACKAGE.','DOCUMENT.')) for n in nodes.values())
    if reg is None:
        if registry_required: errors.append('verification/ARTIFACT_MATERIALIZATION_REGISTRY.json missing')
        return emit('VIBE_ARTIFACT_ARCHIVE_REGISTRY_COMPLETENESS',errors,warnings)
    items=[x for x in (reg.get('artifacts') or []) if isinstance(x,dict)]
    if registry_required and not items: errors.append('artifact registry has no artifacts')
    seen_ids=set(); seen_paths=set()
    for i,x in enumerate(items):
        aid=str(x.get('artifact_id') or '').strip(); path=str(x.get('output_path') or '').strip().replace('\\','/')
        typ=str(x.get('output_type') or '').strip().lower(); mode=str(x.get('materialization_mode') or '').strip().lower()
        ctx=x.get('content_contract') if isinstance(x.get('content_contract'),dict) else {}
        prefix=f'artifact[{i}] {aid or "<missing-id>"}'
        if not aid: errors.append(f'{prefix}: artifact_id required')
        elif aid in seen_ids: errors.append(f'{prefix}: duplicate artifact_id')
        seen_ids.add(aid)
        if not path: errors.append(f'{prefix}: output_path required')
        elif not safe_rel(path): errors.append(f'{prefix}: output_path must be safe package-relative: {path}')
        elif path in seen_paths: errors.append(f'{prefix}: duplicate output_path {path}')
        seen_paths.add(path)
        if not typ: errors.append(f'{prefix}: output_type required')
        if mode not in {'template','assembler','builder','generated'}: errors.append(f'{prefix}: materialization_mode must be explicit')
        tref=str(x.get('template_path') or '').strip()
        bref=str(x.get('assembler_ref') or x.get('builder_ref') or '').strip()
        if mode=='template' and not tref: errors.append(f'{prefix}: template_path required for template mode')
        if mode in {'assembler','builder'} and not bref: errors.append(f'{prefix}: assembler_ref/builder_ref required')
        for label,ref in [('template_path',tref),('assembler_ref',bref)]:
            if ref and ('/' in ref or ref.endswith(('.py','.json','.yaml','.yml','.md'))) and not (root/ref).is_file(): errors.append(f'{prefix}: {label} does not exist: {ref}')
        mid=str(x.get('materialization_node_id') or '').strip()
        if not mid: errors.append(f'{prefix}: materialization_node_id required')
        elif nodes and mid not in nodes: errors.append(f'{prefix}: unknown materialization_node_id {mid}')
        elif mid in nodes and path:
            n=nodes[mid]; npath=str(((n.get('artifact') or {}).get('expected_path') if isinstance(n.get('artifact'),dict) else '') or n.get('output') or '').replace('\\','/')
            if npath and npath!=path: errors.append(f'{prefix}: registry output_path {path} != producer path {npath}')
        validators=[str(v).strip() for v in (x.get('validators') or []) if isinstance(v,str) and str(v).strip()]
        if bool(x.get('post_materialization_validation_required')) and not validators:
            errors.append(f'{prefix}: post-materialization validator required')
        for vref in validators:
            if ('/' in vref or vref.endswith(('.py','.json','.yaml','.yml'))) and not (root/vref).is_file(): errors.append(f'{prefix}: validator does not exist: {vref}')
        archive=typ in {'archive','package','zip'} or path.lower().endswith('.zip')
        if archive:
            members=[str(v).replace('\\','/') for v in (ctx.get('required_members') or []) if isinstance(v,str) and str(v).strip()]
            if not members: errors.append(f'{prefix}: archive required_members required')
            elif len(members)!=len(set(members)): errors.append(f'{prefix}: duplicate archive required_members')
            for m in members:
                if not safe_rel(m): errors.append(f'{prefix}: unsafe required member {m}')
            if 'forbidden_members' not in ctx or not isinstance(ctx.get('forbidden_members'),list):
                errors.append(f'{prefix}: forbidden_members policy must be explicitly declared (may be empty)')
            hashes=ctx.get('member_hashes') if isinstance(ctx.get('member_hashes'),dict) else {}
            archive_hash=x.get('sha256') or ctx.get('sha256') or ctx.get('archive_sha256')
            dynamic=ctx.get('dynamic_hash_validation') if isinstance(ctx.get('dynamic_hash_validation'),dict) else {}
            dynamic_ok=bool(str(dynamic.get('mode') or '').strip() and str(dynamic.get('validator_ref') or '').strip())
            if not hashes and not archive_hash and not dynamic_ok:
                errors.append(f'{prefix}: archive hash contract required (member_hashes, archive sha256, or explicit dynamic_hash_validation)')
            for m,h in hashes.items():
                if members and m not in members: errors.append(f'{prefix}: hashed member {m} is not in required_members')
                if not isinstance(m,str) or not safe_rel(m): errors.append(f'{prefix}: invalid member_hashes key {m}')
                if not isinstance(h,str) or not re.fullmatch(r'[0-9a-fA-F]{64}',h): errors.append(f'{prefix}: invalid sha256 for member {m}')
            if dynamic and not dynamic_ok: errors.append(f'{prefix}: dynamic_hash_validation requires mode + validator_ref')
    # Every declared output should have one registry entry by id when outputs are first-class.
    reg_ids={str(x.get('artifact_id') or '') for x in items}
    for o in outputs:
        oid=str(o.get('id') or '')
        if oid and oid not in reg_ids: errors.append(f'declared output {oid}: artifact registry entry missing')
    return emit('VIBE_ARTIFACT_ARCHIVE_REGISTRY_COMPLETENESS',errors,warnings,{'artifacts_checked':len(items),'outputs_checked':len(outputs)})
if __name__=='__main__': raise SystemExit(main())
