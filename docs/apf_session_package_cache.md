# APF session package load and cache

Status: integrated into APF in M80.4.

`SESSION_PACKAGE_LOAD_AND_CACHE` prevents repeated unpacking and full rereading of the same validated package. `PACKAGE_RELOAD_NECESSITY_GATE` compares version, SHA-256 fingerprint, manifest status, cache availability and required files before every node. Cache checks and reloads preserve the active APF node and process state.

A reload is permitted only for an actual package change, invalid or lost cache, missing cached file, failed validation, or explicit user request.
