# Ordo Tree Editor 0.2.0-alpha.20.0.222-dev

## Changes

- Removed the Show Path workspace mode completely.
- Removed its top-level navigation tab, path builder, path playback/transcript panel, graph focus overlay, context-menu path actions, state, event handlers, help topic, CSS, and dedicated regressions.
- Removed the `show_path` capability from playbook package preparation and degraded-load capability metadata.
- Kept Replay Real Chat and Execute Playbook path highlighting intact; only the separate structural Show Path feature was removed.
- Fixed schema-preserving response normalization so the reconciled values are
  committed through the runtime StatePatch path.
- Clarified preparation progress when an active subprocess cannot provide an
  internal percentage.

## Validation

- Added a regression asserting that Show Path UI, capability, handlers, and path-only CSS do not return.
- Existing tree, replay, execution, package, manifest, OpenAPI, and JavaScript syntax checks remain green.
