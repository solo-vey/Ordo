#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

ROLES={'REQUIRED_CONSEQUENTIAL','DERIVABLE','OPTIONAL','IMPLEMENTATION_DETAIL','INAPPLICABLE'}
TERMINAL={'KNOWN','UNKNOWN_CONFIRMED','INAPPLICABLE'}
WEAK_EXPECTED={'works correctly','correct','ok','valid','success','expected behavior','behaves correctly'}

def issue(code,severity,message,field_id=None,section=None,category='DERIVABLE_FIX',blocking=True):
    return {'code':code,'severity':severity,'message':message,'field_id':field_id,'section':section,'category':category,'blocking':blocking}

def evaluate(data):
    fields=data.get('canonical_fields') or {}
    issues=[]
    metrics={
        'DERIVABLE_UNKNOWN_COUNT':0,
        'UNASKED_REQUIRED_COUNT':0,
        'SYNTHETIC_UNKNOWN_COUNT':0,
        'ORPHAN_SUBSTANTIVE_SECTION_COUNT':0,
        'WEAK_GENERATED_TEST_COUNT':0,
        'PROVENANCE_MISMATCH_COUNT':0,
    }
    for fid,rec in fields.items():
        if not isinstance(rec,dict):
            continue
        role=rec.get('completeness_role')
        status=rec.get('resolution_status')
        if role is not None and role not in ROLES:
            issues.append(issue('INVALID_COMPLETENESS_ROLE','high',f'Unsupported completeness role {role}',fid))
        if role=='REQUIRED_CONSEQUENTIAL':
            if status=='UNASKED':
                metrics['UNASKED_REQUIRED_COUNT']+=1
                issues.append(issue('UNASKED_REQUIRED','high','Required consequential field remains UNASKED',fid,category='ANALYST_DECISION_REQUIRED'))
            elif status not in TERMINAL:
                issues.append(issue('INVALID_REQUIRED_RESOLUTION','high',f'Required consequential field has non-terminal status {status}',fid))
        if role=='DERIVABLE' and rec.get('derivation_available') is True and status!='KNOWN':
            metrics['DERIVABLE_UNKNOWN_COUNT']+=1
            issues.append(issue('DERIVABLE_UNKNOWN','high','Field is derivable from canonical state but remains unresolved/unknown',fid,category='DERIVABLE_FIX'))
        if status=='UNKNOWN_CONFIRMED' and not rec.get('provenance_type'):
            issues.append(issue('UNKNOWN_WITHOUT_PROVENANCE','high','UNKNOWN_CONFIRMED lacks explicit provenance',fid))
        if status=='INAPPLICABLE' and not rec.get('reason'):
            issues.append(issue('INAPPLICABLE_WITHOUT_REASON','medium','INAPPLICABLE lacks reason',fid))

    for af in data.get('artifact_fields') or []:
        if not isinstance(af,dict): continue
        fid=af.get('field_id'); rendered=af.get('rendered_value')
        if isinstance(rendered,str) and rendered.strip().upper()=='UNKNOWN':
            canon=fields.get(fid) or {}
            if canon.get('resolution_status')!='UNKNOWN_CONFIRMED' or not canon.get('provenance_type'):
                metrics['SYNTHETIC_UNKNOWN_COUNT']+=1
                issues.append(issue('SYNTHETIC_UNKNOWN','high','Artifact renders UNKNOWN without confirmed canonical unknown provenance',fid))
        canon=fields.get(fid) or {}
        cprov=canon.get('provenance_type'); rprov=af.get('rendered_provenance_type')
        if rprov and cprov and rprov!=cprov:
            metrics['PROVENANCE_MISMATCH_COUNT']+=1
            issues.append(issue('PROVENANCE_MISMATCH','medium',f'Artifact provenance {rprov} does not match canonical provenance {cprov}',fid,blocking=False))

    for sec in data.get('template_sections') or []:
        if isinstance(sec,dict) and sec.get('substantive') is True and not sec.get('resolution_strategy'):
            metrics['ORPHAN_SUBSTANTIVE_SECTION_COUNT']+=1
            issues.append(issue('ORPHAN_SUBSTANTIVE_SECTION','high','Substantive template section has no resolution strategy',section=sec.get('section_id')))

    for t in data.get('generated_tests') or []:
        if not isinstance(t,dict): continue
        src=t.get('source_rule_ids') or []
        pre=str(t.get('precondition') or t.get('input') or '').strip()
        exp=str(t.get('expected') or t.get('expected_output') or '').strip()
        weak=(not src or not pre or not exp or exp.casefold() in WEAK_EXPECTED or 'correct'==exp.casefold())
        if weak:
            metrics['WEAK_GENERATED_TEST_COUNT']+=1
            issues.append(issue('WEAK_GENERATED_TEST','medium','Generated test lacks rule linkage, concrete input/precondition, or concrete expected outcome',category='DERIVABLE_FIX'))

    deterministic_failures=data.get('deterministic_failures') or []
    for df in deterministic_failures:
        if isinstance(df,dict):
            issues.append(issue(str(df.get('code') or 'DETERMINISTIC_FAILURE'),'critical',str(df.get('message') or 'Deterministic validation failure'),blocking=True))
        else:
            issues.append(issue('DETERMINISTIC_FAILURE','critical',str(df),blocking=True))

    routes={'self_fix':0,'source':0,'analyst':0,'downstream':0}
    for f in data.get('semantic_findings') or []:
        if not isinstance(f,dict): continue
        cat=f.get('category')
        if cat=='DERIVABLE_FIX': routes['self_fix']+=1
        elif cat=='SOURCE_REQUIRED': routes['source']+=1
        elif cat=='ANALYST_DECISION_REQUIRED': routes['analyst']+=1
        elif cat=='IMPLEMENTATION_DETAIL': routes['downstream']+=1
        else:
            issues.append(issue('INVALID_SEMANTIC_FINDING_CATEGORY','medium',f'Unknown semantic finding category {cat}',blocking=True))

    blocking=any(i.get('blocking') for i in issues)
    semantic_status=data.get('semantic_quality_status')
    if blocking or deterministic_failures:
        status='BLOCK'
    elif semantic_status=='BLOCK':
        status='BLOCK'
    elif issues or semantic_status=='PASS_WITH_NOTES' or routes['downstream']:
        status='PASS_WITH_NOTES'
    else:
        status='PASS'
    return {'schema_version':'1.0','quality_status':status,'issues':issues,'metrics':metrics,'routes':routes,'semantic_gate_is_read_only':True,'deterministic_failure_override_allowed':False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',required=True); ap.add_argument('--output')
    a=ap.parse_args(); data=json.loads(Path(a.input).read_text())
    out=evaluate(data); text=json.dumps(out,indent=2,ensure_ascii=False)+'\n'
    if a.output: Path(a.output).write_text(text)
    else: print(text,end='')
    return 2 if out['quality_status']=='BLOCK' else 0
if __name__=='__main__': raise SystemExit(main())
