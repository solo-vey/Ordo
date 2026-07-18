# Prompt Application and Trace Evidence Contract

Status: `M71.4 validated package contract`

## Authority order

```text
JSON IR / CLI evidence selects the executable step.
prompt_refs provide local guidance for that selected step.
session trace proves which prompt identities were applied.
```

A prompt cannot select or alter navigation, skip a node, bypass a gate, mutate confirmed state, or make output eligible.

## Application algorithm

For the current CLI-served node, gate, or artifact:

1. Read `prompt_refs` only from the selected executable object.
2. Validate every `use` against the controlled phase vocabulary.
3. Preserve source-list order for refs sharing a phase.
4. Resolve `prompt_id` in `PROMPT_MANIFEST.json`.
5. Verify file existence and SHA-256.
6. Apply the resolved prompt before the local action represented by `use`.
7. Keep prompt bodies hidden unless the user explicitly requests an allowed debug view.
8. Emit recordable identity evidence without prompt text.

## Controlled phases

```text
before_question
during_clarification
after_answer
before_confirmation
on_open_gap
on_gate_fail
before_artifact_generation
```

## Trace payload

```json
{
  "runtime_step_id": "N_VALUE_SEMANTICS",
  "prompt_refs_applied": [
    {
      "prompt_id": "hp.normalization.value_comparison.v1",
      "use": "before_question",
      "sha256": "de24dd70cda64ffbc16219cf1fcde1a8cb60c6aaf5a93296bf7a8f7c1c3849ae",
      "ordinal": 1
    },
    {
      "prompt_id": "hp.normalization.value_comparison.v1",
      "use": "during_clarification",
      "sha256": "de24dd70cda64ffbc16219cf1fcde1a8cb60c6aaf5a93296bf7a8f7c1c3849ae",
      "ordinal": 2
    }
  ]
}
```

Required fields are `prompt_id`, `use`, `sha256`, and `ordinal`. The payload must not contain `prompt_text`, `prompt_body`, hidden reasoning, or a prompt-derived `next_node`.

## Failure behavior

Block local prompt application when:

- a ref is unresolved;
- the manifest path is missing;
- checksum verification fails;
- `use` is outside the controlled vocabulary;
- same-phase order cannot be determined;
- prompt content claims navigation, gate, approval, or state authority.

Natural-language authority review can be manual or heuristic. This contract does not claim deterministic classification of prompt text.
