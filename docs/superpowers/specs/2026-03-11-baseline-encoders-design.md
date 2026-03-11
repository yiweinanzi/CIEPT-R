# Remaining Baselines And Local Encoder/OCR Integration Design

## Context

The repository already integrated the first baseline wave through `B003-B011`, but there are still locally downloaded baseline repositories that are not wired into the shared runner:

- `Guider` (`Teach Me How to Denoise`)
- `MAGNET`
- `SMORE`
- `DiffMM`
- `MixRec`

At the same time, the user now has local model weights for:

- `models/Qwen3-Embedding-4B`
- `models/Qwen3-VL-Embedding-2B`

and wants PaddleOCR integrated as well.

The current repository has no dedicated local-encoder/OCR package, and the remaining baseline candidates need to be classified into:

- integrable now
- blocked by incompatible runtime/data assumptions
- still blocked by missing assets (`RecGOAT`, `IGDMRec`, correct multimodal `CLEAR`)

## Goal

1. Extend the baseline layer to integrate all locally available, relevant remaining baselines that can be run through the current bootstrap environment.
2. Add a local encoder/OCR package that exposes lazy, path-based interfaces for Qwen text embeddings, Qwen multimodal embeddings, and PaddleOCR.

## Decomposition

This work naturally splits into two sub-projects:

### Sub-project A: Remaining baseline integrations

- `Guider` -> MMRec-family guided teacher/student runner
- `MAGNET` -> MMRec-family runner
- `SMORE` -> MMRec-family runner
- `DiffMM` -> standalone diffusion-family runner
- `MixRec` -> compatibility audit and truthful blocker handling

### Sub-project B: Local encoder and OCR integration

- Qwen text embedding adapter
- Qwen multimodal embedding adapter
- PaddleOCR adapter
- shared local-model registry/config

## Approaches Considered

### Approach 1: Keep adding per-repo ad-hoc scripts

- Pros: fast for one repo at a time
- Cons: scales poorly, duplicates runtime patching and result-writing logic

### Approach 2: Extend family-based adapters and add a separate local-model package

- Pros: fits the current baseline architecture, keeps encoder/OCR logic out of the research core
- Cons: needs a bit more upfront structure

### Approach 3: Only add metadata and leave real execution to notebooks

- Pros: minimal code
- Cons: does not satisfy the user’s “integrate” requirement

## Recommendation

Use **Approach 2**.

It preserves the good boundary already established in `src/ciept/baselines/`, and it keeps local model/OCR integration in an independent package so the core `ciept` research implementation remains decoupled from heavyweight runtime dependencies.

## Baseline Design

### 1. Extend the registry with post-`B011` baseline tasks

Add new baseline tasks for downloaded candidate repos that are now being promoted into executable integrations:

- `B012`: Guider / Teach Me How to Denoise
- `B013`: MAGNET
- `B014`: SMORE
- `B015`: DiffMM
- `B016`: MixRec compatibility audit

The original blocked/missing items remain truthful:

- `B008`: blocked because the local CLEAR repo is the wrong paper/codebase
- `RecGOAT`, `IGDMRec`: still missing locally

### 2. Reuse the MMRec-family runner where possible

`Guider`, `SMORE`, and `MAGNET` all follow the same broad pattern:

- numeric `.inter` file with `x_label`
- `image_feat.npy` / `text_feat.npy`
- `configs/overall.yaml` + dataset/model YAML
- `utils.quick_start` style training entry

They should reuse the current MMRec formatter, but each gets its own default smoke executor because:

- `Guider` has student/teacher model arguments
- `MAGNET` and `SMORE` need model-specific config overrides

### 3. Add a DiffMM family adapter

`DiffMM` expects:

- pickled train/test sparse matrices
- `image_feat.npy` / `text_feat.npy`
- standalone `Main.py`

Add a new formatter that converts presplit interactions into:

- `trnMat.pkl`
- `tstMat.pkl`
- deterministic placeholder modality features

and a standalone smoke executor with lightweight CPU-safe stubs for CUDA-only assumptions.

### 4. Treat MixRec as a runtime/data mismatch unless proven otherwise

`MixRec` depends on:

- TensorFlow 1.14
- multi-behavior datasets (`pv/cart/buy`, etc.)
- leave-one-out style evaluation

That is materially different from the current single-behavior presplit multimodal baseline path. The repository should:

- record this as `asset_mismatch` or `runtime_mismatch`
- avoid pretending it is runnable on the current dataset contract

## Encoder/OCR Design

### 1. Add a dedicated local-model package

Create `src/ciept/encoders/` with:

- `registry.py`: local path validation and model descriptors
- `text.py`: Qwen text embedding adapter
- `vision.py`: Qwen multimodal embedding adapter
- `ocr.py`: PaddleOCR adapter

### 2. Use lazy loading only

These adapters should validate local paths early but defer heavyweight imports/model construction until first use.

This matters because:

- `Qwen3-Embedding-4B` is large
- `Qwen3-VL-Embedding-2B` requires `transformers` and `qwen-vl-utils`
- PaddleOCR requires `paddlepaddle`

Lazy loading keeps test/runtime overhead under control.

### 3. Standardize outputs

The adapters should expose narrow methods:

- text encoder: `embed_texts(texts, instruction=None)`
- VL encoder: `embed_inputs(items, instruction=None)` where each item can contain text and/or image
- OCR engine: `extract_text(image_path)`

Return values should be plain Python/NumPy-friendly objects so downstream preprocessing can consume them without depending on the original backend types.

### 4. Configuration

Add a stable local config file, e.g.:

- `configs/models/local_backends.yaml`

with paths for:

- `qwen_text_embedding`
- `qwen_vl_embedding`
- `paddleocr`

## Testing Strategy

Tests should verify:

- the registry promotes new candidate baselines into the correct status buckets
- Guider/MAGNET/SMORE/DiffMM prepare the right dataset formats and write unified outputs
- MixRec is reported as a truthful incompatibility
- Qwen text/VL/OCR adapters validate paths and lazily construct backends

Tests should not require:

- loading the full 4B model into memory
- GPU availability
- downloading OCR models during pytest
