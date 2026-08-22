#!/usr/bin/env python3
import argparse, json
from collections import deque, defaultdict
from pathlib import Path
import yaml

ASSESSABLE_KINDS={'information','artifact'}
EXPOSURE_KINDS={'information','artifact','action','operation','process'}

def analyze(graph):
    nodes={n['id']:n for n in graph.get('nodes',[]) if isinstance(n,dict) and n.get('id')}
    adj=defaultdict(list)
    for e in graph.get('edges',[]):
        if not isinstance(e,dict): continue
        a,b=e.get('from'),e.get('to')
        if a in nodes and b in nodes: adj[a].append(b)
    gate_covers=defaultdict(set)
    for nid,n in nodes.items():
        if n.get('kind')=='validation_gate':
            gate_covers[nid].update(n.get('covers') or [])
    # Explicit validated_by edges also establish gate coverage for their source.
    for e in graph.get('edges',[]):
        if not isinstance(e,dict) or e.get('type')!='validated_by': continue
        a,b=e.get('from'),e.get('to')
        if b in nodes and nodes[b].get('kind')=='validation_gate': gate_covers[b].add(a)

    variables={}
    opportunities=[]
    for src,n in nodes.items():
        if n.get('kind')!='information': continue
        candidate_gates={g for g,covers in gate_covers.items() if src in covers}
        if not candidate_gates:
            continue  # missing-validation is a different architecture concern
        dist={src:0}; q=deque([src])
        while q:
            cur=q.popleft()
            for nxt in adj[cur]:
                if nxt not in dist:
                    dist[nxt]=dist[cur]+1; q.append(nxt)
        reachable=[(dist[g],g) for g in candidate_gates if g in dist]
        if not reachable:
            variables[src]={
                'validation_required':True,
                'validating_gate':None,
                'validation_latency':None,
                'unvalidated_exposure_count':None,
                'unvalidated_exposure_nodes':[],
                'rollback_span':None,
                'rollback_nodes':[],
                'status':'VALIDATION_GATE_UNREACHABLE'
            }
            continue
        latency,gate=min(reachable, key=lambda x:(x[0],x[1]))
        # Only nodes strictly before the earliest gate are unvalidated exposure.
        exposure=[]; rollback=[]
        for nid,d in dist.items():
            if nid==src or d>=latency: continue
            kind=nodes[nid].get('kind')
            if kind=='validation_gate': continue
            if kind in EXPOSURE_KINDS:
                exposure.append(nid)
            if kind in ASSESSABLE_KINDS:
                rollback.append(nid)
        exposure=sorted(exposure); rollback=sorted(rollback)
        rec={
            'validation_required':True,
            'validating_gate':gate,
            'validation_latency':latency,
            'unvalidated_exposure_count':len(exposure),
            'unvalidated_exposure_nodes':exposure,
            'rollback_span':len(rollback),
            'rollback_nodes':rollback,
            'status':'OK'
        }
        variables[src]=rec
        if latency>1:
            opportunities.append({'rule_id':'VALIDATION_LATENCY','variable_id':src,'value':latency,'validating_gate':gate})
        if exposure:
            opportunities.append({'rule_id':'UNVALIDATED_EXPOSURE','variable_id':src,'value':len(exposure),'nodes':exposure})
        if rollback:
            opportunities.append({'rule_id':'ROLLBACK_SPAN','variable_id':src,'value':len(rollback),'nodes':rollback})
    return {
        'format':'vibe-graph-locality-analysis/v1',
        'semantic_source':'canonical_data_layer_graph',
        'score_mode':'DIAGNOSTIC_OPPORTUNITY_ONLY',
        'variables':variables,
        'opportunities':opportunities,
        'summary':{
            'assessed_variables':len(variables),
            'validation_latency_opportunities':sum(1 for x in opportunities if x['rule_id']=='VALIDATION_LATENCY'),
            'unvalidated_exposure_opportunities':sum(1 for x in opportunities if x['rule_id']=='UNVALIDATED_EXPOSURE'),
            'rollback_span_opportunities':sum(1 for x in opportunities if x['rule_id']=='ROLLBACK_SPAN')
        }
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--graph',default='authoring/information_flow_graph.yaml')
    ap.add_argument('--output')
    a=ap.parse_args()
    graph=yaml.safe_load(Path(a.graph).read_text())
    out=analyze(graph)
    text=json.dumps(out,indent=2,sort_keys=True)+"\n"
    if a.output: Path(a.output).write_text(text)
    else: print(text,end='')
if __name__=='__main__': main()
