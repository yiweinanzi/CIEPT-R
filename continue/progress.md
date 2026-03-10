# Progress Log

## 2026-03-10 12:15 UTC - T010

- Goal: Add an audit-dataset protocol that can export samples for VLM pre-annotation, merge predictions back, and initialize human adjudication queues.
- Changes: Extended `src/ciept/audit/` with audit dataset schemas, audit-example generation from stress artifacts, VLM request export, VLM prediction merge, adjudication queue initialization, and a file-based CLI for the full protocol.
- Verification: `python -m pytest tests/test_audit_dataset.py -v`; `python -m pytest tests/test_audit_merge.py tests/test_persistence.py::test_t010_marked_done_and_t011_selected_next -v`; `python -m pytest -v`; `bash scripts/check.sh`.
- Risks/Next: Continue from `T011` with ranking, faithfulness, and usage-diagnosis metrics that can consume audit examples and adjudication artifacts.

## 2026-03-10 12:02 UTC - T009

- Goal: Add a protocol-driven offline conflict stress-test pipeline that generates nuisance/lure artifacts and review metadata.
- Changes: Extended `src/ciept/data/` with perturbation schemas, positive-preserving nuisance rules, negative-preserving lure rules, a JSONL-based offline pipeline, and a CLI that writes perturbed examples, nuisance masks, protocol summaries, and review queues under `data/interim/`.
- Verification: `python -m pytest tests/test_conflict_stress_rules.py -v`; `python -m pytest tests/test_conflict_stress_pipeline.py tests/test_persistence.py::test_t009_marked_done_and_t010_selected_next -v`; `python -m pytest -v`; `bash scripts/check.sh`.
- Risks/Next: Continue from `T010` with VLM audit-set structures that can consume the perturbation artifacts written here.

## 2026-03-10 11:52 UTC - T008

- Goal: Add a minimal but executable training/evaluation path that connects reranking, intervention loss, and the main ranking objective.
- Changes: Added `src/ciept/train/` and `src/ciept/eval/` with `confidence-weighted ListMLE`, toy batch generation, a train step, an eval step, simple ranking metrics, and a CLI for `train`/`eval` modes.
- Verification: `python -m pytest tests/test_train_losses.py tests/test_train_engine.py -v`; `python -m pytest tests/test_train_cli.py tests/test_persistence.py::test_t008_marked_done_and_t009_selected_next -v`; `python -m pytest -v`; `bash scripts/check.sh`.
- Risks/Next: Continue from `T009` with the conflict stress-test and nuisance/lure perturbation protocol on top of the now-runnable toy train/eval loop.

## 2026-03-10 11:40 UTC - T007

- Goal: Add the first trainable-style intervention layer on top of transport outputs, centered on normalized support and leakage-ratio diagnostics.
- Changes: Added `src/ciept/audit/` with support normalization, support logits, binary Gumbel/STE gating, ratio-based leakage, a lightweight scorer, and a single-pass intervention loss that returns gate, counterfactual scores, and component losses.
- Verification: `python -m pytest tests/test_audit_support.py tests/test_audit_gating.py -v`; `python -m pytest tests/test_audit_losses.py tests/test_persistence.py::test_t007_marked_done_and_t008_selected_next -v`; `python -m pytest -v`; `bash scripts/check.sh`.
- Risks/Next: Continue from `T008` with ranking/training entrypoints that can consume the new reranker and intervention modules.

## 2026-03-10 11:29 UTC - T006

- Goal: Introduce a torch-based reranker skeleton that turns cost, `source_mass`, `target_capacity`, and `mass_budget` into a real transport-based forward pass.
- Changes: Extended `src/ciept/transport/` with torch-native reranker inputs/outputs, pairwise feature costs, capacity penalties, a partial-transport projection operator, and a `CapacityCalibratedPartialTransportReranker` that emits a scalar score plus transport diagnostics. Added `torch` to the dependency surface and installed it in the active environment for this task.
- Verification: `python -m pytest tests/test_reranker_forward.py tests/test_reranker_validation.py -v`; `python -m pytest tests/test_persistence.py::test_t006_marked_done_and_t007_selected_next -v`; `python -m pytest -v`; `bash scripts/check.sh`.
- Risks/Next: Continue from `T007` with normalized support and intervention logic, reusing this reranker as the model-side transport entrypoint.

