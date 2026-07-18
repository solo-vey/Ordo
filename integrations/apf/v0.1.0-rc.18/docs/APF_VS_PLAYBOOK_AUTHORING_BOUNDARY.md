# APF vs concrete playbook authoring boundary

## APF patch mode

May modify the APF package, must use rc.8 confirmation gates for process-changing patches, and produces a new APF patch/closure.

## Concrete playbook authoring mode

Uses the latest confirmed APF baseline, creates a separate concrete playbook package, must not mutate the APF baseline, and must not modify the Ordo language package.

## Improvement handling

If future concrete authoring exposes an APF deficiency:

1. do not fix APF inside the concrete package workflow;
2. record an APF improvement candidate;
3. preserve it in backlog/handoff;
4. implement it only through a separate APF patch.
