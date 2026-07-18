# A3 Prompt Registry Migration Report

## Status

`A3-applied-working-state`

## Implemented

- semantic, versioned APF prompt registry;
- canonical prompt manifest with SHA-256;
- object-side attachment map and controlled `use` vocabulary;
- package-local prompt application trace contract;
- migration map from existing prompt-like APF surfaces;
- authority policy preserving process structure over prompt text.

## Registered prompt families

- `apf.package.quick_start`;
- `apf.runtime.start`;
- `apf.process.resume_after_deviation`;
- `apf.state.backtrack_invalidation`;
- `apf.validation.gate_failure`;
- `apf.validation.report_interpretation`.

## Explicit exclusions

- no node-bound mini-prompt applicability review;
- no implementation of `BL-APF-002`;
- no new opcode, compiler, CLI, or runtime-core behavior;
- no prompt-derived navigation;
- no hidden reasoning or prompt text in trace evidence.

## Release status

The confirmed baseline remains `v0.1.0-rc.12-confirmed-closure`. A3 is not a confirmed release.
