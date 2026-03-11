#!/usr/bin/env bash

set -euo pipefail

python -m pytest -v \
  tests/test_baseline_bridge.py \
  tests/test_baseline_formats.py \
  tests/test_baseline_registry.py \
  tests/test_baseline_runner.py \
  tests/test_local_encoders.py \
  tests/test_persistence.py

python -m pytest -v \
  tests/test_audit_dataset.py \
  tests/test_audit_gating.py \
  tests/test_audit_losses.py \
  tests/test_audit_merge.py \
  tests/test_audit_support.py \
  tests/test_cli.py \
  tests/test_config.py \
  tests/test_conflict_stress_pipeline.py \
  tests/test_conflict_stress_rules.py \
  tests/test_data_cli.py \
  tests/test_data_protocol.py \
  tests/test_delivery_bundle.py \
  tests/test_delivery_review.py \
  tests/test_experiment_modules.py \
  tests/test_experiment_runner.py

python -m pytest -v \
  tests/test_graph_adapters.py \
  tests/test_graph_builders.py \
  tests/test_graph_cache.py \
  tests/test_graph_types.py \
  tests/test_metrics_faithfulness.py \
  tests/test_metrics_ranking.py \
  tests/test_metrics_usage.py \
  tests/test_priors_aggregate.py \
  tests/test_priors_heuristics.py \
  tests/test_priors_nuisance.py \
  tests/test_recbole_adapter.py

python -m pytest -v \
  tests/test_reranker_forward.py \
  tests/test_reranker_validation.py \
  tests/test_train_cli.py \
  tests/test_train_engine.py \
  tests/test_train_losses.py \
  tests/test_transport_sanity.py \
  tests/test_transport_solver.py
