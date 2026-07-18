# Interaction / Process Rail / Conversation Semantics Value Registry

Status: `M64.2 value registry convention`

This registry explains common values used by `interaction_model`, `process_rail`, and `conversation_semantics`.

## Attribute value kinds

| Kind | Meaning | Example |
|---|---|---|
| `strict enum` | Use only listed values unless schema changes. | `backtracking: restricted` |
| `convention string` | Package may define additional values, but must document them. | `resume_policy: resume_at_declared_checkpoint` |
| `free text` | Human-readable description, not deterministic runtime condition. | `purpose: ...` |
| `reference` | Points to a node, gate, artifact, or policy. | `rail_id: default_runtime_rail` |
| `path` | File path or artifact path. | `output_templates/report.md` |

## human_role

| Value | Meaning |
|---|---|
| `content_decision_owner` | Human owns domain meaning, scope, and content approval. |
| `approval_owner` | Human owns explicit approval gates. |
| `process_owner` | Human owns process shape, branching, and acceptance criteria. |
| `reviewer` | Human reviews outputs but may not own full process decisions. |

## ai_role

| Value | Meaning |
|---|---|
| `guided_process_driver` | AI leads the user along the declared rail. |
| `ordo_executor` | AI executes a compiled Ordo process under runtime discipline. |
| `ordo_developer` | AI authors or improves Ordo packages. |
| `summarizer` | AI summarizes/reformats, but does not own routing. |

## cli_role

| Value | Meaning |
|---|---|
| `deterministic_validator` | CLI/helper tools validate mechanical conditions. |
| `artifact_builder` | CLI/helper tools build output/package artifacts. |
| `graph_renderer` | CLI/helper tools render graph artifacts. |
| `none` | No CLI/helper role is claimed. |

## raw_tool_output_policy

| Value | Meaning |
|---|---|
| `summarize_before_user` | AI summarizes raw tool output before presenting it. |
| `show_on_request` | Raw output appears only if the user asks. |
| `show_full` | Raw output may be shown directly. |
| `never_show_raw` | Raw output must not be shown directly. |

## state_tracking

| Value | Meaning |
|---|---|
| `required` | Explicit state tracking is required for correct execution. |
| `recommended` | State tracking is useful but not mandatory for every path. |
| `none` | No explicit state tracking claim is made. |

## backtracking

| Value | Meaning |
|---|---|
| `disabled` | No backward navigation through previous decisions. |
| `restricted` | Backtracking is allowed only under explicit policy/review. |
| `enabled` | Backtracking is generally allowed, subject to consistency checks. |

## input_classes

| Value | Meaning |
|---|---|
| `answer_current_node` | User answers the active node/question. |
| `clarification` | User asks for explanation without state mutation. |
| `deviation` | User temporarily leaves the active route. |
| `backtrack_request` | User asks to reopen an earlier step. |
| `new_requirement` | User introduces new scope or requirement. |
| `approval` | User explicitly approves proposal/artifact/gate. |
| `refusal` | User rejects proposal/path/artifact. |
| `out_of_scope` | Input does not belong to the declared process. |

## unmatched_input_policy

| Value | Meaning |
|---|---|
| `clarify_before_state_change` | Ask for clarification before state changes. |
| `reject` | Reject ambiguous input for current node. |
| `log_and_continue` | Record input but do not change route/state. |
| `route_to_human_review` | Ask human owner how to classify input. |
