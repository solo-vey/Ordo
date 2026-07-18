# `ordo go-no-go`

`ordo go-no-go` is the M46.5 deterministic helper that returns a final machine-readable decision for an Ordo package review.

It composes existing checks:

```text
lint → compile → coverage → validate-state → validate-artifacts → consistency
```

It writes:

```text
reports/GO_NO_GO_REPORT.json
```

Exit codes:

- `0` — `go`
- `1` — any `no_go*` status

Typical use after generated artifacts already exist:

```bash
ordo go-no-go packages/history_event_guided_intake \
  --answers packages/history_event_guided_intake/run_inputs/intake_success.yaml
```

Typical use when the package must first run guided intake and render outputs:

```bash
ordo go-no-go packages/history_event_guided_intake \
  --run-intake \
  --answers packages/history_event_guided_intake/run_inputs/intake_success.yaml \
  --generate-output
```

Known limits:

- It does not execute an AI model.
- It does not call live REST, Mongo, queues, or product services.
- It validates declared contracts, generated artifacts, and cross-artifact consistency.

After `ordo intake` has already produced `reports/intake_report.json`, M46.6 allows the shorter form:

```bash
ordo go-no-go packages/history_event_guided_intake
```

In this case the helper reuses the latest embedded intake state unless `--state` or `--answers` is provided explicitly.

