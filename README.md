# CIEPT-R

## 项目简介 | Overview

**中文**

CIEPT-R 是一个面向多模态推荐研究的工程化仓库，围绕 `aaai项目.md` 中描述的 CIEPT-R 方法逐步实现数据协议、图结构、先验、传输重排、干预审计、实验 runner、baseline 对齐和本地模型后端。

当前仓库的目标不是“已经完成整篇论文复现”，而是提供一个可持续推进的研究工程底座：

- 固定数据协议和时间切分约束
- 把核心研究模块拆成可测试的边界
- 为 baseline、VLM、OCR、本地编码器预留统一接入面
- 用持续验证保证每一步修改都可回归

**English**

CIEPT-R is an engineering-first research repository for multimodal recommendation. It incrementally implements the CIEPT-R method described in `aaai项目.md`, including the data contract, graph structures, priors, transport-based reranking, intervention/audit tooling, experiment runners, baseline alignment, and local model backends.

This repository is not presented as a finished paper reproduction. It is a maintainable research codebase designed to:

- enforce a stable data protocol and temporal split policy,
- decompose the method into testable modules,
- provide unified integration surfaces for baselines, VLMs, OCR, and local encoders,
- and keep every step regression-tested.

## 当前能力 | Current Capabilities

**中文**

当前仓库已经具备：

- 离线 `raw / interim / processed` 数据协议与全局时间切分
- evidence graph、块对角拓扑、reliability/capacity/nuisance 先验
- toy partial transport、torch reranker、干预与 leakage 诊断
- ranking / faithfulness / usage diagnosis 指标
- dispatcher-based 实验 runner 与交付物导出
- 多条 baseline family runner 与 smoke 执行路径
- 本地 `Qwen3-Embedding-4B`、`Qwen3-VL-Embedding-2B`、`Qwen3.5-9B`、`PaddleOCR` 的 lazy adapters

**English**

The repository currently provides:

- an offline `raw / interim / processed` data protocol with global temporal splitting,
- evidence-graph, block-diagonal topology, and reliability/capacity/nuisance priors,
- toy partial transport, a torch reranker, intervention logic, and leakage diagnostics,
- ranking / faithfulness / usage-diagnosis metrics,
- a dispatcher-based experiment runner and delivery/export tooling,
- multiple baseline-family runners with smoke execution paths,
- and lazy adapters for local `Qwen3-Embedding-4B`, `Qwen3-VL-Embedding-2B`, `Qwen3.5-9B`, and `PaddleOCR`.

## 当前边界 | Current Boundaries

**中文**

当前仓库仍然有意保留以下边界：

- 真实 Amazon Reviews 2023 全量预处理尚未完成
- 大规模 benchmark 结果与多 seed 统计尚未完成
- 部分 baseline 仍缺官方资产或本地资产不完整
- 本地大模型后端已接入，但默认保持 lazy-load，不在测试阶段强制加载 4B/9B 权重

**English**

The repository still intentionally stops short of:

- full-scale Amazon Reviews 2023 preprocessing,
- benchmark-grade results and multi-seed statistics,
- complete coverage for every baseline when the upstream asset is missing or incomplete,
- eager loading of large local backends during tests or CI-like verification.

## 仓库结构 | Repository Layout

```text
aaai项目.md                         Research framing / 研究设定
configs/                           Project and local-backend configs / 配置
continue/                          Persistent task state and progress / 持久化任务状态
data/                              Raw, interim, processed data layout / 数据目录
deliverables/current/              Delivery review and required assets / 交付物审查
docs/superpowers/                  Design and implementation plans / 设计与计划文档
scripts/                           Verification scripts / 验证脚本
src/ciept/                         Main Python package / 主 Python 包
tests/                             Regression tests / 回归测试
```

## 核心模块 | Core Modules

### 数据协议 | Data Protocol

**中文**

`src/ciept/data/` 负责：

- iterative k-core
- 全局绝对时间 `80/10/10` 切分
- missing modality 保留策略
- stress / lure / nuisance 协议

**English**

`src/ciept/data/` handles:

- iterative k-core filtering,
- global absolute-time `80/10/10` splits,
- missing-modality retention,
- and stress / lure / nuisance protocols.

### 图与先验 | Graph And Priors

**中文**

`src/ciept/graph/` 与 `src/ciept/priors/` 提供：

- text / vision evidence nodes
- 严格块对角 topology
- corroboration / stability / vulnerability heuristics
- capacity prior 与 nuisance mask

**English**

`src/ciept/graph/` and `src/ciept/priors/` provide:

- text / vision evidence nodes,
- strict block-diagonal topology,
- corroboration / stability / vulnerability heuristics,
- capacity priors and nuisance masks.

### 传输与训练骨架 | Transport And Training Skeleton

**中文**

`src/ciept/transport/` 与 `src/ciept/train/` 提供：

- toy partial transport sanity checks
- torch reranker skeleton
- confidence-weighted ListMLE training stub

