# Ordo Visual Graph Generator — Output Layers

Status: documentation update after graph-layer review.

This utility renders Ordo YAML/IR as a visual workflow graph. The default graph is the main workflow tree. Additional data types are rendered as optional overlay layers. A layer must not destroy the readability of the main tree.

## Rendering rule

Use this rule for every extra data type:

```text
Main workflow tree stays primary.
Extra metadata is attached near the node when it belongs to that node.
Only truly global/unmatched metadata goes into a separate side cluster.
Avoid bottom-only metadata dumps.
Avoid fan-out edges from global summary nodes when the same information can be embedded into the card.
```

## Supported output formats

The stable output formats are:

```text
graph.mmd
svg
png
```

SVG/PNG are generated through Graphviz `dot`.

## Workflow layer

Source fields:

```yaml
nodes[].id
nodes[].question
nodes[].answer_type
nodes[].on_answer
nodes[].next
nodes[].branches
```

Rules:

- Render workflow nodes as rectangles.
- Render edges from `on_answer` / `next`.
- Use meaningful branch labels.
- Avoid noisy `answer` labels for free-text direct transitions.
- Terminal nodes are rendered at the end of the corresponding path.

## Branch label layer

Branch labels should be resolved in this priority order:

1. `on_answer.<key>.label/title/text/description`
2. `answer_options` / `options`
3. option labels parsed from question text, for example `A — ...`, `1. ...`
4. `update_state.selected_path_label`
5. `update_state.test_coverage_level`
6. `update_state.coverage_level`
7. `update_state.*_label`
8. object-style `allowed_answers`
9. raw branch key

## Artifacts / concrete documents layer

Current implemented behavior:

- Supports fallback extraction of document bullets from node text.
- Supports `outputs[]` as package/archive nodes.

Known sample-YAML status:

```text
outputs: present
document bullets: present
artifacts: not present
artifact_requirements: not present
coverage_rules: not present
rendered_artifact_assertions: not present
go_no_go: not present
```

Documentation requirement:

- The utility should support canonical artifact fields when they exist.
- For YAML files that only contain `outputs[]` and document bullets, the graph must mark this as partial artifact coverage rather than inventing missing artifact metadata.

## Assertions layer

Source fields:

```yaml
assertions[].id
assertions[].polarity
assertions[].condition
assertions[].phase
assertions[].severity
assertions[].on_fail
```

Rules:

- Assertions that can be associated with a node are attached beside that node.
- Unmatched/global assertions go into an `Unattached / global assertions` cluster.
- Do not collect all assertions into one bottom cluster if most are node-specific.

Attachment heuristics:

- `state.<field>` in assertion condition attaches to the node that writes that field.
- Known contract keywords may attach to corresponding contract nodes.
- Otherwise, keep assertion global.

## State fields / contracts layer

Source fields:

```yaml
nodes[].on_answer.update_state
nodes[].required_fields
state
contract.required
```

Rules:

- A state card should be placed beside the node that writes it.
- State cards should include status inside the card:
  - `required`
  - `declared`
  - `written`
  - `runtime/control`
  - `no writer`
- Do not draw large fan-out lines from `contract.required` or `state schema` to every field. That hurts readability.
- Runtime/global fields without writer nodes go into a separate side cluster.

## Contract detail cards v2

Source fields:

```yaml
nodes[].required_fields
nodes[].answer_type
nodes[].question
nodes[].on_answer.update_state
```

Rules:

- `required_fields` is the primary source for required contract fields.
- Parsing mandatory fields from `question` is only a fallback.
- A contract card should show:
  - input type
  - meaning / short question summary
  - required fields
  - written state fields
  - coverage status
  - checkpoint notes

Example card:

```text
Contract details v2
input: free_text
meaning: technical contract: provider_class, rule_class...
requires: technical_contract
writes: state.technical_contract
coverage: ✓ technical_contract
checkpoint: one node/contract at a time; no node merge
```

## Gates layer

Source fields:

```yaml
gates[].id
gates[].method
gates[].trust_class
gates[].condition
gates[].on_fail
outputs[].allowed_after
```

Rules:

- Gate cards should be attached to the node that satisfies them when possible.
- Gates referenced only by output go/no-go may attach to output or global gates block.
- Gate cards should include:
  - id
  - method
  - trust_class
  - condition
  - on_fail
- Avoid output label escaping bugs: labels must use real newline strings before DOT escaping.

## Output / go-no-go layer

Source fields:

```yaml
outputs[].id
outputs[].type
outputs[].allowed_after
```

Rules:

- Render output packages as folder nodes.
- Summarize `allowed_after` as go/no-go conditions.
- Avoid drawing every allowed-after gate edge in dense summary views unless explicitly requested.
- Detailed gate views may show gate-to-output edges.

## Unmatched input / repair layer

Source fields:

```yaml
nodes[].on_unmatched_input.action
nodes[].on_unmatched_input.strategy
nodes[].on_unmatched_input.max_attempts
nodes[].on_unmatched_input.on_exhausted.action
nodes[].on_unmatched_input.on_exhausted.reason
```

Rules:

- Repair cards attach beside their node.
- Show action, strategy, max attempts, and exhausted behavior.
- Global freeform/runtime rules stay in a separate block unless clearly attachable.

## Includes layer

Source fields:

```yaml
includes[].library
includes[].version
includes[].as
```

Fallback fields for other Ordo shapes:

```yaml
includes[].path
includes[].file
includes[].type
```

Rules:

- Show includes as library/dependency cards.
- Attach includes to a module/root card, not to arbitrary workflow nodes.

## Freeform / runtime notes layer

Source fields:

```yaml
freeform[].id
freeform[].role
freeform[].maturity
freeform[].incident_count
freeform[].incident_threshold
freeform[].content
```

Rules:

- Attach a freeform rule near a node if content clearly refers to that node/contract.
- Otherwise place it into `Global freeform/runtime notes`.
- Show maturity and incident count as rule status.

## Rendering rules / output templates layer

Source fields:

```yaml
runtime.rendering_model
assertions[] mentioning template/render/model_assisted
nodes[] mentioning model-assisted rendering
outputs[]
```

Rules:

- Render model-assisted rendering policy as a rendering policy card.
- Attach template/rendering assertions to that policy or rendering contract node.
- Show final output documents/packages as render targets.
- Do not invent template metadata that is absent from YAML.

## Trace overlay v2

Trace overlay is a separate input file, not inferred from the YAML.

It must include node id, branch identity, next node, and optional comments.

See `TRACE_OVERLAY_SCHEMA.md`.

## Known generated reference files

Useful reference SVGs from the review session:

```text
demo_support_triage_attached_assertions.svg
demo_support_triage_attached_state_fields.svg
demo_support_triage_contract_details_v2.svg
demo_support_triage_state_schema_coverage_clean.svg
demo_support_triage_gate_details.svg
demo_support_triage_includes_freeform_details.svg
demo_support_triage_artifact_coverage_readiness.svg
demo_support_triage_trace_overlay_v2.svg
```