## 2026-03-10 11:12 UTC - T005

- Goal: Validate partial transport semantics with a NumPy toy solver before attempting a larger reranker.
- Changes: Added `src/ciept/transport/` with typed transport problems/results, an iterative partial-projection mini-solver, and semantic helpers for capacity constraints and reject-mass checks.
- Verification: `python -m pytest tests/test_transport_solver.py -v`; `python -m pytest tests/test_transport_sanity.py tests/test_persistence.py::test_t005_marked_done_and_t006_selected_next -v`; `python -m pytest -v`; `bash scripts/check.sh`.
- Risks/Next: Continue from `T006` with a larger transport reranker, reusing the toy solver behavior as a semantic regression baseline.

## 2026-03-10 10:56 UTC - T004

- Goal: Build a runnable heuristic prior layer for reliability, capacity priors, and nuisance masks on top of the graph boundary.
- Changes: Added `src/ciept/priors/` with metadata-first corroboration/stability/vulnerability heuristics, interpretable reliability aggregation, safe `q_cap` normalization, and nuisance inference that prefers explicit labels but falls back to slightly aggressive heuristics.
- Verification: `python -m pytest tests/test_priors_heuristics.py tests/test_priors_aggregate.py -v`; `python -m pytest tests/test_priors_nuisance.py tests/test_persistence.py::test_t004_marked_done_and_t005_selected_next -v`; `python -m pytest -v`; `bash scripts/check.sh`.
- Risks/Next: Continue from `T005` with toy partial transport sanity checks using the new reliability and capacity outputs as inputs.

## 2026-03-10 10:36 UTC - T003

- Goal: Define the graph-facing interfaces for item evidence nodes, strict block-diagonal topology, and cache serialization.
- Changes: Added `src/ciept/graph/` with dataclass-based node and topology types, block-diagonal topology builders, cache round-trip helpers, and an adapter placeholder that keeps tensor logic deferred.
- Verification: `python -m pytest tests/test_graph_types.py tests/test_graph_builders.py -v`; `python -m pytest tests/test_graph_cache.py tests/test_persistence.py::test_t003_marked_done_and_t004_selected_next -v`; `python -m pytest -v`; `bash scripts/check.sh`.
- Risks/Next: Continue from `T004` with reliability prior, capacity prior, and nuisance mask interfaces on top of the graph boundary defined here.

## 2026-03-10 10:08 UTC - T002

- Goal: Establish the offline data protocol with deterministic global temporal splitting and explicit missing-modality handling.
- Changes: Added `data/` directory conventions, `ciept.data` package with iterative k-core filtering and `80/10/10` global split helpers, plus a CLI that writes `train.csv`, `valid.csv`, `test.csv`, and `protocol_summary.json`.
- Verification: `python -m pytest tests/test_data_protocol.py tests/test_data_cli.py -v`; final full-suite verification pending before commit.
- Risks/Next: Continue from `T003` with evidence graph and block-diagonal topology interfaces on top of the new dataset contract. Raw Amazon Reviews 2023 download was deferred after confirming the three main categories plus meta are about 73 GB, while `/root/autodl-tmp` currently has about 45 GB free.

## 2026-03-10 09:57 UTC - T001

- Goal: Bootstrap the repository into a runnable Python project with persistent agent state and verification.
- Changes: Added `README.md`, `pyproject.toml`, `configs/base.yaml`, `src/ciept/` package, `scripts/check.sh`, bootstrap tests, and the `continue/` persistence workflow files. Expanded `continue/task.json` by decomposing `aaai项目.md` into staged engineering tasks `T002` through `T013`.
- Verification: `python -m pytest tests/test_persistence.py::test_continue_task_file_exists_and_has_bootstrap_task -v`; `python -m pytest tests/test_config.py tests/test_cli.py -v`; final full-suite verification pending before commit.
- Risks/Next: Run full verification, then continue from `T002` with data protocol and global temporal split.

## 2026-03-10 09:30 UTC - INIT

- Goal: Establish the repository bootstrap plan and persistent workflow files.
- Changes: Added initial workflow template and prepared `T001` as the first executable task.
- Verification: Pending bootstrap implementation.
- Risks/Next: Complete `T001` with runnable package, tests, and verification script.
