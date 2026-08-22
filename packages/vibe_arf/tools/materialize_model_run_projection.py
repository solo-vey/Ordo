#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re, shutil
from pathlib import Path

FORBIDDEN_PREFIXES=('authoring/','verification/','tests/','editor/','compiled/','cli_embedded/')
PATH_RE=re.compile(r'(?<![A-Za-z0-9_])((?:source|authoring|authoring_templates|patterns|verification|tools|language|dependencies|cli_embedded|portable_overrides|canonical_support|utilities|analyst_context|compiled|tests|reports|editor)/[A-Za-z0-9_./-]+)')

def sha_bytes(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def sha_file(p:Path)->str:return sha_bytes(p.read_bytes())

def project(root:Path,out:Path):
    root=root.resolve(); out=out.resolve()
    if out.exists(): shutil.rmtree(out)
    shutil.copytree(root,out)
    src=root/'source/program.ordo.yaml'
    text=src.read_text()
    mappings=[]
    def repl(m):
        raw=m.group(1); rel=raw.rstrip('.,;:)"\'')
        if not rel.startswith(FORBIDDEN_PREFIXES): return raw
        target='model_support/'+rel
        p=root/rel
        if p.is_file():
            dst=out/target; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,dst)
            mappings.append({'source_path':rel,'projected_path':target,'sha256':sha_file(p),'materialization':'exact_copy'})
        else:
            mappings.append({'source_path':rel,'projected_path':target,'sha256':None,'materialization':'unresolved_reference_preserved'})
        return target + raw[len(rel):]
    projected=PATH_RE.sub(repl,text)
    (out/'source/program.ordo.yaml').write_text(projected)
    # Remove original forbidden surfaces from projection so accidental inclusion is impossible.
    for pref in FORBIDDEN_PREFIXES:
        p=out/pref.rstrip('/')
        if p.is_dir(): shutil.rmtree(p)
        elif p.exists(): p.unlink()
    uniq={x['source_path']:x for x in mappings}
    manifest={
      'schema_version':'1.0','contract_id':'MODEL_RUN_SUPPORT_PROJECTION',
      'canonical_source_path':'source/program.ordo.yaml','canonical_source_sha256':sha_file(src),
      'projected_source_path':'source/program.ordo.yaml','projected_source_sha256':sha_file(out/'source/program.ordo.yaml'),
      'rule':'forbidden EDIT/test/compiled references are remapped to exact-copy model_support projections; canonical source is unchanged',
      'mappings':[uniq[k] for k in sorted(uniq)],
      'resolved_count':sum(1 for x in uniq.values() if x['sha256']),
      'unresolved_count':sum(1 for x in uniq.values() if not x['sha256'])}
    (out/'MODEL_RUN_SUPPORT_PROJECTION.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    return manifest

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('output'); a=ap.parse_args()
    m=project(Path(a.root),Path(a.output)); print(json.dumps({'status':'PASS','resolved':m['resolved_count'],'unresolved':m['unresolved_count'],'projection_sha256':m['projected_source_sha256']},indent=2))
if __name__=='__main__':main()
