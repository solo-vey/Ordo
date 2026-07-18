# Shared output/template subflow policy

APF v0.1.0-alpha.18 closes the shared terminal output/template subflow.

## User-facing flow

When a terminal point is reached, the runtime asks for output policy:

1. use an existing output;
2. add a new artifact;
3. confirm no output is required;
4. defer the output decision.

For new artifacts, the user describes the artifact freely. Examples such as Jira task, GitHub issue, document, checklist, JSON/YAML payload, message, or handoff summary are hints only, not a fixed list. The runtime must show the terminal path state fields before recipe/template authoring.

## Output recipe

A recipe records:

- artifact intent and inferred artifact kind;
- available and selected state fields;
- direct inserts;
- generated sections;
- generation instructions;
- assumptions and risks.

## Review mode

Document-like artifacts use file-first review packages by default:

- template file;
- mock-filled example;
- mapping report;
- assumptions/risks summary.

Chat should show only a short summary for large documents. Short artifacts may use inline preview.

## Review decisions

The user-facing decision set is intentionally small:

1. confirm;
2. revise;
3. defer;
4. remove artifact.

Detailed actions such as uploaded modified file, mapping changes, mock regeneration, section changes, style changes, or assumptions fixes are interpreted as variants of `revise`.

## Readiness gate

Unfinished active artifacts/templates cannot be used. The final readiness gate must force one of two actions before output generation: complete and confirm the template, or remove the artifact from the terminal point.
