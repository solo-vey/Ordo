# PROMPT: Merge PRH Multi-Chat Results

The chat receives several `PRH_CHAT_NATIVE_PARTIAL_RESULTS_<chat_id>.zip` packages and the PRH chat-native backend package.

1. Verify the integrity of every partial package.
2. Verify unique `chat_id` and `run_id` values.
3. Do not treat declared model labels as provider-verified identities.
4. Group results by scenario, baseline/candidate, declared model label, and chat ID.
5. Run dynamic aggregation, differential comparison, stability analysis only for groups with at least three repeats, semantic consensus, cross-chat consistency analysis, and cross-model comparison.
6. Distinguish within-chat stability, cross-chat reproducibility, and cross-model portability.
7. Never issue a provider-level production `GO`.
8. The final chat-native verdict may be `PASS`, `FAIL`, or `REVIEW_REQUIRED`.
9. Create `PRH_CHAT_NATIVE_MULTI_CHAT_MERGED_RESULTS.zip` containing the merged run index, duplicate/missing-run report, per-chat and per-model reports, cross-chat and cross-model reports, backlog, and final chat-native decision.

Proceed without rerunning scenarios.
