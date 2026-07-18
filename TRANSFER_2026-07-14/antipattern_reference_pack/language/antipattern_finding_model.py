from __future__ import annotations
from datetime import datetime,timezone
from hashlib import sha256
SEVERITY_RANK={'info':0,'warning':1,'error':2,'critical':3}
def materialize_finding(finding,*,context,source_hash=None,detected_at=None):
    if finding.severity=='critical' and finding.enforcement!='blocking': raise ValueError('critical must block')
    fid='FIND-'+sha256(f'{finding.rule_id}|{context.source_id}|{finding.antipattern_id}'.encode()).hexdigest()[:16].upper()
    decision='block' if finding.matched and finding.enforcement=='blocking' else 'allow_with_advisory' if finding.matched else 'allow'
    src={'context_type':context.context_type,'source_id':context.source_id or 'UNSPECIFIED'}
    if source_hash: src['source_hash']=source_hash
    return {'schema_version':'ordo.antipattern_finding.v1','finding_type':'ANTIPATTERN.FINDING','finding_id':fid,'rule_id':finding.rule_id,'antipattern_id':finding.antipattern_id,'matched':finding.matched,'severity':finding.severity,'enforcement':finding.enforcement,'decision':decision,'message':finding.message,'evidence':[{'signal':e.signal,'predicate':e.predicate,'observed_value':e.observed_value,'expected_value':e.expected_value} for e in finding.evidence],'recovery':finding.recovery,'remediation':finding.remediation,'source':src,'timestamps':{'detected_at':detected_at or datetime.now(timezone.utc).isoformat()},'resolution':{'status':'open'}}
def aggregate_findings(fs):
    m=[f for f in fs if f.get('matched')]; b=[f for f in m if f['enforcement']=='blocking']; a=[f for f in m if f['enforcement']=='advisory']
    return {'schema_version':'ordo.antipattern_gate_report.v1','report_type':'GATE.REPORT','decision':'block' if b else 'allow_with_advisory' if a else 'allow','summary':{'total_findings':len(fs),'matched_findings':len(m),'blocking_findings':len(b),'advisory_findings':len(a),'inconclusive_findings':0,'highest_severity':max((f['severity'] for f in m),key=lambda x:SEVERITY_RANK[x]) if m else None},'blocking_finding_ids':[f['finding_id'] for f in b],'advisory_finding_ids':[f['finding_id'] for f in a],'findings':fs}