**English**

`src/ciept/transport/` and `src/ciept/train/` provide:

- toy partial-transport sanity checks,
- a torch reranker skeleton,
- and a confidence-weighted ListMLE training stub.

### 审计与指标 | Audit And Metrics

**中文**

`src/ciept/audit/` 与 `src/ciept/metrics/` 提供：

- support normalization
- intervention / leakage analysis
- ranking, faithfulness, and usage-diagnosis metrics

**English**

`src/ciept/audit/` and `src/ciept/metrics/` provide:

- support normalization,
- intervention / leakage analysis,
- and ranking / faithfulness / usage-diagnosis metrics.

### Baselines

**中文**

`src/ciept/baselines/` 现在已经支持多种 family-based integration：

- RecBole family: `LightGCN`
- Python package family: `VBPR`
- MMRec-style family: `BM3`, `MGCN`, `Guider`, `SMORE`
- Standalone family: `I3-MRec`, `DiffMM`
- Indexed imputation family: `Training-free Graph-based Imputation`

以下 baseline 当前仍被如实标记为 blocker：

- `CLEAR`: 本地仓库与目标论文不匹配
- `MAGNET`: 本地 archive 缺少模型实现
- `MixRec`: 当前 runner 契约不兼容
- `RecGOAT`, `IGDMRec`: 本地仍缺资产

**English**

`src/ciept/baselines/` now supports multiple family-based integrations:

- RecBole family: `LightGCN`
- Python-package family: `VBPR`
- MMRec-style family: `BM3`, `MGCN`, `Guider`, `SMORE`
- Standalone family: `I3-MRec`, `DiffMM`
- Indexed-imputation family: `Training-free Graph-based Imputation`

The following baselines remain truthfully blocked:

- `CLEAR`: the local repository does not match the required paper,
- `MAGNET`: the local archive is missing model implementation files,
- `MixRec`: incompatible with the current runner contract,
- `RecGOAT`, `IGDMRec`: assets still missing locally.

### 本地模型与 OCR | Local Models And OCR

**中文**

`src/ciept/encoders/` 提供 lazy-load adapters：

- `LocalQwenTextEmbedder`
- `LocalQwenVLEmbedder`
- `LocalQwenVLM`
- `LocalPaddleOCREngine`

配置见 `configs/models/local_backends.yaml`。

**English**

`src/ciept/encoders/` provides lazy-load adapters for:

- `LocalQwenTextEmbedder`
- `LocalQwenVLEmbedder`
- `LocalQwenVLM`
- `LocalPaddleOCREngine`

Configuration lives in `configs/models/local_backends.yaml`.

## 快速开始 | Quick Start

### 1. 安装基础依赖 | Install Base Dependencies

```bash
python -m pip install -e .[dev]
```

### 2. 可选：安装 baseline 依赖 | Optional: Baseline Dependencies

```bash
python -m pip install -e .[baseline]
```

### 3. 可选：安装本地模型/OCR 依赖 | Optional: Local Model / OCR Dependencies

```bash
python -m pip install -e .[local_models]
```

### 4. 运行验证 | Run Verification

```bash
python -m pytest -v
bash scripts/check.sh
```

## 常用入口 | Common Entrypoints

### 数据预处理 | Data Preparation

```bash
PYTHONPATH=src python -m ciept.data.cli \
  --interactions data/raw/<dataset>/interactions.csv \
  --items data/raw/<dataset>/items.csv \
  --output-dir data/processed/<dataset> \
  --min-user-degree 5 \
  --min-item-degree 5
```

### Toy Train / Eval

```bash
PYTHONPATH=src python -m ciept.train.cli --mode train
PYTHONPATH=src python -m ciept.train.cli --mode eval
```

## 文档入口 | Documentation

**中文**

- 研究设定：`aaai项目.md`
- 持久化任务状态：`continue/task.json`
- 进度日志：`continue/progress.md`
- 交付物审查：`deliverables/current/implementation_review.md`
- 资源缺口：`deliverables/current/required_assets.md`
- 设计与计划：`docs/superpowers/specs/`, `docs/superpowers/plans/`

**English**

- Research framing: `aaai项目.md`
- Persistent task state: `continue/task.json`
- Progress log: `continue/progress.md`
- Delivery review: `deliverables/current/implementation_review.md`
- Resource gaps: `deliverables/current/required_assets.md`
- Design and plans: `docs/superpowers/specs/`, `docs/superpowers/plans/`

## 说明 | Notes

**中文**

这个仓库刻意把“研究核心实现”和“baseline / 本地模型 / OCR 辅助层”分开。RecBole、PaddleOCR、Qwen 本地权重都不应反向污染 `src/ciept` 的核心研究模块边界。

**English**

This repository intentionally separates the core research implementation from the auxiliary baseline / local-model / OCR layers. RecBole, PaddleOCR, and local Qwen weights should not leak back into the core `src/ciept` research boundaries.
