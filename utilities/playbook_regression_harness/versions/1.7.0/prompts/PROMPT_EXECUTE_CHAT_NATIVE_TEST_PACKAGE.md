# PROMPT: Execute PRH Chat-Native Test Package

Use this chat to execute a regression pilot from `PRH_CHAT_NATIVE_TEST_PACKAGE.zip`.

1. Unpack the package and read `README_START_HERE.md`.
2. Use only the bundled baseline and candidate playbook packages.
3. Record:
   - `execution_mode: chat_native`;
   - `declared_model_label`: the model name selected by the user in the UI;
   - `model_label_verified_by_provider: false`;
   - a unique `chat_id`.
4. Execute the scenarios and repeat count from `campaign.yaml`.
5. For every repeat:
   - start with a clean run envelope;
   - do not copy the previous result;
   - create a run manifest;
   - preserve the raw response;
   - create a normalized trace;
   - run dynamic property evaluation.
6. Never invent API request IDs, provider provenance, or exact token usage.
7. At completion, create `PRH_CHAT_NATIVE_PARTIAL_RESULTS_<chat_id>.zip`.
8. If the package is assigned to one chat only, create the complete results ZIP.
9. The final verdict must not exceed `REVIEW_REQUIRED`.
10. Report the SHA-256 of the results ZIP.

Proceed without additional confirmation.
