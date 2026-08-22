#!/usr/bin/env python3
from __future__ import annotations
import argparse,re
from pathlib import Path
from _alpha26_validation_common import source_program,emit

def owner(n):
    ec=n.get('execution_contract') if isinstance(n.get('execution_contract'),dict) else {}
    o=str(ec.get('owner') or '').lower(); rx=str(ec.get('runtime_executor') or '').lower()
    if rx=='package_tool' or o in {'deterministic','machine','tool'}: return 'deterministic'
    ic=str(((n.get('node_context') or {}).get('interaction_class') or '')).upper()
    if ic=='MACHINE_INTERNAL': return 'deterministic'
    action=str(n.get('action') or '').upper()
    if action.startswith(('PACKAGE.','DOCUMENT.','CLI.','PYTHON.')): return 'deterministic'
    return o or 'unknown'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('package'); a=ap.parse_args(); root=Path(a.package)
    p=source_program(root) or {}; errors=[]; warnings=[]
    nodes=[x for x in (p.get('nodes') or []) if isinstance(x,dict) and x.get('id')]
    gates=[x for x in (p.get('gates') or []) if isinstance(x,dict) and x.get('id')]
    for n in nodes:
        nid=str(n.get('id')); ec=n.get('execution_contract') if isinstance(n.get('execution_contract'),dict) else {}
        rx=str(ec.get('runtime_executor') or '').lower(); det=owner(n)=='deterministic'
        if not det: continue
        # Strict generated-profile rule only for explicit package-tool execution or materialization actions.
        materialization=str(n.get('action') or '').upper().startswith(('PACKAGE.','DOCUMENT.')) or isinstance(n.get('artifact'),dict)
        if rx=='package_tool' or materialization:
            if rx!='package_tool':
                errors.append(f'{nid}: deterministic package/materialization node must declare execution_contract.runtime_executor=package_tool')
            tool=str(n.get('tool_ref') or '').strip()
            if not tool: errors.append(f'{nid}: package_tool node requires tool_ref')
            elif Path(tool).is_absolute() or '..' in Path(tool).parts: errors.append(f'{nid}: tool_ref must be safe package-relative: {tool}')
            elif not (root/tool).is_file(): errors.append(f'{nid}: tool_ref does not exist: {tool}')
            effect=bool(n.get('writes')) or bool(n.get('output')) or (isinstance(n.get('artifact'),dict) and bool(n['artifact'].get('state_path')))
            if not effect: errors.append(f'{nid}: deterministic package_tool contract must declare writes/output/artifact.state_path')
            if isinstance(n.get('artifact'),dict):
                art=n['artifact']; sp=str(art.get('state_path') or '').strip(); ep=str(art.get('expected_path') or n.get('output') or '').strip()
                if not sp: errors.append(f'{nid}: artifact.state_path required')
                if not ep: errors.append(f'{nid}: artifact.expected_path/output required')
                if n.get('output') and art.get('expected_path') and str(n.get('output')).replace('\\','/')!=str(art.get('expected_path')).replace('\\','/'):
                    errors.append(f'{nid}: output and artifact.expected_path disagree')
            route=bool(n.get('next')) or bool(n.get('on_answer')) or bool(n.get('transitions'))
            if not route: errors.append(f'{nid}: deterministic node has no explicit route')
    for g in gates:
        gid=str(g.get('id')); m=str(g.get('method') or '').lower(); tc=str(g.get('trust_class') or '').lower()
        if m=='mechanical' or tc=='deterministic':
            if not str(g.get('condition') or g.get('assert') or '').strip(): errors.append(f'{gid}: deterministic gate requires executable condition/assert contract')
            if not str(g.get('on_pass') or '').strip(): errors.append(f'{gid}: deterministic gate requires on_pass')
            if not str(g.get('on_fail') or '').strip(): errors.append(f'{gid}: deterministic gate requires on_fail/fail-closed route')
            if m!='mechanical' or tc!='deterministic': errors.append(f'{gid}: deterministic gate must use method=mechanical + trust_class=deterministic')
    return emit('VIBE_DETERMINISTIC_CONTRACT_COMPLETENESS',errors,warnings,{'nodes_checked':len(nodes),'gates_checked':len(gates)})
if __name__=='__main__': raise SystemExit(main())
