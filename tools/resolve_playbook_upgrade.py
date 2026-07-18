#!/usr/bin/env python3
import json,sys
from pathlib import Path

def load(p): return json.loads(Path(p).read_text())
def resolve(active,new):
    if active.get("playbook_id") != new.get("playbook_id"):
        return {"decision":"upgrade_blocked","reason":"playbook_id_mismatch","automatic_runtime_mutation":False}
    if active.get("playbook_version") == new.get("playbook_version"):
        return {"decision":"no_action","reason":"same_version","automatic_runtime_mutation":False}
    mode=new.get("compatibility",{}).get("previous_playbook","incompatible")
    decision={"compatible":"recommended_revalidation","revalidation_required":"recommended_revalidation","migration_required":"migration_required","incompatible":"upgrade_blocked"}.get(mode,"upgrade_blocked")
    changes=new.get("changes",{})
    return {"decision":decision,"from_version":active.get("playbook_version"),"to_version":new.get("playbook_version"),"changed_nodes":changes.get("changed_nodes",[]),"changed_contracts":changes.get("changed_contracts",[]),"changed_outputs":changes.get("changed_outputs",[]),"changed_gates":changes.get("changed_gates",[]),"migration":new.get("migration",{}),"rollback":new.get("rollback",{}),"automatic_runtime_mutation":False}
if __name__=="__main__":
    if len(sys.argv)!=3: raise SystemExit("usage: resolve_playbook_upgrade.py ACTIVE NEW")
    print(json.dumps(resolve(load(sys.argv[1]),load(sys.argv[2])),indent=2))
