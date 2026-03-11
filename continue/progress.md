# Progress Log

## 2026-03-11 03:24 UTC - B017

- Goal: Move the active baseline focus away from the blocked CLEAR task and prioritize the next non-CLEAR acquisition track.
- Changes: Switched `current_focus` to `B017`, added follow-up acquisition tasks for `RecGOAT`, complete `MAGNET`, and `IGDMRec`, and updated resource tracking to reflect that CLEAR is temporarily deprioritized while other baselines are pursued first.
- Verification: `python -m pytest tests/test_persistence.py::test_b012_to_b016_and_m001_to_m003_follow_up_states_are_recorded -v`; `python -m pytest -v`; `bash scripts/check.sh`.
- Risks/Next: `B017` now becomes the active path; `CLEAR` remains blocked but is no longer the main execution focus.

## 2026-03-11 03:08 UTC - M004

- Goal: Integrate the local `models/Qwen3.5-9B` backend as a lazy VLM wrapper alongside the new local encoder package.
- Changes: Added `src/ciept/encoders/vlm.py`, extended `configs/models/local_backends.yaml` with the local VLM path, and exposed the wrapper through `src/ciept/encoders/__init__.py`.
- Verification: `python -m pytest tests/test_local_encoders.py -v`; lightweight smoke with `transformers`, `sentence-transformers`, `paddleocr`, and the local backend registry confirmed the local VLM path and wrapper are wired.
- Risks/Next: The wrapper is lazy by design; full 9B generation was not forced into CPU memory during smoke verification.

## 2026-03-11 02:58 UTC - M003

- Goal: Integrate PaddleOCR as a local lazy OCR backend.
- Changes: Added `src/ciept/encoders/ocr.py`, installed `paddlepaddle`, and registered the OCR backend in `configs/models/local_backends.yaml`.
- Verification: `python -m pytest tests/test_local_encoders.py -v`; lightweight smoke confirmed `PaddleOCR` import and `LocalPaddleOCREngine` construction.
- Risks/Next: First real OCR call may still download OCR weights if the runtime cache is empty.

## 2026-03-11 02:53 UTC - M002

- Goal: Integrate the local `models/Qwen3-VL-Embedding-2B` backend as a lazy multimodal embedding adapter.
- Changes: Added `src/ciept/encoders/vision.py`, registered the local model path, and installed `transformers` plus `qwen-vl-utils` for runtime support.
- Verification: `python -m pytest tests/test_local_encoders.py -v`; lightweight smoke confirmed local path validation and wrapper construction.
- Risks/Next: Full VL model loading remains lazy to avoid forcing a 2B model into CPU memory during repository verification.

## 2026-03-11 02:48 UTC - M001

- Goal: Integrate the local `models/Qwen3-Embedding-4B` backend as a lazy text embedding adapter.
- Changes: Added `src/ciept/encoders/text.py`, `src/ciept/encoders/registry.py`, and `configs/models/local_backends.yaml`, then installed `sentence-transformers` and `transformers` runtime dependencies.
- Verification: `python -m pytest tests/test_local_encoders.py -v`; lightweight smoke confirmed local path validation and wrapper construction.
- Risks/Next: Full 4B model loading remains lazy to avoid unnecessary memory pressure in CI-like verification.

## 2026-03-11 02:42 UTC - B016

- Goal: Audit MixRec compatibility against the current single-behavior multimodal baseline runner.
- Changes: Classified MixRec as a `runtime_mismatch` in the baseline registry and runner because it depends on TF1.14, multi-behavior datasets, and leave-one-out evaluation instead of the repository's current presplit single-behavior contract.
- Verification: `python -m pytest tests/test_baseline_registry.py tests/test_baseline_runner.py -v`.
- Risks/Next: Keep blocked unless a dedicated multi-behavior compatibility track is added.

## 2026-03-11 02:37 UTC - B015

