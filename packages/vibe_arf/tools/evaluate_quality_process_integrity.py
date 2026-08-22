#!/usr/bin/env python3
from pathlib import Path
import json, sys

REDUNDANT_REASONS={
    'duplicate_semantic_alias','unconsumed','missing_producer','missing_consumer','constructively_eliminable'
}
HUMAN_AUTHORITY_CLASSES={'human_authority','analyst_authority','human_decision','approval_authority'}

def group_count(item): return len(set(item.get('groups') or []))
def requested_variable_count(item):
    ids=item.get('variable_ids') or item.get('parameter_ids') or item.get('requested_variable_ids') or item.get('requested_parameters') or []
    if isinstance(ids,dict): ids=list(ids.keys())
    if not isinstance(ids,(list,tuple,set)): ids=[ids] if ids not in (None,'') else []
    n=len({str(x) for x in ids if x not in (None,'')})
    return max(1,n)
def cross_group_penalty(n):
    if n<=1: return 0
    return 70+50*(n-2)
def group_collapse_penalty(n):
    if n<=1: return 0
    return 100*n

def _verified_unique(items,id_key,label,required_extra=()):
    seen=set(); out=[]
    for x in items or []:
        if not isinstance(x,dict): raise ValueError(f'{label} item must be an object')
        xid=str(x.get(id_key) or '').strip()
        if not xid or xid in seen: raise ValueError(f'{label} has duplicate or missing {id_key}')
        seen.add(xid)
        if x.get('mechanically_verified') is not True: raise ValueError(f'{label} {xid} is not mechanically verified')
        if not str(x.get('candidate_evidence') or '').strip(): raise ValueError(f'{label} {xid} lacks candidate_evidence')
        for k in required_extra:
            if x.get(k) in (None,''): raise ValueError(f'{label} {xid} lacks {k}')
        out.append(x)
    return out

