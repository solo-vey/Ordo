# APF Improvement — Session Package Load and Cache

Status: in-progress — M80.0–M80.1 implemented

## Problem

Some APF chats repeatedly unpack and reread the same unchanged package at every node. This wastes execution time and can introduce inconsistent rereads.

## Capability

`SESSION_PACKAGE_LOAD_AND_CACHE`

After the first successful package-read pass, APF records:

```yaml
package_runtime_state:
  package_loaded: true
  package_version: <version>
  package_fingerprint: <sha256>
  unpacked_location: <runtime-path>
  manifest_validated: true
  source_of_truth_loaded: true
```

## Gate

`PACKAGE_RELOAD_NECESSITY_GATE`

When package version and fingerprint are unchanged and the validated session cache is present, repeated unpack/full-read is prohibited.

Reload is allowed only when:

- a new package or version is supplied;
- the fingerprint changes;
- the runtime cache is unavailable or invalid;
- a required file is missing;
- manifest/checksum validation fails;
- the user explicitly requests a full reread.

## Runtime sequence

`MESSAGE_RECEIVED → PACKAGE_CACHE_CHECK → CACHE_HIT or RELOAD_REQUIRED → ACTIVE_NODE_EXECUTION`

## Required trace events

- `PACKAGE_CACHE_HIT`
- `PACKAGE_CACHE_MISS`
- `PACKAGE_RELOAD_REQUIRED`
- `PACKAGE_RELOAD_COMPLETED`
- `PACKAGE_CACHE_INVALIDATED`

## Scope

The mechanism belongs to the APF runtime contract. Generated playbooks inherit it automatically; playbook-specific instructions should contain only a short non-repetition rule.


M80.1 completed: deterministic fingerprinting, atomic cache-state persistence, staged load/replace, rollback and invalidate operations.
