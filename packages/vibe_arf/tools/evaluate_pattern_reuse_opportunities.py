#!/usr/bin/env python3
from pathlib import Path
import argparse,json,yaml,hashlib
from validate_pattern_graph_realization import assess as assess_graph_realization

def evaluate(root):
    root=Path(root).resolve()
    reg=json.loads((root/'patterns/PATTERN_REGISTRY.json').read_text())
    snap=json.loads((root/'authoring/pattern_selection_input_snapshot.json').read_text())
    arts={x['id']:x for x in (yaml.safe_load((root/'authoring/artifact_catalog.yaml').read_text()) or {}).get('artifacts',[])}
    caps={x['id']:x for x in (yaml.safe_load((root/'authoring/capability_requirement_catalog.yaml').read_text()) or {}).get('requirements',[])}
    cat=yaml.safe_load((root/'authoring/pattern_instance_catalog.yaml').read_text()) or {}
    proj=yaml.safe_load((root/'authoring/pattern_execution_projection.yaml').read_text()) or {}
    inst={x['instance_id']:x for x in cat.get('instances',[])}
    frags={x['pattern_instance_id']:x for x in proj.get('fragments',[])}
    realization=assess_graph_realization(root)
    realized={x.get('pattern_instance_id'):x for x in realization.get('instances',[])}
    reward_default=int((reg.get('reuse_scoring') or {}).get('qualified_reuse_reward_points',50))
    patterns={p['id']:p for p in reg.get('patterns',[])}
    opportunities=[]; seen=set()
    def add(pid,semantic_id,artifact_id=None,capability_id=None,origin=None):
        if semantic_id in seen: return
        seen.add(semantic_id); p=patterns[pid]; reward=int((p.get('reward_points') or reward_default))
        pb=(arts.get(artifact_id,{}).get('pattern_binding') if artifact_id else None) or (caps.get(capability_id,{}).get('pattern_binding') if capability_id else None)
        qualified=False; iid=None; evidence=''
        realization_status=None
        if pb and pb.get('pattern_id')==pid:
            iid=pb.get('instance_id'); ii=inst.get(iid); ff=frags.get(iid); rr=realized.get(iid)
            realization_status=(rr or {}).get('status')
            qualified=bool(ii and ff and rr and str(ii.get('pattern_version'))==str(pb.get('pattern_version')) and ii.get('requirement_origin') not in ('pattern_instantiation','pattern_generated',None,'') and ff.get('projection_source')=='pattern_execution_template' and ff.get('selection_performed_at_tree_stage') is False and realization_status=='PASS')
            if qualified: evidence=f'pre-library requirement snapshot + validated instance {iid} + exact graph-realization PASS'
        status='QUALIFIED_REUSE' if qualified else 'MISSED_REUSE'
        miss_reason='unselected_or_unbound_pattern'
        if iid and realization_status!='PASS': miss_reason='pattern_selected_but_graph_not_realized'
        opportunities.append({'opportunity_id':semantic_id,'semantic_responsibility_id':semantic_id,'pattern_id':pid,'pattern_instance_id':iid,'artifact_id':artifact_id,'capability_requirement_id':capability_id,'requirement_origin':origin,'status':status,'mechanically_verified':True,'graph_realization_status':realization_status,'miss_reason':None if qualified else miss_reason,'candidate_evidence':evidence or ('selected Data-Layer pattern lacks exact final graph realization' if iid else 'frozen pre-library exact applicability without qualified pattern instance'),'awarded_points':reward if qualified else 0,'potential_points':reward})
    # Eligibility comes only from the frozen pre-library snapshot.
    for a in snap.get('artifacts',[]):
        if not a.get('required',True): continue
        for pid,p in patterns.items():
            if p.get('selection_match_policy','artifact_or_capability')!='capability_required' and a.get('kind') in set(p.get('artifact_kinds') or []):
                add(pid,f"artifact:{a['id']}:{pid}",artifact_id=a['id'],origin=a.get('requirement_origin'))
    for c in snap.get('capability_requirements',[]):
        if not c.get('required',True): continue
        for pid,p in patterns.items():
            if c.get('capability_tag') in set(p.get('capability_tags') or []):
                # If the same capability is already represented by an artifact exact match, do not double count it.
                aid=c.get('artifact_id'); artifact_sem=f'artifact:{aid}:{pid}' if aid else None
                if artifact_sem and artifact_sem in seen: continue
                add(pid,f"capability:{c['id']}:{pid}",artifact_id=aid,capability_id=c['id'],origin=c.get('requirement_origin'))
    qualified=[x for x in opportunities if x['status']=='QUALIFIED_REUSE']
    missed=[x for x in opportunities if x['status']=='MISSED_REUSE']
    payload={'schema_version':'1.0','status':'PASS','producer':'tools/evaluate_pattern_reuse_opportunities.py','selection_input_snapshot_digest':snap.get('snapshot_digest'),'qualified_reuse_events':qualified,'opportunities':opportunities,'missed_reward_opportunities':missed,'total_awarded_points':sum(x['awarded_points'] for x in qualified),'total_potential_points':sum(x['potential_points'] for x in opportunities),'graph_realization_status':realization.get('status'),'graph_realization_report':realization}
    raw=json.dumps(payload,sort_keys=True,separators=(',',':')).encode(); payload['report_digest']=hashlib.sha256(raw).hexdigest(); return payload

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--out'); a=ap.parse_args(); p=evaluate(Path(a.root)); txt=json.dumps(p,ensure_ascii=False,indent=2)+'\n';
    if a.out: Path(a.out).write_text(txt)
    else: print(txt,end='')
if __name__=='__main__': main()
