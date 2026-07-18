# CSG-3 — State-protection and process-control contract

Status: completed

Implemented:

- normative state-protection assertions for generated playbooks;
- explicit classification-before-mutation rule;
- pause/resume/exit semantics;
- process-control and safety bypass routing;
- controlled `exited_incomplete` terminal status;
- trace hooks when Execution Trace is enabled;
- review-record template and blocking conditions.

Preserved boundaries:

- APF internal CSG remains disabled;
- CSG does not replace existing correction, backtracking, requirement-change, safety, or process-control contracts;
- unrelated input cannot complete a step or mutate confirmed business state.

Next: CSG-4 — authoring-flow, package artifacts, validation, and regression integration.
