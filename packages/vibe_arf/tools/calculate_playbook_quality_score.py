#!/usr/bin/env python3
from pathlib import Path
import json, sys

def clamp_result(v): return max(0.0,min(1000.0,float(v)))
def norm(v): return int(v) if float(v).is_integer() else round(float(v),6)
def group_count(item): return len(set(item.get('groups') or []))
def requested_variable_count(item):
    ids=item.get('variable_ids') or item.get('parameter_ids') or item.get('requested_variable_ids') or item.get('requested_parameters') or []
    if isinstance(ids, dict): ids=list(ids.keys())
    if not isinstance(ids, (list,tuple,set)): ids=[ids] if ids not in (None,'') else []
    n=len({str(x) for x in ids if x not in (None,'')})
    return max(1,n)
def additional_open_variable_penalty(item): return 10*max(0,requested_variable_count(item)-1)
def cross_group_open_penalty(n):
    if n <= 1: return 0
    return 70 + 50 * (n - 2)
def group_collapse_penalty(n):
    if n <= 1: return 0
    return 100 * n

REUSE_REWARD_SCORE_CAP=200
def calibrate_reuse_reward(raw_points):
    return min(float(REUSE_REWARD_SCORE_CAP),max(0.0,float(raw_points)))

def load_pattern_reuse(p):
    root=p.get('pattern_reuse_candidate_root')
    if not root: return {'status':'NOT_EVALUATED','qualified_reuse_events':[],'missed_reward_opportunities':[],'total_awarded_points':0}
    root=Path(root).resolve()
    if not root.exists(): raise ValueError('pattern_reuse_candidate_root does not exist')
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from evaluate_pattern_reuse_opportunities import evaluate
    r=evaluate(root)
    if r.get('status')!='PASS' or r.get('producer')!='tools/evaluate_pattern_reuse_opportunities.py': raise ValueError('pattern reuse evidence is not deterministic PASS evidence')
    seen=set()
    for x in r.get('qualified_reuse_events',[]):
        sid=x.get('semantic_responsibility_id')
        if not sid or sid in seen: raise ValueError('duplicate or missing semantic responsibility in pattern reuse rewards')
        seen.add(sid)
        if x.get('mechanically_verified') is not True or x.get('status')!='QUALIFIED_REUSE': raise ValueError('unverified pattern reuse event')
        if not x.get('candidate_evidence'): raise ValueError('pattern reuse event lacks candidate evidence')
    return r

