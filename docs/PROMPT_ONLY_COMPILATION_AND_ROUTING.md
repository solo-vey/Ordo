# Prompt-Only Compilation and Evidence-Based Runtime Routing

## Purpose

Ordo Source remains the single source of truth. The same playbook may be compiled to:

- `engine_runtime`: enforced state, transitions, gates, CSG, and runtime evidence;
- `prompt_only`: lightweight model instructions for tasks where evidence shows that full runtime control is unnecessary.

## Trust boundary

A prompt-only artifact does not inherit full Ordo runtime guarantees. Every output must include `PROMPT_COMPILATION_MANIFEST.json` with explicit `guarantees_retained`, `guarantees_lost`, source SHA-256, compiler version, model profile, and evidence basis.

## Commands

```bash
ordo compile-prompt <package> --out compiled/prompt_only
ordo validate-prompt compiled/prompt_only --source source/program.ordo.yaml
ordo route-runtime --metrics evidence_metrics.json --policy routing_policy.json
ordo package <package> --profile prompt_only --out playbook-prompt-only.zip
```

## Routing

`prompt_only` is allowed only when repeated evaluation meets the configured composite, branch, and backtrack thresholds. Any source, compiler, policy, provider, or model-version change requires revalidation. Failure routes to `engine_runtime`.

## Prohibited uses

Do not use prompt-only execution when mechanical approvals, safety gates, regulated state transitions, audit-grade runtime evidence, or deterministic replay are mandatory.
