# Required Assets

## Datasets
- Amazon Reviews 2023: Clothing_Shoes_and_Jewelry, Sports_and_Outdoors, Beauty_and_Personal_Care
- Legacy Amazon baselines: Clothing, Sports, Beauty
- Cross-domain appendix datasets: KuaiRec, MicroLens, THACIL-style micro-video set

## Models
- Core runtime: PyTorch 2.10
- Future VLM choice for audit pre-annotation (provider-agnostic placeholder): GPT-4.1/4o, Qwen2.5-VL, Gemini, or an equivalent local VLM
- Baseline implementations/checkpoints as required for comparison

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

## Deferred External Assets
- Real benchmark datasets are not yet downloaded
- Real VLM integration is not yet connected
- External baseline methods are not yet integrated