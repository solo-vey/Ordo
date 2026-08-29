from __future__ import annotations
def extract_signals(i,s):
 a=s.get('artifacts',{}); p=s.get('package',{}); pr=s.get('process',{}); c=s.get('conversation',{}); r=s.get('repository',{}); au=s.get('authorization',{}); n=s.get('node',{}); e=s.get('evidence',{})
 if i=='PROMPT_AS_IMPLEMENTATION': return {'implementation_prompt_present':bool(a.get('implementation_prompt')),'implementation_artifacts_absent':not any(a.get(x) for x in ['source_code','repository_patch','tests','implementation_artifacts']),'completion_claim_present':bool(s.get('claims',{}).get('implementation_complete'))}
 if i=='PACKAGE_VALIDATION_WITHOUT_COMPLETENESS_VALIDATION': return {'package_structure_valid':bool(p.get('structure_valid')),'mandatory_artifacts_missing':bool(p.get('missing_mandatory_artifacts',[]))}
 if i=='MANDATORY_BRANCH_SHORT_CIRCUIT':
  req=pr.get('required_stages',[]); done=set(pr.get('completed_stages',[])); order=pr.get('stage_order',req); cur=pr.get('current_stage'); miss=[x for x in req if x not in done]; later=False
  if cur in order and miss: later=order.index(cur)>min(order.index(x) for x in miss if x in order)
  return {'required_stage_missing':bool(miss),'later_stage_entered':later}
 if i=='FINAL_LABEL_OVERCLAIM': return {'final_label_present':bool(p.get('final_label')),'supporting_evidence_insufficient':e.get('supports_final_label') is False}
 if i=='SCOPE_CONFIRMATION_AS_IMPLEMENTATION_AUTHORIZATION': return {'scope_confirmed':bool(c.get('scope_confirmed')),'repository_mutation_started':bool(r.get('mutation_started')),'mutation_authorization_absent':not bool(au.get('repository_mutation'))}
 if i=='COMPLEXITY_ROUTING_AND_EXECUTION_IN_ONE_NODE': return {'single_node_multi_decision':len(n.get('decisions',[]))>=3 or {'complexity_assessment','route_selection','execution'}<=set(n.get('responsibilities',[])),'execution_started':bool(n.get('execution_started')),'route_not_explicit':not bool(n.get('route_explicit')),'authorization_not_explicit':not bool(n.get('authorization_explicit'))}
 raise KeyError(i)
