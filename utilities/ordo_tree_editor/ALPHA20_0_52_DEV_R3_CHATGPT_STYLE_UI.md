# alpha.20.0.52-dev — R3 ChatGPT-style interaction layer

UI redesign before final Release 3 live acceptance.

Implemented:
- workspace order/labels: Execute Playbook, Replay Real Chat, Show Tree, Show Path;
- system UI forced to English while analyst/model content remains source/model-authored;
- ChatGPT-style live transcript: analyst bubbles right, model output unboxed on white;
- compact system/activity lines and shimmer activity while the current model step runs;
- ChatGPT-style composer with internal + attachment and black circular send/stop control;
- textarea remains editable while model works; send is blocked and Enter preserves draft;
- send control morphs into Stop during a current model step;
- Current State, Pause/Resume Auto, Auto Answers moved to top control bar;
- duplicate active current-node status removed from the transcript header;
- Stop current model step aborts the active client request, applies no partial returned state,
  keeps the execution pointer on the same node and pauses for explicit resume;
- recovery radio controls aligned with their labels;
- tree viewport zoom controls: zoom out, reset 100%, zoom in;
- Replay Real Chat restyled to the same light chat visual language.

No playbook semantics or Compiler semantics changed.
