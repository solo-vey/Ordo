# Contracts and Artifact Coverage

This document links the M46 contract/artifact layer to the runtime model.

`compile` checks whether contract and artifact references are structurally valid.

`coverage` checks whether confirmed contracts have artifact requirements.

`validate-artifacts` checks rendered artifacts against confirmed values.

`consistency` checks whether rendered artifacts disagree with each other.

`go-no-go` combines the pipeline into a final decision.

Important boundary:

```text
compile != final package valid
```

A package may compile successfully and still fail because a confirmed contract value is missing from Passport, Jira, QA, Implementation Prompt, or JSON reports.
