# APF Session Package Load and Cache

Status: integrated (M80.4)

APF loads and validates an unchanged package once per session. Before each active-node execution it evaluates `PACKAGE_RELOAD_NECESSITY_GATE`. A valid matching cache returns `PACKAGE_CACHE_HIT`; repeated unpacking or full rereading is forbidden.

Reload is allowed only when version or SHA-256 fingerprint changes, cache state/location is missing or invalid, a required cached file is missing, validation failed, or the user explicitly requests reload. Cache operations must not advance the process or alter the active node. Failed replacement preserves the prior valid cache and process state.

Trace events: `PACKAGE_CACHE_HIT`, `PACKAGE_CACHE_MISS`, `PACKAGE_RELOAD_REQUIRED`, `PACKAGE_RELOAD_COMPLETED`, `PACKAGE_CACHE_INVALIDATED`.
