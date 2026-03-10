# Reproducibility Checklist

- Install dependencies from `pyproject.toml`
- Run `python -m pytest -v`
- Run `bash scripts/check.sh`
- Run `python -m ciept.train.cli --mode train`
- Run `python -m ciept.train.cli --mode eval`
- Run `python -m ciept.data.stress_cli --input-jsonl ... --output-dir ...`
- Run `python -m ciept.audit.audit_cli build ...`
- Run experiment dispatch through `ciept.experiments.runner.run_experiment(...)`

## Deferred External Assets
- Real datasets not downloaded
- Real VLM not connected
- External baselines not integrated