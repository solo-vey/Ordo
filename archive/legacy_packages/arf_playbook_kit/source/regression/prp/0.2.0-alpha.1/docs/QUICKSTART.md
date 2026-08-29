# Quick Start

## Minimum route

Upload:
- this PRP package;
- baseline playbook ZIP;
- candidate playbook ZIP.

Paste `prompts/START_PRP.md`.

The controlling chat performs deterministic and semantic regression first. It then asks for one behavioral mode.

## Recommended route while developing an applied playbook

Use PRP inside the same ARF authoring chat as a release/regression checkpoint.

Keep deterministic comparison and final promotion control in that chat.

For chat-native behavioral execution, export the generated test package to a separate chat. This avoids contaminating the authoring context and allows choosing another model.

Return the generated results ZIP to the original ARF/PRP chat for aggregation and final decision.