def main(inp,out):
    d=json.loads(Path(inp).read_text(encoding='utf-8'))
    tier=str(d.get('evidence_tier') or '').strip()
    if tier not in ('offline_conformance','pseudo_live_optimization','live_acceptance'):
        raise ValueError('evidence_tier must be offline_conformance, pseudo_live_optimization or live_acceptance')
    elig=d.get('result_eligibility') or {}
    formal_eligible=(tier=='live_acceptance' and str(elig.get('status') or '').upper()=='PASS' and (elig.get('formal_score_eligible') is True or elig.get('result_scoring_eligible') is True))
    pseudo_eligible=(tier in ('offline_conformance','pseudo_live_optimization') and (elig.get('pseudo_score_eligible') is True or tier=='offline_conformance'))

    p=d.get('process') or {}
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from evaluate_quality_process_integrity import evaluate as evaluate_process_integrity
    process_integrity=evaluate_process_integrity(p)
    if process_integrity.get('producer')!='tools/evaluate_quality_process_integrity.py':
        raise ValueError('process integrity evidence is not deterministic')
    hard_invalidations=list(process_integrity.get('hard_invalidations') or [])
    revision_eligibility_state='HARD_INELIGIBLE' if hard_invalidations else 'ELIGIBLE'
    process_pen=dict(process_integrity.get('penalties') or {})
    # Preserve raw deterministic penalty evidence; aggregate a separate capped view for scoring.
    effective_process_pen=dict(process_pen)
    effective_process_pen['open_question_family']=min(240, float(process_pen.get('open_question',0))+float(process_pen.get('open_question_additional_variable',0)))
    effective_process_pen.pop('open_question',None); effective_process_pen.pop('open_question_additional_variable',None)
    effective_process_pen['group_mixing_family']=min(300, float(process_pen.get('open_question_cross_group',0))+float(process_pen.get('group_collapse',0)))
    effective_process_pen.pop('open_question_cross_group',None); effective_process_pen.pop('group_collapse',None)
    effective_process_pen['reasked_known_information']=min(150,float(process_pen.get('reasked_known_information',0)))
    effective_process_pen['nonadaptive_question']=min(120,float(process_pen.get('nonadaptive_question',0)))
    effective_process_pen['prefilled_confirmation_family']=min(80,float(process_pen.get('prefilled_confirmation',0))+float(process_pen.get('prefilled_confirmation_cross_group',0)))
    effective_process_pen.pop('prefilled_confirmation',None); effective_process_pen.pop('prefilled_confirmation_cross_group',None)
    reuse=load_pattern_reuse(p)
    raw_reuse_reward=sum(float(x.get('awarded_points') or 0) for x in reuse.get('qualified_reuse_events',[]))
    reuse_reward=calibrate_reuse_reward(raw_reuse_reward)
    process_rewards={'qualified_reusable_pattern':norm(reuse_reward),'qualified_reusable_pattern_raw':norm(raw_reuse_reward),'qualified_reusable_pattern_score_cap':REUSE_REWARD_SCORE_CAP,'saturated_points':norm(max(0.0,raw_reuse_reward-reuse_reward))}
    process_score=max(0,1000-sum(effective_process_pen.values())+reuse_reward)
    reward_opps=[]
    for x in reuse.get('missed_reward_opportunities',[]):
        reward_opps.append({'id':'REUSE_'+str(x.get('opportunity_id')),'type':'POSITIVE_REWARD_OPPORTUNITY','dimension':'reusable_pattern','pattern_id':x.get('pattern_id'),'semantic_responsibility_id':x.get('semantic_responsibility_id'),'candidate_evidence':x.get('candidate_evidence'),'potential_points':min(float(x.get('potential_points',50)),max(0.0,REUSE_REWARD_SCORE_CAP-reuse_reward)),'remediation':'During Data-Layer authoring, instantiate the applicable canonical reusable pattern and derive its execution projection instead of synthesizing an ad-hoc subtree.'})

    docs=[]
    for doc in d.get('result_documents') or []:
        if bool(doc.get('technical')): continue
        if doc.get('artifact_lineage_valid_for_development') is not True:
            raise ValueError(f"eligible document {doc.get('id')} lacks exact candidate artifact lineage for development scoring")
        def normalize_defect(x, source):
            z=dict(x); z['source']=source
            required=['id','points','dimension','candidate_evidence','basis','missing_or_weak','remediation']
            missing=[k for k in required if z.get(k) in (None,'')]
            if missing: raise ValueError(f"{source} defect missing fields: {','.join(missing)}")
            if source=='analytical' and str(z.get('basis') or '').startswith('reference') and not z.get('reference_evidence'):
                raise ValueError('reference-relative analytical defect requires reference_evidence')
            return z
        doc_mech=list(doc.get('mechanical_defects') or [])
        if doc_mech:
            mech_points=sum(float(x.get('points') or 0) for x in doc_mech); mech_defects=[normalize_defect(x,'mechanical') for x in doc_mech]
        else:
            intrinsic=[]
            for ref in doc.get('reference_variants') or []:
                major=int(ref.get('missing_major_parts') or 0); detail=int(ref.get('missing_or_incomplete_details') or 0); m=list(ref.get('mechanical_defects') or [])
                pts=sum(float(x.get('points') or 0) for x in m) if m else 100*major+10*detail; intrinsic.append((pts,m,major,detail))
            if not intrinsic: raise ValueError(f"eligible document {doc.get('id')} has no reference_variants")
            unique={round(x[0],9) for x in intrinsic}
            if len(unique)>1 and any((ref.get('relevance_weight') is not None) for ref in (doc.get('reference_variants') or [])):
                raise ValueError('candidate-intrinsic mechanical penalties disagree across weighted references; provide document-level mechanical_defects')
            mech_points=sum(x[0] for x in intrinsic)/len(intrinsic); mech_defects=[normalize_defect(x,'mechanical') for x in intrinsic[0][1]] if len(unique)==1 and intrinsic[0][1] else []
        refs=[]; raw_refs=list(doc.get('reference_variants') or [])
        if not raw_refs: raise ValueError(f"eligible document {doc.get('id')} has no reference_variants")
        raw_weights=[float(ref.get('relevance_weight')) if ref.get('relevance_weight') is not None else 1.0 for ref in raw_refs]
        if any(w < 0 for w in raw_weights) or sum(raw_weights)<=0: raise ValueError('invalid reference relevance weights')
        total_w=sum(raw_weights); weighted_analytical=0.0; all_defects=list(mech_defects)
        for ref,wraw in zip(raw_refs,raw_weights):
            analytical=[normalize_defect(x,'analytical') for x in (ref.get('analytical_defects') or [])]
            analytical_points=sum(float(x.get('points') or 0) for x in analytical if x.get('candidate_penalty',True) not in (False,0))
            w=wraw/total_w; weighted_analytical += w*analytical_points
            refs.append({'reference_id':str(ref.get('id') or ''),'reference_hash':str(ref.get('hash') or ''),'relevance_weight':w,'analytical_penalty_points':norm(analytical_points),'analytical_score':norm(clamp_result(1000-analytical_points)),'defects':analytical})
            all_defects.extend(dict(x,reference_id=str(ref.get('id') or '')) for x in analytical)
        score=clamp_result(1000-mech_points-weighted_analytical)
        consensus={'reference_id':'CONSENSUS','score':norm(score),'mechanical_score':norm(clamp_result(1000-mech_points)),'analytical_score':norm(clamp_result(1000-weighted_analytical)),'mechanical_penalty_points':norm(mech_points),'analytical_penalty_points':norm(weighted_analytical),'defects':all_defects}
        docs.append({'document_id':str(doc.get('id') or ''),'score':norm(score),'mechanical_score':norm(clamp_result(1000-mech_points)),'mechanical_penalty_points':norm(mech_points),'weighted_analytical_penalty_points':norm(weighted_analytical),'reference_consensus':refs,'selected':consensus,'all_variant_scores':refs,'defects':all_defects})
    if not docs: raise ValueError('no eligible non-technical result documents')
    development_result_score=sum(float(x['score']) for x in docs)/len(docs); development_score=(process_score+2*development_result_score)/3
    pseudo_result_score=development_result_score if pseudo_eligible else None; pseudo_playbook_score=development_score if pseudo_eligible else None
    formal_result_score=development_result_score if formal_eligible else None; formal_process_score=process_score if formal_eligible else None; formal_playbook_score=development_score if formal_eligible else None
    acceptance_result_score=formal_result_score; acceptance_score=formal_playbook_score
    o={'schema_version':'4.2','status':'PASS','revision_eligibility_state':revision_eligibility_state,'hard_violation_count':len(hard_invalidations),'hard_invalidations':hard_invalidations,'evidence_tier':tier,'process_score':norm(process_score),'process_penalties':process_pen,'effective_process_penalties':effective_process_pen,'process_rewards':process_rewards,'pattern_reuse_evidence':reuse,'quality_process_integrity':process_integrity,'consolidated_improvement_opportunities':reward_opps,
       'development_result_score':norm(development_result_score),'development_score':round(development_score,6),
       'pseudo_result_score':norm(pseudo_result_score) if pseudo_result_score is not None else None,'pseudo_playbook_score':round(pseudo_playbook_score,6) if pseudo_playbook_score is not None else None,'pseudo_score_eligible':bool(pseudo_eligible),
       'formal_result_score':norm(formal_result_score) if formal_result_score is not None else None,'formal_process_score':norm(formal_process_score) if formal_process_score is not None else None,'formal_playbook_score':round(formal_playbook_score,6) if formal_playbook_score is not None else None,'formal_score_eligible':bool(formal_eligible),
       'acceptance_result_score':norm(acceptance_result_score) if acceptance_result_score is not None else None,'acceptance_score':round(acceptance_score,6) if acceptance_score is not None else None,'acceptance_status':'AVAILABLE' if formal_eligible else 'UNAVAILABLE_PROVENANCE_INELIGIBLE','documents':docs,'consolidated_defects':list(process_integrity.get('defects') or [])+[dict(z,document_id=d['document_id']) for d in docs for z in d.get('defects',[])],'formula':'(1000 - process penalties + capped qualified reuse reward contribution + 2 * result_component) / 3','score_contract':'development_score remains the optimizer objective for eligible revisions; HARD_INELIGIBLE revisions retain visible score for diagnosis but cannot replace best-so-far or be accepted; HARD_UNSCORABLE is reserved for measurement failure; reusable-pattern rewards require deterministic pre-library eligibility evidence'}
    Path(out).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
    if len(sys.argv)!=3: print('usage: calculate_playbook_quality_score.py INPUT.json OUTPUT.json',file=sys.stderr); sys.exit(2)
    try: main(sys.argv[1],sys.argv[2])
    except Exception as e: print(f'quality-score: FAIL: {e}',file=sys.stderr); sys.exit(1)
