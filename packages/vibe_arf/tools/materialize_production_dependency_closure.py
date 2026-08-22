#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import ast, hashlib, json, re, sys, fnmatch

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]).resolve()
CONTRACT = json.loads((ROOT/'PRODUCTION_PACKAGE_CONTRACT.json').read_text())
PREFIXES = tuple(CONTRACT.get('dependency_closure',{}).get('controlled_prefixes',[]))
FORBIDDEN_PATTERNS = tuple(pat for cls in CONTRACT.get('artifact_classes',[]) if cls.get('default_inclusion')=='forbidden' for pat in cls.get('patterns',[]))
reasons: dict[str,set[str]] = {}

def forbidden(rel:str)->bool:
    return any(fnmatch.fnmatch(rel,pat) or (pat.endswith('/**') and (rel==pat[:-3] or rel.startswith(pat[:-2]))) for pat in FORBIDDEN_PATTERNS)

def controlled(rel:str)->bool:
    return rel.startswith(PREFIXES)

def add(rel:str, reason:str)->bool:
    rel = rel.replace('\\','/').lstrip('./')
    p=ROOT/rel
    if forbidden(rel) or not controlled(rel) or not p.is_file(): return False
    before=len(reasons.get(rel,set()))
    reasons.setdefault(rel,set()).add(reason)
    return len(reasons[rel])>before

def add_tree(rel_dir:str, reason:str):
    d=ROOT/rel_dir
    if d.is_dir():
        for p in d.rglob('*'):
            if p.is_file(): add(p.relative_to(ROOT).as_posix(),reason)

# Canonical support manifest is an authoritative retained support inventory.
cm=ROOT/'canonical_support/CANONICAL_SUPPORT_MANIFEST.json'
if cm.is_file():
    add('canonical_support/CANONICAL_SUPPORT_MANIFEST.json','canonical_support_manifest_root')
    data=json.loads(cm.read_text())
    for row in data.get('files',[]):
        if isinstance(row,dict) and row.get('path'):
            add(row['path'],'canonical_support_manifest_entry')

# Runtime/editor roots whose dynamic loading cannot be soundly reconstructed from static imports alone.
add_tree('cli_embedded/ordo_pkg','embedded_runtime_dynamic_import_tree')
add_tree('utilities/ordo_tree_editor','editor_runtime_surface')

# Exact execution and verification roots.
vp=json.loads((ROOT/'verification_profile.json').read_text())
for c in vp.get('checks',[]):
    s=(c.get('args') or {}).get('script')
    if s: add(s,'verification_profile:'+str(c.get('id')))
rm=json.loads((ROOT/'verification/EXECUTION_RESPONSIBILITY_MAP.json').read_text())
for e in rm.get('entries',[]):
    for ref in e.get('tool_or_validator_refs') or []:
        if isinstance(ref,str): add(ref,'responsibility:'+str(e.get('element_id') or e.get('id')))
# Simulation/runtime exact dependency.
sim=ROOT/'verification/SIMULATION_KIT_DEPENDENCY.json'
if sim.is_file():
    dep=json.loads(sim.read_text()).get('path')
    if dep: add(dep,'declared_simulation_dependency')
# The closure must remain rematerializable in a production authoring package.
add('tools/materialize_production_dependency_closure.py','closure_materializer')
for _dual in ['tools/materialize_run_package_dependency_closure.py','tools/build_dual_playbook_distribution.py','tools/validate_distribution_package.py','tools/validate_dual_playbook_distribution.py','tools/test_dual_distribution_package_contract.py','tools/run_with_watchdog.py']:
    add(_dual,'dual_distribution_tooling')

PATH_RE=re.compile(r'(?<![A-Za-z0-9_])((?:tools|tests|canonical_support|dependencies|utilities|cli_embedded|portable_overrides|language)/[A-Za-z0-9_./+()\-]+)')
TEXT_EXT={'.py','.json','.yaml','.yml','.md','.txt','.toml','.ini','.cfg','.sh','.command'}

def explicit_refs(path:Path, reason_prefix:str):
    if path.suffix.lower() not in TEXT_EXT and path.name not in {'VERSION'}: return
    try: txt=path.read_text(errors='ignore')
    except Exception: return
    src=path.relative_to(ROOT).as_posix()
    for m in PATH_RE.finditer(txt):
        rel=m.group(1).rstrip('.,;:)]}')
        add(rel,f'{reason_prefix}:{src}')

def python_imports(path:Path):
    if path.suffix!='.py': return
    try: tree=ast.parse(path.read_text(errors='ignore'))
    except Exception: return
    src=path.relative_to(ROOT).as_posix()
    mods=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Import): mods += [a.name for a in n.names]
        elif isinstance(n,ast.ImportFrom) and n.module: mods.append(n.module)
    for mod in mods:
        parts=mod.split('.')
        candidates=[ROOT.joinpath(*parts).with_suffix('.py'), ROOT.joinpath(*parts,'__init__.py'), path.parent.joinpath(*parts).with_suffix('.py'), path.parent.joinpath(*parts,'__init__.py')]
        for c in candidates:
            if c.is_file():
                try: rel=c.relative_to(ROOT).as_posix()
                except ValueError: continue
                if add(rel,f'python_import:{src}'): pass
                break

# Discover explicit controlled dependencies from canonical non-controlled authoring/runtime contracts.
discovery=[]
for rel in ['README.md','AUTHORING_TOOLING.md','START_HERE.md','START_HERE_RUNTIME_MODE.md','START_PROMPT.md','START_PROMPT_RUNTIME_MODE.md']:
    p=ROOT/rel
    if p.is_file(): discovery.append(p)
for base in ['source','verification','authoring','editor']:
    d=ROOT/base
    if d.is_dir(): discovery.extend(p for p in d.rglob('*') if p.is_file())
for p in discovery: explicit_refs(p,'explicit_ref')

# Recursive closure over newly included controlled text/import dependencies.
seen=set()
while True:
    pending=[ROOT/r for r in sorted(reasons) if r not in seen]
    if not pending: break
    for p in pending:
        rel=p.relative_to(ROOT).as_posix(); seen.add(rel)
        explicit_refs(p,'explicit_ref')
        python_imports(p)

rows=[]
for rel in sorted(reasons):
    p=ROOT/rel
    rows.append({'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'reasons':sorted(reasons[rel])})
out={'schema_version':'1.1','contract_id':'PRODUCTION_DEPENDENCY_CLOSURE','algorithm':'declared_roots_plus_local_reachability','materializer':'tools/materialize_production_dependency_closure.py','file_count':len(rows),'files':rows}
(ROOT/'PRODUCTION_DEPENDENCY_CLOSURE.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'PASS','path':str(ROOT/'PRODUCTION_DEPENDENCY_CLOSURE.json'),'files':len(rows)},indent=2))