def evaluate(p):
    p=p or {}; oq=list(p.get('open_questions') or []); pc=list(p.get('prefilled_confirmations') or [])
    startup=p.get('startup_interaction') or {}; startup_requires=bool(startup.get('requires_analyst_information')); startup_listed=bool(startup.get('represented_in_open_questions'))
    interactions=list(oq)
    if startup_requires and not startup_listed:
        s=dict(startup); s.setdefault('id','__STARTUP__'); interactions.append(s)
    base_open=30*len(interactions)
    additional_vars=10*sum(max(0,requested_variable_count(x)-1) for x in interactions)

    # Structured collapse evidence is canonical. It suppresses the weaker cross-group scope
    # penalty only for the same interaction; base and additional-variable burden still stack.
    collapse_items=_verified_unique(p.get('group_collapse_interactions') or [],'interaction_id','group_collapse_interactions',('group_count',))
    collapse_by_id={str(x['interaction_id']):int(x['group_count']) for x in collapse_items}
    if any(n<2 for n in collapse_by_id.values()): raise ValueError('group collapse requires group_count >= 2')
    cross=0
    for x in interactions:
        iid=str(x.get('id') or '')
        if iid and iid in collapse_by_id: continue
        cross += cross_group_penalty(group_count(x))
    collapse=sum(group_collapse_penalty(n) for n in collapse_by_id.values())
    # Legacy unlinked evidence remains supported for historical fixtures, but cannot claim suppression.
    legacy=list(p.get('group_collapse_groups') or [])
    if not collapse_items and legacy:
        collapse += sum(group_collapse_penalty(int(n)) for n in legacy)
    if not collapse_items and not legacy:
        collapse += 200*int(p.get('group_collapse_count') or 0)

    redundant=_verified_unique(p.get('redundant_variables') or [],'variable_id','redundant_variables',('reason',))
    for x in redundant:
        if str(x.get('reason')) not in REDUNDANT_REASONS: raise ValueError(f"unsupported redundant-variable reason: {x.get('reason')}")
    redundant_pen=min(100,10*len(redundant))

    unsupported=_verified_unique(p.get('unsupported_inferences') or [],'id','unsupported_inferences',('field_id','authority_class'))
    hard=[]; ordinary=[]
    for x in unsupported:
        if str(x.get('authority_class')).strip().lower() in HUMAN_AUTHORITY_CLASSES: hard.append(x)
        else: ordinary.append(x)
    unsupported_pen=min(300,100*len(ordinary))

    independent=int(p.get('analyst_independent_facts') or 0)
    derivable=int(p.get('source_derivable_technical_facts_requested') or 0)
    penalties={
      'open_question':base_open,
      'open_question_additional_variable':additional_vars,
      'startup_full_information':500 if bool(startup.get('contains_all_or_nearly_all_required_information')) else 0,
      'open_question_cross_group':cross,
      'group_collapse':collapse,
      'excess_independent_facts':min(100,max(0,independent-10)*5),
      'source_derivable_technical_facts':min(150,max(0,derivable)*25),
      'no_partial_information_path':150 if bool(p.get('no_partial_information_path')) else 0,
      'reasked_known_information':50*int(p.get('reasked_known_information_count') or 0),
      'nonadaptive_question':30*int(p.get('nonadaptive_question_count') or 0),
      'redundant_variable':redundant_pen,
      'prefilled_confirmation':5*len(pc),
      'prefilled_confirmation_cross_group':15*sum(group_count(x)>1 for x in pc),
      'unsupported_inference':unsupported_pen,
    }
    defects=[]
    for x in redundant:
        defects.append({'id':'REDUNDANT_VARIABLE_'+str(x.get('variable_id')),'source':'mechanical','points':10,'dimension':'data_layer_economy','candidate_evidence':x.get('candidate_evidence'),'basis':'mechanically proven redundant variable: '+str(x.get('reason')),'missing_or_weak':'variable is not necessary to preserve semantics or artifact quality','remediation':'Remove or merge the redundant variable while preserving producer/consumer bindings, provenance and required artifact information.'})
    for x in ordinary:
        defects.append({'id':'UNSUPPORTED_INFERENCE_'+str(x.get('id')),'source':'mechanical','points':100,'dimension':'evidence_integrity','candidate_evidence':x.get('candidate_evidence'),'basis':'value used without required supporting source/provenance evidence','missing_or_weak':'justified derivation or accepted source evidence','remediation':'Derive the value from accepted evidence with provenance; if it is genuinely human-owned, ask only the minimal authority input instead of guessing.'})
    return {
      'status':'FAIL' if hard else 'PASS',
      'producer':'tools/evaluate_quality_process_integrity.py',
      'penalties':penalties,
      'defects':defects,
      'hard_invalidations':[{
          'id':'UNSUPPORTED_HUMAN_AUTHORITY_VALUE',
          'field_id':x.get('field_id'),
          'candidate_evidence':x.get('candidate_evidence'),
          'reason':'human-authority value was used without human/source authority evidence',
          'remediation':'Obtain explicit human authority evidence or leave the value unresolved; never synthesize approval/authority.'
      } for x in hard],
      'redundant_variables':redundant,
      'unsupported_inferences':ordinary,
      'stacking':{
          'suppressed_cross_group_interactions':sorted(collapse_by_id),
          'rule':'group-collapse suppresses weaker cross-group scope penalty for the same interaction; base/additional-variable and independently evidenced defect families still stack'
      },
      'legacy_group_collapse_evidence_used':bool(legacy and not collapse_items)
    }

def main(inp,out=None):
    d=json.loads(Path(inp).read_text(encoding='utf-8'))
    p=d.get('process',d)
    r=evaluate(p)
    text=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
    if out: Path(out).write_text(text,encoding='utf-8')
    else: print(text,end='')
    raise SystemExit(0 if r['status']=='PASS' else 1)
if __name__=='__main__':
    if len(sys.argv) not in (2,3): print('usage: evaluate_quality_process_integrity.py INPUT.json [OUTPUT.json]',file=sys.stderr); raise SystemExit(2)
    main(sys.argv[1],sys.argv[2] if len(sys.argv)==3 else None)
