# Required Assets

## Datasets
- Amazon Reviews 2023: Clothing_Shoes_and_Jewelry, Sports_and_Outdoors, Beauty_and_Personal_Care
- Legacy Amazon baselines: Clothing, Sports, Beauty
- Cross-domain appendix datasets: KuaiRec, MicroLens, THACIL-style micro-video set

## Models
- Core runtime: PyTorch 2.10
- Future VLM choice for audit pre-annotation (provider-agnostic placeholder): GPT-4.1/4o, Qwen2.5-VL, Gemini, or an equivalent local VLM
- Baseline implementations/checkpoints as required for comparison
- Local text embedding backend: `models/Qwen3-Embedding-4B`
- Local multimodal embedding backend: `models/Qwen3-VL-Embedding-2B`
- Local generative VLM backend: `models/Qwen3.5-9B`
- Local OCR runtime: `paddleocr` + `paddlepaddle`

## Baselines
- LightGCN
- VBPR
- BM3
- MGCN
- Teach Me How to Denoise
- I3-MRec
- CLEAR
- Training-free Graph-based Imputation
- RecGOAT
- IGDMRec
- Modality-Guided Mixture of Graph Experts

## Baseline Tracking Status
- `LightGCN`: integrated through the RecBole auxiliary runner.
- `VBPR`: integrated through the upstream Python package source with presplit numeric formatting.
- `BM3`: integrated through the MMRec-style adapter family.
- `MGCN`: integrated through the MMRec-style adapter family.
- `I3-MRec`: integrated through a standalone entrypoint adapter.
- `Training-free Graph-based Imputation`: integrated through the indexed imputation adapter family.
- `Guider`: confirmed mapping to `Teach Me How to Denoise`; no longer treated as missing.
- `MAGNET`: confirmed mapping, but the downloaded archive is incomplete and cannot be executed yet.
- `DiffMM`: integrated through the standalone diffusion-family adapter.
- `MixRec`: blocked; the downloaded archive depends on TF1.14, multi-behavior data, and leave-one-out evaluation, which do not match the current runner contract.
- `SMORE`: integrated through the MMRec-style adapter family.
- `CLEAR`: blocked; the downloaded `CLEAR-replication-main.zip` is an API recommendation repository, not the required multimodal recommendation baseline.
- `RecGOAT`: still missing locally, but there is an official code lead at `github.com/6lyc/RecGOAT-LLM4Rec`; this is now the next acquisition focus.
- `IGDMRec`: still missing; official implementation or faithful reproduction still needs to be acquired.

## Deferred External Assets
- Real benchmark datasets are not yet downloaded
- Real VLM integration is not yet connected
- Correct multimodal CLEAR implementation is not yet downloaded
- RecGOAT and IGDMRec are not yet downloaded
- A complete MAGNET implementation archive is not yet available locally
