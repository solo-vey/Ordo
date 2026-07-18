# OpenTimestamps Verification Instructions

Verify the proof against the unchanged evidence ZIP included in `EVIDENCE/`.

```bash
ots verify INDEPENDENCE_EVIDENCE/INDEPENDENT_DEVELOPER_ORDO_ARF_ADOPTION_EVIDENCE_PACKAGE.zip.ots
```

Run the command from the submission root. The OpenTimestamps client infers the timestamped target filename; if needed, copy the proof beside the evidence ZIP or use the client workflow supported by your environment.

Expected target SHA-256:

```text
5327e261edea7f7f1e43a73c0c1dc1bd28a3ce6879e7f9af3335175ac52ed65c
```

A successful independent verification should identify a Bitcoin block and an attested existence time. Record the verifier, verification time, client version, and result in your evidence registry.