- Goal: Integrate DiffMM as a candidate baseline through the shared runner.
- Changes: Added `prepare_diffmm_dataset()` to emit `trnMat.pkl`, `tstMat.pkl`, and deterministic placeholder modality features; extended the baseline runner with a DiffMM smoke executor that validates the upstream data loader on prepared presplit data.
- Verification: `python -m pytest tests/test_baseline_formats.py tests/test_baseline_runner.py -v`; ad hoc smoke: `run_baseline(... baseline_name='DiffMM' ...)` produced unified outputs and loaded the upstream DataHandler successfully.
- Risks/Next: The current smoke path validates adapter compatibility rather than full diffusion-model training.

## 2026-03-11 02:31 UTC - B014

- Goal: Integrate SMORE as a candidate multimodal baseline.
- Changes: Reused the MMRec-style family adapter for SMORE, added model-specific scalar overrides in the default smoke executor, and verified the upstream training path on a tiny presplit dataset.
- Verification: `python -m pytest tests/test_baseline_runner.py -v`; ad hoc smoke: `run_baseline(... baseline_name='SMORE' ...)` completed and wrote unified outputs.
- Risks/Next: Continue from the same candidate baseline track with DiffMM and MixRec audit.

## 2026-03-11 02:26 UTC - B013

- Goal: Attempt MAGNET baseline integration and determine whether the downloaded asset is usable.
- Changes: Validated the local archive structure and found that the downloaded MAGNET package lacks the actual model implementation files referenced by its own README. Reclassified it as `asset_incomplete` instead of pretending the baseline is runnable.
- Verification: `python -m pytest tests/test_baseline_registry.py tests/test_baseline_runner.py -v`; ad hoc smoke failed before model load because the archive has no executable MAGNET model package.
- Risks/Next: Blocked until a complete MAGNET code release is acquired.

## 2026-03-11 02:21 UTC - B012

- Goal: Integrate Guider / Teach Me How to Denoise through the shared baseline layer.
- Changes: Added a guided-MMRec integration mode, reused the MMRec formatter, and implemented a lightweight smoke executor that validates teacher/student configuration, data loading, and model construction on a tiny presplit dataset.
- Verification: `python -m pytest tests/test_baseline_runner.py -v`; ad hoc smoke: `run_baseline(... baseline_name='Guider' ...)` completed and wrote unified outputs.
- Risks/Next: Keep the smoke path lightweight because the full teacher/student train loop is heavier than the rest of the bootstrap baselines.

## 2026-03-11 02:16 UTC - B011

- Goal: Close the missing-baseline tracking task after completing the current baseline integration wave.
- Changes: Updated `deliverables/current/required_assets.md` to track still-missing baselines, reclassified the CLEAR asset as a mismatch, and recorded which candidate downloads have already been promoted into known mappings.
- Verification: `python -m pytest tests/test_baseline_registry.py tests/test_baseline_formats.py tests/test_baseline_runner.py -v`; `python -m pytest -v`; `bash scripts/check.sh`.
- Risks/Next: The current task focus remains `B008` because the correct multimodal CLEAR implementation is still missing locally.

## 2026-03-11 02:12 UTC - B010

- Goal: Resolve mapping conclusions for downloaded candidate baselines.
- Changes: Enriched the baseline registry to classify `Guider` as `Teach Me How to Denoise`, `MAGNET` as `Modality-Guided Mixture of Graph Experts`, and keep `DiffMM/MixRec/SMORE` as candidate-only references.
- Verification: `python -m pytest tests/test_baseline_registry.py -v`; `python -m pytest tests/test_baseline_runner.py -v`.
- Risks/Next: Feed the mapping conclusions into missing-asset tracking and keep CLEAR blocked until the correct repository is acquired.

## 2026-03-11 02:08 UTC - B009

- Goal: Integrate the Training-free Graph-based Imputation baseline through the shared baseline layer.
- Changes: Added indexed split/embedding preparation under `src/ciept/baselines/formats.py`, archive handling, graph-imputation runner dispatch, and a default `neigh_mean` smoke executor with a minimal `torch_sparse` stub for bootstrap verification.
- Verification: `python -m pytest tests/test_baseline_formats.py tests/test_baseline_runner.py -v`; ad hoc smoke: `run_baseline(... baseline_name='Training-free Graph-based Imputation' ...)` on a tiny presplit dataset produced standardized outputs and an imputed visual embedding file.
- Risks/Next: The smoke path validates adapter compatibility, not benchmark-scale graph-imputation performance.

