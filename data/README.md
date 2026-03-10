# Data Layout

This repository uses a three-stage data layout:

- `data/raw/`: immutable source downloads
- `data/interim/`: temporary artifacts created during preprocessing
- `data/processed/`: reproducible train/valid/test outputs and protocol summaries

## Protocol Rules

- Temporal splitting is performed offline with a global absolute-time `80/10/10` split.
- RecBole or downstream training code should only read the processed split files.
- Iterative k-core filtering is applied before the split.
- Items with missing modalities are retained and represented via explicit modality flags and a missing-modality report.
- Main results use the transductive setting; cold-start should be reported separately.
