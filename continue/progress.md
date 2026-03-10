# Progress Log

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
