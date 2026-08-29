# Execution Package Generator

The generator receives:

- baseline playbook ZIP;
- candidate playbook ZIP;
- canonical scenario suite;
- selected behavioral mode;
- campaign settings.

## Chat-native output

The generated ZIP must be self-contained and contain:

- both playbook versions;
- scenario fixtures;
- campaign configuration;
- prompt for the execution chat;
- result schemas;
- evidence policy;
- continuation instructions;
- merge instructions.

## Provider API output

The generated ZIP must contain:

- both playbook versions or immutable paths/digests;
- provider adapter;
- environment/config template;
- scenario fixtures;
- orchestration scripts;
- result schemas;
- live execution runbook.

The generator must never embed credentials.
