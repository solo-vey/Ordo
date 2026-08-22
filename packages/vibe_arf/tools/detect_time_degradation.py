#!/usr/bin/env python3
import argparse, json, statistics
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--threshold-multiplier',type=float,default=1.35)
    ap.add_argument('--small-complexity-delta',type=float,default=0.10)
    ns=ap.parse_args()
    d=json.loads(Path(ns.input).read_text())
    recent=[float(x) for x in d.get('recent_valid_wall_times_ms',[]) if x is not None]
    median=statistics.median(recent) if len(recent)>=3 else None
    signals=[]
    if int(d.get('runtime_restart_count',0))>0: signals.append('RUNTIME_RESTART')
    if int(d.get('candidate_compile_count',0))>1: signals.append('DUPLICATE_COMPILE')
    if median and float(d.get('wall_time_ms',0)) > median*ns.threshold_multiplier and abs(float(d.get('semantic_complexity_delta',0))) <= ns.small_complexity_delta:
        signals.append('WALL_TIME_DEGRADATION')
    # Useful diagnosis signals; they do not by themselves imply a defect.
    if int(d.get('gap_loop_iterations',0))>=4: signals.append('HIGH_GAP_LOOP_COUNT')
    status='PERFORMANCE_DEGRADATION' if any(s in signals for s in ('RUNTIME_RESTART','DUPLICATE_COMPILE','WALL_TIME_DEGRADATION')) else 'NO_DEGRADATION_DETECTED'
    out={
      'status':status,
      'mode':'OPPORTUNITY_DIAGNOSTIC',
      'score_effect':0,
      'threshold_multiplier':ns.threshold_multiplier,
      'recent_valid_median_wall_time_ms':median,
      'current_wall_time_ms':d.get('wall_time_ms'),
      'signals':signals,
      'diagnosis_order':['CONFIRM_REGIME','PROFILE_PHASES','COUNT_REPEATED_WORK','CHECK_INPUT_DRIVEN_COMPLEXITY','FIX_ORCHESTRATION_FIRST','OPTIMIZE_ARCHITECTURE_SECOND','CONTROLLED_AB'],
      'prohibited_shortcuts':['SUPPRESS_CONSEQUENTIAL_GAPS','WEAKEN_EVALUATOR','CHANGE_SCORE_REGIME','REUSE_RESPONSE_AFTER_INPUT_HASH_CHANGE']
    }
    Path(ns.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(status)
if __name__=='__main__': main()
