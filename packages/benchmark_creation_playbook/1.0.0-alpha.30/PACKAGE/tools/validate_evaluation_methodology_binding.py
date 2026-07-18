#!/usr/bin/env python3
from pathlib import Path
import argparse,json,hashlib,sys

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(o): return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def compile_effective(root,profile):
    forbidden=set(root.get("forbidden_profile_changes",[]))
    requested=set(profile.get("overrides",[]))
    bad=sorted(forbidden & requested)
    errors=[]
    inh=profile.get("inherits",{})
    if inh.get("methodology_id")!=root.get("methodology_id") or inh.get("version")!=root.get("version"):
        errors.append("INHERITANCE_MISMATCH")
    if bad: errors.append("FORBIDDEN_OVERRIDES:"+",".join(bad))
    docs=profile.get("canonical_documents",root.get("default_documents",[]))
    total=sum(float(x.get("weight",0)) for x in docs)
    if abs(total-1.0)>1e-9: errors.append("DOCUMENT_WEIGHTS_MUST_SUM_TO_1")
    eff={"root":root,"profile":profile,"resolved":{"canonical_documents":docs,"expected_terminal_states":profile.get("expected_terminal_states",{}),"scenario_specific_checks":profile.get("scenario_specific_checks",[]),"caps":profile.get("caps",[])}}
    return eff,errors

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--methodology',required=True); ap.add_argument('--profile',required=True); ap.add_argument('--audit'); ap.add_argument('--out',required=True); a=ap.parse_args()
    r=load(a.methodology); p=load(a.profile); eff,errs=compile_effective(r,p)
    binding={"methodology_version":r.get("version"),"methodology_sha256":sha(a.methodology),"profile_version":p.get("version"),"profile_sha256":sha(a.profile),"effective_methodology_sha256":hashlib.sha256(canonical(eff).encode()).hexdigest()}
    if a.audit:
        audit=load(a.audit); ab=audit.get("methodology_binding",{})
        for k,v in binding.items():
            if ab.get(k)!=v: errs.append("AUDIT_BINDING_MISMATCH:"+k)
    out={"status":"PASS" if not errs else "FAIL","errors":errs,"methodology_binding":binding,"effective_methodology":eff}
    Path(a.out).write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')
    return 0 if not errs else 2
if __name__=='__main__': raise SystemExit(main())
