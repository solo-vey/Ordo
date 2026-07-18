# 31. Language / CLI Repository Root Contract Model

`root_contract` is a repository-hygiene treatment for non-package roots.

A root contract may declare `required_paths`, `yaml_globs`, `json_globs`, and `python_globs`. Validation is deterministic, read-only, path-contained, and reports `passed` or `blocked`.

`root_contract` does not replace package-level `clean-check`. It complements it for repository roots whose structure is not defined by `ordo.yml`.
