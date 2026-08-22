#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path

def fp(x): return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def trans(op,s):
    s=dict(s or {})
    if op=='answer_dependency_propagation':
        ans=s.get('accepted_answer'); deps=s.get('dependent_parameters',{}) or {}; out={}
        if ans is not None:
            for k,v in deps.items():
                if isinstance(v,list):
                    for p in v: out[p]=ans.get(k) if isinstance(ans,dict) and k in ans else ans
        return {'status':'PASS','answer_propagation_record':out if ans is not None else {'status':'NO_NEW_ANSWER'}}
    if op=='dependency_closure':
        seeds=set(s.get('changed_refs',[]) or []); edges=s.get('traceability_edges',[]) or []; adj={}
        for e in edges: adj.setdefault(e.get('from'),set()).add(e.get('to'))
        seen=set(seeds); q=list(seeds)
        while q:
            a=q.pop(0)
            for b in adj.get(a,set()):
                if b not in seen: seen.add(b); q.append(b)
        return {'status':'PASS','change_dependency_closure':sorted(seen)}
    if op=='invalidation':
        closure=set(s.get('change_dependency_closure',[]) or []); reasons=s.get('change_reasons',{}) or {}
        return {'status':'PASS','invalidated_refs':[{'ref':x,'reason':reasons.get(x,'dependent_on_changed_state')} for x in sorted(closure)]}
    if op=='valid_state_preservation':
        allrefs=set(s.get('all_valid_refs',[]) or []); invalid={x.get('ref') if isinstance(x,dict) else x for x in (s.get('invalidated_refs',[]) or [])}
        return {'status':'PASS','preserved_valid_refs':sorted(allrefs-invalid)}
    if op=='merge_incremental_analyst_facts':
        allowed={'KNOWN','UNASKED','UNKNOWN_CONFIRMED','INAPPLICABLE'}
        fields={k:dict(v) for k,v in (s.get('canonical_fields') or {}).items()}
        conflicts=[]; merged=0; ignored=[]
        for fact in (s.get('incoming_facts') or []):
            if not isinstance(fact,dict) or not fact.get('field_id'):
                ignored.append({'reason':'INVALID_FACT_SHAPE','fact':fact}); continue
            fid=str(fact['field_id']); incoming=dict(fact); status=str(incoming.get('resolution_status') or '')
            if status not in allowed:
                ignored.append({'reason':'INVALID_RESOLUTION_STATUS','field_id':fid,'status':status}); continue
            if status=='UNKNOWN_CONFIRMED' and not incoming.get('provenance_type'):
                ignored.append({'reason':'UNKNOWN_CONFIRMED_REQUIRES_PROVENANCE','field_id':fid}); continue
            if status=='INAPPLICABLE' and not incoming.get('reason'):
                ignored.append({'reason':'INAPPLICABLE_REQUIRES_REASON','field_id':fid}); continue
            current=dict(fields.get(fid) or {})
            explicit=bool(incoming.get('explicit_correction')) or str(incoming.get('provenance_type') or '').casefold()=='correction'
            changed=bool(current) and (current.get('value')!=incoming.get('value') or current.get('resolution_status')!=status)
            if changed and not explicit and current.get('resolution_status') in {'KNOWN','UNKNOWN_CONFIRMED','INAPPLICABLE'}:
                conflicts.append({'field_id':fid,'existing':current,'incoming':incoming,'kind':'AMBIGUOUS_CONTRADICTION'})
                continue
            if explicit and current:
                incoming['supersedes']={'value':current.get('value'),'resolution_status':current.get('resolution_status'),'provenance_type':current.get('provenance_type'),'provenance_ref':current.get('provenance_ref')}
            # preserve field class/asked metadata unless explicitly updated
            for k in ('field_class','asked_count','last_question_id'):
                if k not in incoming and k in current: incoming[k]=current[k]
            fields[fid]={**current,**incoming}
            merged+=1
        return {'status':'PASS' if not ignored else 'PASS_WITH_IGNORED','canonical_fields':fields,'facts_merged':merged,'conflicts':conflicts,'ignored_facts':ignored,'recompute_required':merged>0}
    if op=='interactive_completeness_scan':
        fields=s.get('canonical_fields') or {}; unasked=[]; conflicted=[]; invalid=[]; derivable=[]
        substantive={'SUBSTANTIVE_REQUIRED','SUBSTANTIVE_DECISIONAL'}
        terminal={'KNOWN','UNKNOWN_CONFIRMED','INAPPLICABLE'}
        for fid,rec in fields.items():
            if not isinstance(rec,dict): continue
            cls=rec.get('field_class'); role=rec.get('completeness_role'); status=rec.get('resolution_status')
            required = role=='REQUIRED_CONSEQUENTIAL' or (role is None and cls in substantive)
            if role=='DERIVABLE' and rec.get('derivation_available') is True and status!='KNOWN':
                derivable.append(fid)
            if required:
                if status=='UNASKED': unasked.append(fid)
                elif status=='CONFLICTED': conflicted.append(fid)
                elif status not in terminal: invalid.append(fid)
                elif status=='UNKNOWN_CONFIRMED' and not rec.get('provenance_type'): invalid.append(fid)
                elif status=='INAPPLICABLE' and not rec.get('reason'): invalid.append(fid)
        ready=not unasked and not conflicted and not invalid and not derivable
        return {'status':'READY_TO_COMPOSE' if ready else 'BLOCK','unasked_substantive_fields':sorted(unasked),'pending_derivable_fields':sorted(derivable),'conflicted_fields':sorted(conflicted),'invalid_status_fields':sorted(invalid),'allowed_terminal_statuses':sorted(terminal)}
    if op=='merge_state_diff':
        base=dict(s.get('state') or {})
        diff=s.get('state_diff') or {}
        if not isinstance(diff,dict):
            return {'status':'FAIL','code':'STATE_DIFF_NOT_OBJECT'}
        def merge(a,b):
            out=dict(a)
            for k,v in b.items():
                if isinstance(v,dict) and isinstance(out.get(k),dict): out[k]=merge(out[k],v)
                else: out[k]=v
            return out
        merged=merge(base,diff)
        return {'status':'PASS','state':merged,'preserved_unrelated_keys':sorted(set(base)-set(diff))}
    if op=='discover_authority_decisions':
        rows=[]
        for rec in (s.get('candidate_decisions') or []):
            if not isinstance(rec,dict): continue
            if rec.get('authority_owner')!='human': continue
            if not rec.get('consequential',False): continue
            if rec.get('status') in {'RESOLVED','KNOWN','UNKNOWN_CONFIRMED','INAPPLICABLE'}: continue
            did=rec.get('decision_id'); grp=rec.get('information_group')
            if not did or not grp: continue
            rows.append(dict(rec))
        groups={}
        for rec in rows: groups.setdefault(rec['information_group'],[]).append(rec)
        batches=[]
        for grp in sorted(groups):
            decisions=sorted(groups[grp],key=lambda x:(x.get('priority',999999),str(x['decision_id'])))
            batches.append({'information_group':grp,'decision_ids':[x['decision_id'] for x in decisions],'decisions':decisions})
        return {'status':'PASS','authority_batches':batches,'decision_count':sum(len(x['decision_ids']) for x in batches)}
    if op=='apply_authority_decision_diff':
        existing={str(x.get('decision_id')):dict(x) for x in (s.get('decisions') or []) if isinstance(x,dict) and x.get('decision_id')}
        for ans in (s.get('responses') or []):
            if not isinstance(ans,dict) or not ans.get('decision_id'): continue
            did=str(ans['decision_id']); cur=existing.get(did,{'decision_id':did})
            cur.update(ans); cur['status']=ans.get('status','RESOLVED')
            existing[did]=cur
        unresolved=[x for x in existing.values() if x.get('status') not in {'RESOLVED','KNOWN','UNKNOWN_CONFIRMED','INAPPLICABLE'}]
        return {'status':'PASS','decisions':sorted(existing.values(),key=lambda x:x['decision_id']),'unresolved_decision_ids':sorted(x['decision_id'] for x in unresolved)}
    if op=='traceability_sync':
        edges=s.get('traceability_edges',[]) or []
        uniq={(e.get('from'),e.get('to'),e.get('type','depends_on')) for e in edges if e.get('from') and e.get('to')}
        return {'status':'PASS','traceability_graph':{'edges':[{'from':a,'to':b,'type':t} for a,b,t in sorted(uniq)]}}
    raise SystemExit(f'unsupported operation: {op}')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--operation',required=True); ap.add_argument('--input'); ap.add_argument('--output')
    a=ap.parse_args(); state=json.loads(Path(a.input).read_text()) if a.input else json.load(__import__('sys').stdin)
    result=trans(a.operation,state); report={'schema_version':'1.0','operation':a.operation,'input_sha256':fp(state),'result':result}
    text=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
    if a.output: Path(a.output).write_text(text)
    else: print(text,end='')
if __name__=='__main__': main()
