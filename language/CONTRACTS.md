# Contracts

A contract is a first-class Ordo object that records values confirmed or rejected during a process.

Contracts are the bridge between guided intake and generated artifacts. A contract field is not safe to rely on unless it has an explicit status.

## Field statuses

```text
missing
candidate
proposed
confirmed
blocked
not_applicable
```

## Minimum contract shape

```json
{
  "kind": "contract",
  "id": "G_EVENT_IDENTITY_CONTRACT",
  "status": "confirmed",
  "fields": {
    "alias": { "value": "LU_CHANGE_CAPITAL", "status": "confirmed", "required": true }
  }
}
```

## Rule

A generated artifact may not present a `candidate` or `proposed` field as if it were `confirmed`.
