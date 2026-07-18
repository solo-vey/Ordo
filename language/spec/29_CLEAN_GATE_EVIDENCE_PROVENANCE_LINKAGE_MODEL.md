# 29. Clean-Gate Evidence / Release Provenance Linkage Model

Status: accepted and implemented in M69.3.

The release evidence set consists of a source report and a provenance wrapper. The source report decides gate status. The wrapper proves identity and execution context.

Invariant:

```text
sha256(bytes(repo_clean_check.json))
  == release_clean_gate_provenance.linkage.report_sha256
```

The wrapper may mirror selected report fields for discovery, but consumers must treat the source report as authoritative. A missing source report is represented explicitly and is never interpreted as a passed gate.