## 2026-03-11 02:03 UTC - B008

- Goal: Attempt CLEAR baseline integration and determine whether the downloaded asset is usable.
- Changes: Validated the downloaded archive against the project baseline list and found a hard mismatch: the local `CLEAR-replication-main.zip` is an API recommendation repository, not the required multimodal CLEAR method. Recorded the mismatch in the registry and task state.
- Verification: `python -m pytest tests/test_baseline_registry.py tests/test_baseline_runner.py -v`.
- Risks/Next: Blocked until the correct multimodal CLEAR implementation is downloaded.

## 2026-03-11 01:57 UTC - B007

- Goal: Integrate I3-MRec through the unified baseline layer.
- Changes: Added I3-MRec-specific dataset preparation and a default smoke executor that copies prepared data into the upstream `Data/<dataset>` layout and runs `main.py` with lightweight CPU-safe stubs for `faiss`, `numba`, and `.cuda()` calls.
- Verification: `python -m pytest tests/test_baseline_formats.py tests/test_baseline_runner.py -v`; ad hoc smoke: `run_baseline(... baseline_name='I3-MRec' ...)` on a tiny presplit dataset executed the upstream entrypoint and wrote unified outputs.
- Risks/Next: The smoke path is integration-focused and keeps heavy ANN/runtime dependencies outside the core repository.

## 2026-03-11 01:50 UTC - B006

- Goal: Integrate MGCN through the shared MMRec-style baseline path.
- Changes: Reused the MMRec formatter and runner family for MGCN, adding a default smoke executor that injects lightweight `torchvision` and `torch_scatter` stubs for bootstrap execution on CPU.
- Verification: `python -m pytest tests/test_baseline_formats.py tests/test_baseline_runner.py -v`; ad hoc smoke: `run_baseline(... baseline_name='MGCN' ...)` on a tiny presplit dataset completed and wrote unified outputs.
- Risks/Next: The bootstrap smoke path validates compatibility, while full benchmark runs still belong to later experiment execution on real datasets.

## 2026-03-11 01:43 UTC - B005

- Goal: Integrate BM3 through the shared MMRec-style baseline path.
- Changes: Added archive extraction plus MMRec `.inter`/feature preparation and a default smoke executor that bootstraps the upstream trainer with small CPU-safe overrides.
- Verification: `python -m pytest tests/test_baseline_formats.py tests/test_baseline_runner.py -v`; ad hoc smoke: `run_baseline(... baseline_name='BM3' ...)` on a tiny presplit dataset completed and wrote unified outputs.
- Risks/Next: Continue the same adapter family for MGCN.

## 2026-03-11 01:35 UTC - B004

- Goal: Integrate VBPR through the unified baseline layer.
- Changes: Added VBPR-specific numeric interaction/visual-feature preparation, archive extraction, and a default smoke executor that trains the upstream `VBPR` model for one lightweight pass on prepared presplit data.
- Verification: `python -m pytest tests/test_baseline_formats.py tests/test_baseline_runner.py -v`; ad hoc smoke: `run_baseline(... baseline_name='VBPR' ...)` on a tiny presplit dataset produced unified outputs with valid/test AUC metrics.
- Risks/Next: Continue with the MMRec-style multimodal baselines.

## 2026-03-11 01:27 UTC - B003

- Goal: Integrate LightGCN on top of the RecBole data bridge and shared baseline runner.
- Changes: Fixed the RecBole runtime path to use `data_path/<dataset>/` layout, upgraded the baseline runner with a default RecBole smoke executor, and verified that LightGCN can read the bridged presplit dataset and emit standardized outputs.
- Verification: `python -m pytest tests/test_baseline_runner.py -v`; ad hoc smoke: `run_baseline(... baseline_name='LightGCN' ...)` on a tiny presplit dataset completed through RecBole and wrote unified outputs.
- Risks/Next: Continue baseline-family integrations on top of the now-working runner.

## 2026-03-11 01:17 UTC - B002

