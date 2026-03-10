# Entrypoints

- Data: `python -m ciept.data.cli`
- Stress protocol: `python -m ciept.data.stress_cli`
- Audit protocol: `python -m ciept.audit.audit_cli build|export-vlm|merge-vlm|init-adjudication`
- Train/eval: `python -m ciept.train.cli --mode train|eval`
- Delivery: `python -m ciept.delivery.cli --output-dir deliverables/current`