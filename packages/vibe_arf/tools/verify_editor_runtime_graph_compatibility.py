#!/usr/bin/env python3
from pathlib import Path
import argparse,json,yaml
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("target",nargs="?",default=str(Path(__file__).resolve().parents[1]))
    a=ap.parse_args()
    R=Path(a.target).resolve()
    src=R/"source/program.ordo.yaml"
    d=yaml.safe_load(src.read_text(encoding="utf-8"))
    nodes={x['id']:x for x in (d.get('nodes') or []) if isinstance(x,dict) and x.get('id')}
    gates={x['id']:x for x in (d.get('gates') or []) if isinstance(x,dict) and x.get('id')}
    ext=set((d.get('graph_contract') or {}).get('external_terminal_targets') or [])
    ids=set(nodes)|set(gates)
    def targets(obj,is_gate=False):
        out=[]
        def rec(v):
            if isinstance(v,dict):
                for k,x in v.items():
                    if k=='next' and isinstance(x,str): out.append(x)
                    else: rec(x)
            elif isinstance(v,list):
                for x in v: rec(x)
        if is_gate:
            for k in ('on_pass','on_fail'):
                x=obj.get(k)
                if isinstance(x,str) and x.casefold() not in {'block','continue','retry','stop','warn'}:
                    out.append(x)
        else: rec(obj)
        return out
    adj={k:targets(v,False) for k,v in nodes.items()}
    adj.update({k:targets(v,True) for k,v in gates.items()})
    entry=(d.get('graph_contract') or {}).get('entry_node')
    seen=set(); stack=[entry]
    while stack:
        cur=stack.pop()
        if cur in seen or cur not in ids: continue
        seen.add(cur)
        for x in adj.get(cur,[]):
            if x in ids: stack.append(x)
    no_route=sorted(k for k in ids if not adj.get(k) and k not in ext)
    unreachable=sorted(ids-seen)
    checks={
      'all_nodes_and_gates_reachable':not unreachable,
      'all_nonterminal_elements_have_route':not no_route,
      'all_declared_gates_reached':all(g in seen for g in gates),
    }
    status='PASS' if all(checks.values()) else 'FAIL'
    print(json.dumps({'status':status,'source':str(src),'entry':entry,'reachable':len(seen),'total':len(ids),
                      'unreachable':unreachable,'no_route':no_route,'checks':checks},indent=2))
    return 0 if status=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
