# CLI workflow

Standard Runtime Mode workflow:

```bash
ordo runtime-status <package>
ordo lint <package>
ordo compile <package>
ordo test <package>
ordo coverage <package>
ordo runtime-entry <package>
ordo intake <package> --answers <answers-file> --non-interactive
ordo validate-state <package> --answers <answers-file>
ordo check-gate <package> <GATE_ID> --answers <answers-file>
ordo next-step <package> --answers <answers-file>
ordo generate-output <package> --out <output-dir>
ordo validate-output <package>
ordo validate-artifacts <package> --artifacts <output-dir>
ordo consistency <package> --artifacts <output-dir>
ordo go-no-go <package>
ordo validate-cli-status <report.json>
ordo package <package> --out <package.zip>
```

Use `ordo --help` and subcommand `--help` as source of truth for exact arguments.

`compile` checks source-to-IR validity. It does not prove generated artifacts are complete or consistent.

## M57 Runtime Checkpoint Discipline

Runtime Mode now enforces a checkpoint layer: one node, one contract, and one decision at a time. Helper reports expose `checkpoint_table`, `earliest_incomplete_node`, `open_required_fields`, and `forward_allowed`. `next-step` prioritizes the earliest incomplete node, and `generate-output` is blocked while checkpoint gaps remain. Detailed rules live in `language/RUNTIME_CHECKPOINTS.md` and package `START_HERE_RUNTIME_MODE.md`; minimal runtime prompts stay minimal.



## M59.1 embedded runtime workflow

For runtime packages, prefer the package-owned CLI:

```bash
cli_embedded/ordo runtime-entry .
cli_embedded/ordo next-step . --state run_state.json
cli_embedded/ordo check-gate . <GATE_ID> --state run_state.json
cli_embedded/ordo validate-state . --state run_state.json
```

If `cli_embedded/ordo` cannot run, stop and report that determinism is not enforced.
