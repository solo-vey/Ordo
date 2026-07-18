# M70.4 Production CI/Release Validation

M70.4 validates the already implemented production repository hygiene path. It adds no new hygiene engine and no new language behavior.

Validated chain:

1. `repo_hygiene.yml` marks `language/` and `cli/` as release-blocking `root_contract` roots.
2. PR and main workflows invoke the existing `ordo repo-check . --clean` command with the M69 policy profiles.
3. Release workflow invokes the same command with `strict` and `--fail-on-warning`.
4. Release evidence retains the CLI report and its provenance linkage.
5. Standard and strict production smoke runs pass with both release-critical roots checked.

`packages/*` remains delegated. No package-local enforcement is introduced.
