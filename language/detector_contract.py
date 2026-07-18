from __future__ import annotations
from dataclasses import dataclass
from typing import Any
@dataclass(frozen=True)
class DetectionContext:
    signal_schema_version:str
    signals:dict[str,Any]
    context_type:str
    source_id:str|None=None
@dataclass(frozen=True)
class DetectionEvidence:
    signal:str; observed_value:Any; predicate:str; expected_value:Any|None=None
@dataclass(frozen=True)
class AntipatternFinding:
    schema_version:str; finding_type:str; rule_id:str; antipattern_id:str; matched:bool; severity:str; enforcement:str; evidence:tuple[DetectionEvidence,...]; recovery:dict[str,Any]; remediation:dict[str,Any]; message:str
def _clause(c,s):
    k=c['signal']; p=c['predicate']; o=s.get(k); v=c.get('value'); present=k in s
    m={'is_true':o is True,'is_false':o is False,'exists':present,'missing':not present,'equals':o==v,'not_equals':o!=v}.get(p)
    if m is None:
        if p=='contains': m=present and v in o
        elif p=='not_contains': m=(not present) or v not in o
        elif p=='greater_than': m=present and o>v
        elif p=='less_than': m=present and o<v
        else: raise ValueError(p)
    return m,DetectionEvidence(k,o,p,v)
class CanonicalDetector:
    def evaluate(self,*,rule,antipattern,context):
        c=rule['input_contract']
        if context.signal_schema_version!=c['signal_schema_version']: raise ValueError('signal schema version mismatch')
        if context.context_type not in c.get('allowed_contexts',[]): raise ValueError('context type not allowed')
        missing=[x for x in c['required_signals'] if x not in context.signals]
        if missing and rule['evaluation']['missing_signal_policy']=='error': raise ValueError(f'missing required signals: {missing}')
        if missing: matched=False; evidence=()
        else:
            rs=[_clause(x,context.signals) for x in rule['condition']['clauses']]; vals=[x[0] for x in rs]; op=rule['condition']['operator']
            matched=all(vals) if op=='all' else any(vals) if op=='any' else sum(vals)>=rule['condition']['threshold']; evidence=tuple(x[1] for x in rs)
        return AntipatternFinding('ordo.antipattern_finding.v1','ANTIPATTERN.FINDING',rule['id'],antipattern['id'],matched,antipattern['severity'],antipattern['enforcement'],evidence,antipattern['recovery'],antipattern['remediation'],f"Anti-pattern {antipattern['id']} {'detected' if matched else 'not detected'}.")
