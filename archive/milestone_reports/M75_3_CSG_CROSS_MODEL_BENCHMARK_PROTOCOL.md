# M75.3 — CSG Cross-Model and Repeated-Run Benchmark Protocol

Status: infrastructure implemented; evidence collection open.

Production benchmark policy:

- at least 3 distinct provider/model-version targets;
- at least 2 blind runs per target;
- the canonical 26-case dataset must be used unchanged;
- every run must pass the existing M74.3 thresholds;
- synthetic, fixture, dry-run, or label-visible evidence is rejected;
- all score files must use one dataset version;
- raw evidence and deterministic score reports must be retained.

Command:

```bash
python3 -m ordo_pathwalk.cli csg-benchmark-aggregate \
  --scores-dir <score-files-directory> \
  --out CSG_CROSS_MODEL_BENCHMARK_REPORT.json
```

Current evidence:

- OpenAI / GPT-5.6 Thinking: 1 passing blind run.

The gate remains blocked until two additional targets and repeat runs are supplied.
