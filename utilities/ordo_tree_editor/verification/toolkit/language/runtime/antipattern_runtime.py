from __future__ import annotations
import json
from pathlib import Path
from detector_contract import CanonicalDetector,DetectionContext
from antipattern_finding_model import materialize_finding,aggregate_findings
from antipattern_signal_extractors import extract_signals
class AntipatternRuntime:
 def __init__(self,antipattern_registry,rule_registry): self.antipatterns={x['id']:x for x in antipattern_registry['items'] if x.get('status')=='active'}; self.rules=[x for x in rule_registry['items'] if x.get('status')=='active']; self.detector=CanonicalDetector()
 @classmethod
 def from_language_root(cls,r):
  r=Path(r); return cls(json.loads((r/'registries/antipattern_registry.v1.json').read_text()),json.loads((r/'registries/detect_rule_registry.v1.json').read_text()))
 def evaluate_one(self,*,antipattern_id,state,context_type,source_id,source_hash=None,detected_at=None):
  ap=self.antipatterns[antipattern_id]; out=[]
  for rule in [x for x in self.rules if x['antipattern_id']==antipattern_id and context_type in x['input_contract'].get('allowed_contexts',[])]:
   ctx=DetectionContext(rule['input_contract']['signal_schema_version'],extract_signals(antipattern_id,state),context_type,source_id); out.append(materialize_finding(self.detector.evaluate(rule=rule,antipattern=ap,context=ctx),context=ctx,source_hash=source_hash,detected_at=detected_at))
  return out
 def evaluate_all(self,*,state,context_type,source_id,source_hash=None,detected_at=None):
  fs=[]
  for i in self.antipatterns: fs+=self.evaluate_one(antipattern_id=i,state=state,context_type=context_type,source_id=source_id,source_hash=source_hash,detected_at=detected_at)
  return aggregate_findings(fs)
