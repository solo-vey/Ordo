CANONICAL_UNITS={'stage','action','decision','gate','state','artifact','evidence','authorization','recovery','exception'}
def validate_decomposition(source_clauses,mapped_units):
 s={x['clause_id'] for x in source_clauses}; mandatory={x['clause_id'] for x in source_clauses if x.get('mandatory')}; mapped={r for u in mapped_units for r in u.get('source_clause_refs',[])}; issues=[]
 if s-mapped: issues.append({'code':'MIG-TRACE-001','clause_ids':sorted(s-mapped)})
 if mandatory-mapped: issues.append({'code':'MIG-MANDATORY-001','clause_ids':sorted(mandatory-mapped)})
 if any(u.get('unit_type') not in CANONICAL_UNITS for u in mapped_units): issues.append({'code':'MIG-UNIT-001'})
 return {'status':'passed' if not issues else 'blocked','issues':issues}