- Goal: Build a baseline-only bridge from presplit CIEPT datasets into RecBole benchmark files and add a unified baseline runner without coupling RecBole into the core research stack.
- Changes: Added `src/ciept/baselines/data_bridge.py` to validate `train/valid/test.csv` and emit RecBole-style `*.train.inter` / `*.valid.inter` / `*.test.inter` plus optional `.item` and a bridge manifest; added `src/ciept/baselines/runner.py` with a standardized request/result contract, `results/baselines/<baseline>/<run_id>/` outputs, recbole-backed dispatch via injected executor, and explicit `external_script` rejection for later tasks; updated the RecBole config helper, package exports, B002 design/plan docs, and persistence coverage.
- Verification: `python -m pytest tests/test_baseline_bridge.py tests/test_baseline_runner.py tests/test_recbole_adapter.py -v`; `python -m pytest tests/test_persistence.py::test_b002_recbole_bridge_task_marked_done_and_b003_selected_next -v`; `python -m pytest -v`; `bash scripts/check.sh`.
- Risks/Next: Continue from `B003` with concrete LightGCN execution on top of the shared bridge/runner path; the default RecBole executor still requires task-specific wiring once a real baseline is integrated.

## 2026-03-11 00:10 UTC - B001

- Goal: Inventory downloaded baselines, classify direct/mapped/missing assets, and bootstrap a RecBole helper layer without changing the core `ciept` research stack.
- Changes: Added `src/ciept/baselines/` with baseline inventory classification and RecBole config helpers, added `configs/baselines/recbole_base.yaml`, and expanded `continue/task.json` with a baseline integration track `B001-B011`.
- Verification: `python -m pytest tests/test_baseline_registry.py tests/test_recbole_adapter.py -v`; `python -m pytest tests/test_persistence.py::test_b001_baseline_inventory_task_marked_done -v`; `python -m pytest -v`; `bash scripts/check.sh`.
- Risks/Next: Continue from `B002` with a real RecBole dataset bridge and unified baseline runner before integrating baselines one by one.

## 2026-03-10 13:04 UTC - T013

- Goal: Build a reproducible delivery bundle that snapshots the repository state, indexes results, lists required external assets, and reviews current implementation coverage against `aaai项目.md`.
- Changes: Added `src/ciept/delivery/` with manifest export, results indexing, resource inventory generation, implementation review generation, and a delivery CLI. Also replaced the local `graph.adapters.to_tensor_views()` placeholder with a real tensor-view adapter.
- Verification: `python -m pytest tests/test_graph_adapters.py tests/test_delivery_bundle.py -v`; final full-suite verification pending before commit.
- Risks/Next: External datasets, VLMs, and baseline methods still need to be downloaded and integrated; those are now explicitly listed in the delivery bundle.

## 2026-03-10 12:49 UTC - T012

- Goal: Add a dispatcher-based experiment runner that standardizes result directories and per-experiment outputs.
- Changes: Added `src/ciept/experiments/` with shared result types, run-directory I/O, a central dispatcher, and toy modules for main results, robustness, faithfulness, ablation, usage, and efficiency experiments.
- Verification: `python -m pytest tests/test_experiment_runner.py -v`; `python -m pytest tests/test_experiment_modules.py tests/test_persistence.py::test_t012_marked_done_and_t013_selected_next -v`; `python -m pytest -v`; `bash scripts/check.sh`.
- Risks/Next: Continue from `T013` with final delivery artifacts and paper-facing exports built on the now-stable results protocol.

## 2026-03-10 12:38 UTC - T011

- Goal: Add a reusable metrics package that centralizes ranking, faithfulness, and usage-diagnosis formulas.
- Changes: Added `src/ciept/metrics/` with ranking metrics, faithfulness metrics, usage diagnostics, and lightweight dataclass wrappers for metric bundles.
- Verification: `python -m pytest tests/test_metrics_ranking.py tests/test_metrics_faithfulness.py -v`; `python -m pytest tests/test_metrics_usage.py tests/test_persistence.py::test_t011_marked_done_and_t012_selected_next -v`; `python -m pytest -v`; `bash scripts/check.sh`.
- Risks/Next: Continue from `T012` with experiment runners and result templates that consume the new metrics package.

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
