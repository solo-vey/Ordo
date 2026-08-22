#!/usr/bin/env python3
import argparse,json,zipfile,hashlib
from pathlib import Path
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("mapping")
    ap.add_argument("output")
    a=ap.parse_args()
    mp=Path(a.mapping)
    m=json.loads(mp.read_text(encoding="utf-8"))
    answers=m.get("answers")
    if not isinstance(answers,list) or not answers:
        raise SystemExit("answers[] is required")
    events=[]; node_path=[]
    for i,item in enumerate(answers,1):
        node_id=str(item.get("node_id") or "").strip()
        response=item.get("analyst_response",item.get("response"))
        if not node_id: raise SystemExit(f"answers[{i-1}].node_id is required")
        if not isinstance(response,str) or not response.strip():
            raise SystemExit(f"answers[{i-1}] response is required")
        ev={
          "sequence":i,
          "node_id":node_id,
          "analyst_answer_verbatim":response,
          "analyst_response":response,
          "capture_mode":item.get("capture_mode","auto_answer_fixture"),
          "timestamp_status":item.get("timestamp_status","not_recorded"),
        }
        for k in ("question_or_prompt_shown","transition_to"):
            if item.get(k) is not None: ev[k]=item[k]
        events.append(ev); node_path.append(node_id)
    trace={
      "schema_version":"ordo.run_trace.auto_answers.v1",
      "run_id":m.get("run_id","auto-answers-generated"),
      "playbook":m.get("playbook",{}),
      "export_timestamp":"not_recorded",
      "node_path":node_path,
      "interaction_trace_schema_version":"ordo.interaction_trace.v1",
      "interaction_trace_contract":{"status":"fixture","verbatim_answers_available":True,"purpose":"analyst_auto_answers"},
      "interaction_trace":events,
    }
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("run_trace.json",json.dumps(trace,ensure_ascii=False,indent=2)+"\n")
        z.writestr("interaction_trace.json",json.dumps(events,ensure_ascii=False,indent=2)+"\n")
        z.writestr("AUTO_ANSWERS_MANIFEST.json",json.dumps({
          "schema_version":"1.1","answer_count":len(events),"node_path_count":len(node_path),
          "node_ids":node_path,"mapping_sha256":hashlib.sha256(mp.read_bytes()).hexdigest()
        },ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"status":"PASS","output":str(out),"answers":len(events),"node_path":len(node_path)},ensure_ascii=False))
if __name__=="__main__": main()
