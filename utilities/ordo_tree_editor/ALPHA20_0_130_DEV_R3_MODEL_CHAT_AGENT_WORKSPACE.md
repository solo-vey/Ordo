# alpha.20.0.130-dev

Model Chat now has a first local-agent architecture.

## Persistent session workspace
Each chat session gets isolated folders:
- uploads/
- extracted/
- generated/
- tmp/

Uploaded ZIP files are stored and safely extracted locally.

## Tool registry
Initial read/write tools:
- workspace.list
- workspace.search
- workspace.read
- workspace.stat
- workspace.write

No arbitrary shell/run_command tool is enabled in this version.

## Agent loop
One user message may trigger up to 12 internal model/tool iterations.
The model receives a compact workspace index and tool schema, requests local information as needed, receives tool results, and eventually returns a final message.

This replaces the previous architecture where large archives were primarily embedded into a single model prompt.
