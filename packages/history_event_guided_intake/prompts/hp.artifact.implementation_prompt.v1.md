# Artifact Helper — Implementation Prompt generation

Use this helper when generating or reviewing `04_IMPLEMENTATION_PROMPT_<ALIAS>.md`.

## Goal

Separate confirmed implementation requirements from open questions and keep the implementation scope minimal.

## Include

- confirmed business behavior;
- architecture-preservation instruction;
- code discovery before file-specific claims;
- expected tests from `test_strategy_contract`;
- paired markdown test documentation requirement when unit tests are required;
- explicit out-of-scope boundaries.

## Do not

- Do not invent class names or file paths if code discovery has not confirmed them.
- Do not request unrelated refactoring.
- Do not treat open questions as confirmed requirements.

## Authority boundary

This helper does not grant permission to implement beyond the analytical contract.
