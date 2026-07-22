# Repository Hygiene

Ordo uses one policy with two enforcement scopes.

## Development scope

Development scope blocks forbidden paths only when Git tracks them. Local untracked virtual environments, caches, editable-install metadata, coverage files, and operating-system metadata are reported as transient observations but do not block normal development.

Run:

```bash
ordo repo-check . --clean --profile standard --hygiene-scope development --fail-on-warning
```

## Release scope

Release scope scans every path in an isolated tracked-tree export. Any forbidden path blocks the release candidate.

Run against a clean export:

```bash
rm -rf /tmp/ordo-release-candidate
mkdir -p /tmp/ordo-release-candidate
git archive --format=tar HEAD | tar -xf - -C /tmp/ordo-release-candidate
ordo repo-check /tmp/ordo-release-candidate   --clean   --profile strict   --hygiene-scope release   --fail-on-warning
```

## Forbidden categories

The canonical categories are declared in [`../repo_hygiene.yml`](../repo_hygiene.yml):

- Python bytecode, caches, and editable-install metadata;
- virtual environments;
- pytest and coverage output;
- macOS and editor metadata;
- Ordo temporary workspaces;
- transient CI and release reports;
- temporary files.

`.gitignore` prevents common accidental additions, but the hygiene gate remains authoritative.

## Duplicate nesting

Development scope blocks duplicate nesting only when the affected path is Git-tracked. Release scope scans the complete isolated export. The gate detects adjacent repeated directory segments and repository-name nesting such as `Ordo/Ordo/`. Historical provenance removed from the active tree is retained through the checksum-bound external archive locator in [`EXTERNAL_ARCHIVES.md`](EXTERNAL_ARCHIVES.md).

## Generated outputs

New local generated output belongs under `.ordo-generated/` or an external temporary directory. CI evidence should be uploaded as workflow artifacts rather than committed.

Package-level canonical templates remain governed by package contracts. The repository hygiene gate does not silently redefine package semantics.

## Fail-closed behavior

Pull-request and main-branch clean gates use `--fail-on-warning`. The release clean gate validates an isolated export for pull requests, manual runs, and version tags.
