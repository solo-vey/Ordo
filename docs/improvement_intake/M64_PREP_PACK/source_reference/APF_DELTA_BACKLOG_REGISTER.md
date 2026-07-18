# APF Delta Backlog Register

Status: current  
Version: APF v0.1.0-rc.4-post-svg  
Register path: `backlog/APF_DELTA_BACKLOG_REGISTER.md`  
Policy: `docs/DELTA_BACKLOG_CONVENTION_POLICY.md`  
Transfer preservation rule: `delta_files_included_in_transfer_package`  
Ordering rule: `delta_backlog_order_preserved_across_chats`

## Required metadata model

Every row in this register uses the following fields:

```text
source_file
item_id
scope
priority
version_target
decision_status
ordering_position
transfer_status
```

Allowed decision_status values:

```text
implement-now
implement-later
defer
reject
superseded
```

## Current ordered delta intake records

| ordering_position | source_file | item_id | scope | priority | version_target | decision_status | transfer_status |
|---:|---|---|---|---|---|---|---|
| 1 | `APF_FULL_BACKLOG_CURRENT.md` | `RC3-P6` | base APF delta/backlog transfer discipline | high-lightweight | `0.1.0-rc.3-p6` | implement-now | included-in-transfer |
| 2 | `APF_BASE_PACKAGE_IMPROVEMENTS_BACKLOG.md` | `RC4-SVG-01` | packaged SVG graph generator utility | high | `0.1.0-rc.4-svg` | implement-now | implemented-included-in-transfer |
| 3 | `APF_BASE_PACKAGE_DELTA_INSTRUCTIONS_COMPILE_AND_START_PROMPT.md` | `FUTURE-COMPILE-01` | compile capability in base APF package | high | `0.1.0-rc.4-post-svg` | implement-now | implemented-included-in-transfer |
| 4 | `APF_BASE_PACKAGE_DELTA_INSTRUCTIONS_COMPILE_AND_START_PROMPT.md` | `FUTURE-COMPILE-02` | compile utility discovery gate | high | `0.1.0-rc.4-post-svg` | implement-now | implemented-included-in-transfer |
| 5 | `APF_BASE_PACKAGE_DELTA_INSTRUCTIONS_COMPILE_AND_START_PROMPT.md` | `FUTURE-COMPILE-03` | runtime compilation verification hardening | high | `0.1.0-rc.4-post-svg` | implement-now | implemented-included-in-transfer |
| 6 | `APF_BASE_PACKAGE_DELTA_INSTRUCTIONS_COMPILE_AND_START_PROMPT.md` | `FUTURE-PROFILE-01` | package profile gate | high | `0.1.0-rc.4-post-svg` | implement-now | implemented-included-in-transfer |
| 7 | `APF_BASE_PACKAGE_DELTA_INSTRUCTIONS_COMPILE_AND_START_PROMPT.md` | `FUTURE-START-01` | generated package start prompt | high | `0.1.0-rc.4-post-svg` | implement-now | implemented-included-in-transfer |
| 8 | `APF_BASE_PACKAGE_DELTA_INSTRUCTIONS_COMPILE_AND_START_PROMPT.md` | `FUTURE-START-02` | human start guide | high | `0.1.0-rc.4-post-svg` | implement-now | implemented-included-in-transfer |
| 9 | `APF_BASE_PACKAGE_DELTA_INSTRUCTIONS_COMPILE_AND_START_PROMPT.md` | `FUTURE-START-03` | README startup section | high | `0.1.0-rc.4-post-svg` | implement-now | implemented-included-in-transfer |
| 10 | `APF_BASE_PACKAGE_DELTA_INSTRUCTIONS_COMPILE_AND_START_PROMPT.md` | `FUTURE-START-04` | start prompt packaging gate | high | `0.1.0-rc.4-post-svg` | implement-now | implemented-included-in-transfer |
| 11 | `APF_BASE_PACKAGE_DELTA_INSTRUCTIONS_COMPILE_AND_START_PROMPT.md` | `FUTURE-START-05` | README startup section gate | high | `0.1.0-rc.4-post-svg` | implement-now | implemented-included-in-transfer |
| 12 | `APF_BASE_PROCESS_PROGRAM_LEVEL_METADATA_IMPROVEMENT_PROMPT.md` | `FUTURE-PROGRAM-CONTRACT-01` | program-level metadata, interaction semantics, rail policy and approval gates | high | post-rc4 / future base APF process patch | implement-later | preserved-for-transfer |
| 13 | `APF_FUTURE_BACKLOG_AFTER_RC4_SVG.md` | `FUTURE-HASH-01` | checksum-based derived artifact stale detection | medium-high | later tooling | implement-later | preserved-for-transfer |
| 14 | `APF_FUTURE_BACKLOG_AFTER_RC4_SVG.md` | `FUTURE-LIVE-01` | real APF module confusion test-case generation utility | medium | later tooling | defer | preserved-for-transfer |

## Gate status

```text
DELTA_BACKLOG_CONVENTION_GATE: passed
G_DELTA_BACKLOG_ITEM_CLASSIFIED: passed
G_DEFERRED_DELTA_ITEMS_PRESERVED_FOR_TRANSFER: passed
G_DELTA_BACKLOG_ORDER_PRESERVED: passed
G_DELTA_SOURCE_FILES_INCLUDED_IN_TRANSFER_PACKAGE: passed
```

## Notes

- `RC3-P6` is implemented now.
- `RC4-SVG-01` is implemented in `0.1.0-rc.4-svg` and included in transfer artifacts.
- Compile/profile/start-prompt items were implemented in `0.1.0-rc.4-post-svg`.
- `APF_BASE_PROCESS_PROGRAM_LEVEL_METADATA_IMPROVEMENT_PROMPT.md` is recorded as the next high-priority future base-process improvement, not implemented in this patch.
- Deferred items remain visible and must not be removed from future transfer packages without an explicit `reject` or `superseded` decision.
