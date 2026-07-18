# DD-ORDO-M65-002 — APF / History Event Factory Prompt Adoption Plan

Status: accepted-plan
Milestone: M65.1

## Context

M65.0 introduced `prompt_registry` and `prompt_refs` as a language/package standard. The next step is to define how this standard should be applied to the History Event Factory / guided intake package without immediately rewriting runtime behavior.

The improvement proposal requested package-level quick-start prompts, node helper prompts, artifact helpers, repair helpers, manifest integration, and validation coverage.

## Decision

Create a concrete adoption plan for `packages/history_event_guided_intake/` before modifying the source YAML.

The plan defines:

- target `prompts/` folder structure;
- current-node mapping for proposed APF helper nodes;
- planned `prompt_registry` entries;
- planned node `prompt_refs`;
- artifact and repair helper prompt targets;
- README/START_HERE requirements;
- manifest and validation requirements;
- smoke test plan.

## Reason

The current History Event guided intake package uses a smaller MVP node set than the proposed APF prompt registry improvement. A direct rewrite would risk referencing future node ids that do not exist in the current package.

A plan-first milestone keeps the package deterministic and reviewable.

## Consequences

- M65.1 is documentation/package-adoption planning only.
- Prompt files are not yet authoritative package artifacts.
- Source YAML is not rewritten in this milestone.
- The next implementation milestone can add prompt files and registry entries as a scoped patch.

## Non-goals

- No runtime core changes.
- No parent CLI changes.
- No opcode/IR promotion.
- No APF branch logic rewrite.
- No deterministic natural-language classifier.
