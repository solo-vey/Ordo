# alpha.20.0.50-dev — artifact supersession-aware evidence verification

R3 generic evidence fix.

- Release evidence verification evaluates the latest active materialization per artifact path.
- Older materializations remain in lineage as historical/superseded evidence and do not block acceptance.
- A stale or unknown-dependency latest materialization still fails closed.
- No playbook/domain semantics are interpreted.
