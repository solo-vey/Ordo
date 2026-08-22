#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
PATH_RE=re.compile(r'(?<![A-Za-z0-9_])((?:source|authoring|authoring_templates|patterns|verification|tools|language|dependencies|cli_embedded|portable_overrides|canonical_support|utilities|analyst_context|compiled|tests|reports|model_support)/[A-Za-z0-9_./-]+)')
BOOT={
 'CLI_RUN':['ordo.yml','ordo.lock.json','source/program.ordo.yaml','START_HERE_CLI_RUN.md','START_PROMPT_CLI_RUN.md','DISTRIBUTION_PACKAGE_CONTRACT.json','analyst_context/context_catalog.json'],
 'MODEL_RUN':['ordo.yml','ordo.lock.json','source/program.ordo.yaml','START_HERE_MODEL_MODE.md','START_PROMPT_MODEL_MODE.md','DISTRIBUTION_PACKAGE_CONTRACT.json','analyst_context/context_catalog.json']}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build_closure(root,profile):
    root=Path(root).resolve(); c=json.loads((root/'DISTRIBUTION_PACKAGE_CONTRACT.json').read_text()); pc=c['profiles'][profile]
    forbidden=tuple(pc.get('forbidden_prefixes',[])); tokens=tuple(x.lower() for x in pc.get('forbidden_name_tokens',[])); q=[]; reasons={}; rejected=[]
    def add(rel,reason):
        rel=rel.rstrip('.,;:)"\'')
        if any(rel.startswith(p) for p in forbidden) or any(t in rel.lower() for t in tokens):
            rejected.append({'path':rel,'reason':reason}); return
        p=root/rel
        if p.is_file():
            if rel not in reasons: q.append(rel); reasons[rel]=[]
            if reason not in reasons[rel]: reasons[rel].append(reason)
    for rel in BOOT[profile]: add(rel,'bootstrap')
    if profile=='CLI_RUN':
        for rel in ['cli_embedded/ordo','compiled/program.ir.json','compiled/targets.manifest.json']:
            add(rel,'strict_runtime_bootstrap')
    i=0
    while i<len(q):
        rel=q[i]; i+=1; p=root/rel
        try: text=p.read_text(errors='ignore')
        except Exception: text=''
        for m in PATH_RE.finditer(text): add(m.group(1),f'explicit_ref:{rel}')
        if rel.endswith('.py'):
            for mod in re.findall(r'^\s*(?:from|import)\s+([A-Za-z0-9_.]+)',text,re.M): add('tools/'+mod.split('.')[-1]+'.py',f'python_import:{rel}')
    rows=[{'path':rel,'sha256':sha(root/rel),'reasons':reasons[rel],'materialization':'copy'} for rel in sorted(reasons)]
    return {'schema_version':'2.0','contract_id':profile+'_PACKAGE_DEPENDENCY_CLOSURE','profile':profile,'algorithm':'consumer_aware_transitive_dependency_closure','file_count':len(rows),'files':rows,'rejected_forbidden_references':rejected}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('--profile',required=True,choices=['CLI_RUN','MODEL_RUN']); ap.add_argument('--output'); a=ap.parse_args(); d=build_closure(a.root,a.profile); out=a.output or (a.profile+'_PACKAGE_DEPENDENCY_CLOSURE.json'); Path(a.root,out).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n'); print(json.dumps({'status':'PASS','files':d['file_count'],'rejected':len(d['rejected_forbidden_references']),'output':out},indent=2))
if __name__=='__main__': main()
