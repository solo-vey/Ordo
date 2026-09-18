# Artifact Delivery Lifecycle

Generated package output is not automatically approved or delivered. Every
artifact in `generated_outputs/output_manifest.json` carries a lifecycle bound
to its physical file and SHA-256 digest:

```text
generated -> reviewed -> approved -> delivered
```

The manifest records a package-relative download link for the exact physical
artifact. The link is usable by a package browser or delivery surface and is
checked against the physical file; it cannot silently point to another file.

```text
ordo generate-output PACKAGE
ordo validate-artifact-lifecycle PACKAGE
ordo advance-artifact-lifecycle PACKAGE --artifact ARTIFACT_ID --to reviewed --actor reviewer-id
ordo advance-artifact-lifecycle PACKAGE --artifact ARTIFACT_ID --to approved --actor approver-id
ordo advance-artifact-lifecycle PACKAGE --artifact ARTIFACT_ID --to delivered --actor delivery-service
```

`validate-artifact-lifecycle` fails closed when an artifact file is missing,
its hash differs from the manifest, its download link is missing or points to
another file, or reviewer/approval/delivery evidence is incomplete. It also
rejects a premature transition such as `generated -> approved`.

The lifecycle commands update the output manifest and write a transition or
validation report. They do not treat an output-generation report, a template,
or a chat statement as completion evidence; the physical output remains the
source of completion evidence.
