# Progress Log

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
