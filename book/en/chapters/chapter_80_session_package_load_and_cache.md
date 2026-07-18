# Chapter 80. Session Package Load and Cache

A practical problem appeared in long APF/playbook sessions: the model could unpack the archive and reread package files at every step.

```text
unpack → read → execute one step
→ unpack → read → execute next step
```

This is slow, creates noise, and increases the risk that different steps rely on different reread fragments.

M80 introduces a session package load-and-cache contract.

## Load once

After the first successful package-read pass, runtime records:

```text
package_loaded
package_version
package_fingerprint
unpacked_location
manifest_validated
source_of_truth_loaded
```

If the package version and fingerprint have not changed, the validated package is reused within the current session.

## Reload conditions

A repeated unpack/read is required only when:

```text
new package version supplied
fingerprint changed
runtime cache lost
required file missing
manifest validation failed
explicit full reload requested
```

## Cache hit

The correct runtime flow is:

```text
MESSAGE_RECEIVED
→ PACKAGE_CACHE_CHECK
→ cache valid: use loaded baseline
→ cache invalid: unpack + validate + load
→ ACTIVE_NODE_EXECUTION
```

After a valid cache hit, another full unpack/read is forbidden.

## Trace and diagnostics

Runtime records events such as:

```text
PACKAGE_CACHE_HIT
PACKAGE_RELOAD_REQUIRED
PACKAGE_LOADED
PACKAGE_CACHE_INVALID
```

Metrics and diagnostics make unnecessary reloads and invalidation reasons visible.

## APF and playbook boundary

Fingerprinting, cache validation, reload conditions, and trace events belong to the APF/runtime contract.

A specific playbook may contain a short instruction not to reread the factory package at every step, but it must not invent its own cache semantics.

The main M80 principle is:

```text
validate once;
reuse while fingerprint is stable;
reload only for an explicit reason;
record cache behavior in trace.
```
