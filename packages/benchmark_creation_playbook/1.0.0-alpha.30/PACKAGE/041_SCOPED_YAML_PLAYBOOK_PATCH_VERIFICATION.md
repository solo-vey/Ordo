# 041 — Scoped YAML Playbook Patch Verification

## Purpose
Prevent a local YAML playbook change from silently rebuilding or semantically changing unrelated nodes.

## Required patch declaration
Every patch MUST declare:
- baseline and candidate file checksums;
- affected node-ID allowlist;
- optional allowed JSON/YAML paths;
- expected semantic effect;
- prohibited side effects.

## Enforceable gate
`tools/verify_scoped_yaml_patch.py`:
1. parses both YAML files;
2. indexes every mapping with an `id`;
3. computes canonical structural hashes per node;
4. reports added, removed and changed IDs;
5. rejects changed IDs outside the allowlist;
6. reports path-level semantic differences;
7. proves unchanged nodes retain identical canonical hashes;
8. rejects an empty allowlist, duplicate IDs, parse errors and unexplained global changes.

## Acceptance
PASS requires:
- all changed node IDs are allowlisted;
- no removed/added ID is unexplained;
- unchanged-node hash ratio is reported;
- structural and semantic diff reports are persisted;
- exit code is `0`.

Any violation returns non-zero and the patch MUST be rejected or rolled back.
