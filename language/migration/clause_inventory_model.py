def validate_inventory(inventory,ambiguities):
 amap={a['ambiguity_id']:a for a in ambiguities}; issues=[]
 for c in inventory.get('clauses',[]):
  st=c.get('ambiguity',{}).get('status'); refs=c.get('ambiguity',{}).get('ambiguity_ids',[])
  if st!='clear' and not refs: issues.append({'code':'MIG-AMB-001','clause_id':c.get('clause_id')})
  if c.get('classification_confidence',0)<.6 and st=='clear': issues.append({'code':'MIG-CONF-001','clause_id':c.get('clause_id')})
  for r in refs:
   if r not in amap: issues.append({'code':'MIG-AMB-003','ambiguity_id':r})
 if any(a.get('status')=='open' and (a.get('impact')=='critical' or a.get('resolution_policy')=='block') for a in ambiguities): issues.append({'code':'MIG-AMB-BLOCK-001'})
 return {'status':'passed' if not issues else 'blocked','issues':issues}
