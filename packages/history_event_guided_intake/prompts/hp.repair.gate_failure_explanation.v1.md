# Repair Helper — Gate failure explanation

Use this helper when a gate blocks progress.

## Goal

Explain the blocker in human language and identify the missing answer, field, or evidence needed to continue.

## Format

1. State which requirement is missing.
2. Explain why the process cannot continue.
3. Ask for the smallest missing input.
4. Return to the interrupted node after repair.

## Do not

- Do not override the gate.
- Do not rewrite state to move forward artificially.
- Do not announce successful validation without evidence.
- Do not expose raw YAML unless the analyst asks.

## Authority boundary

This helper explains blockers. The gate result remains authoritative.
