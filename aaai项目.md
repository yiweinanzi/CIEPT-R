# 创新点1：Only Match What Matters: Capacity-Calibrated Partial Intent-Evidence Transport for Audited Multimodal Recommendation

## 项目概览

**项目名称**：面向模态冲突鲁棒与审计式反事实忠实的容量校准意图-证据局部传输推荐系统（CIEPT-R）

**目标顶会**：AAAI 2027（首选） / SIGIR 2027（次选）

**时间说明**：截至 **2026 年 3 月 10 日**，尚未看到 AAAI-27 官方 CFP 的公开版本；当前项目计划按 AAAI 常规时间节奏倒排，最终提交窗口以官方通知为准。

**预计周期**：6 到 8 个月。前 6 周只验证三件事：`capacity-calibrated partial reject option` 是否稳定成立、`normalized support + leakage ratio` 是否能闭环评估、`global 80/10/10 time split + usage diagnosis` 是否能在主 benchmark 上跑通。若三者任一失败，立即收缩题目。

**核心创新**：

1. **容量校准的最小充分证据选择（Capacity-Calibrated Minimal Sufficient Evidence Selection）**：通过显式 transported mass budget \(m_{ui}\) 和节点容量 prior \(q(\mathbf r)\) 控制实际运输质量，只让与当前用户意图匹配的最小充分证据进入决策路径，从而赋予 unmatched mass 清晰的 reject semantics。
2. **块对角拓扑下的结构化局部传输（Block-Diagonal Topology with Partial Intent-Evidence Transport）**：商品侧仅在文本流形和视觉流形内部定义拓扑，跨模态一致性完全交由特征代价矩阵建模，避免跨模态伪几何。Gromov 项只作为结构正则，而不是喧宾夺主的 solver headline。
3. **审计式干预与内容使用诊断（Audited Intervention and Content Usage Diagnosis）**：通过 capacity-normalized support、Leakage Ratio、Sufficiency/Comprehensiveness、Image Shuffle Drop 和人工/VLM 审计集，验证模型是否真正使用了多模态内容，以及是否把决策质量泄漏到了 nuisance 证据上。

**核心立场**：  
这篇论文的主问题不是“我们实现了一个更复杂的 OT 求解器”，而是：  
**在多模态冲突下，推荐模型能否只依赖最小且足以支撑排序的证据，并显式拒绝多余或误导性证据。**

------

## 次世代多模态推荐 (Next-Gen MMRec) 符合性检查

## 顶会定义的 Next-Gen MMRec 三大特征

#### **特征1：Fine-grained Modality Decoupling（细粒度解耦与匹配）**

**要求**：从整图/整句整体融合，转向证据级、属性级、区域级的结构化建模。

**我们的符合情况**：

- 商品侧不再用单一 `whole-item embedding` 表示，而是拆成文本节点和视觉节点。
- 文本拓扑仅在文本子空间内定义：相邻短语距离、属性键值依赖、可选句法距离。
- 视觉拓扑仅在视觉子空间内定义：patch / region 的二维坐标距离与局部邻接。
- 商品图结构代价矩阵 \(C^i\) 被严格定义为块对角矩阵，跨模态块不承载几何意义。
- 跨模态对应关系只通过特征代价矩阵 \(C_{\text{feat}}\) 建模，不再人为构造文本 token 与视觉 patch 的伪几何边。
- 用户侧通过历史 evidence graph 编码后抽取少量可学习 intent anchors，形成用户意图图。

#### **特征2：Robustness to Modality Conflict（对噪声与冲突的鲁棒性）**

**要求**：面对图文不符、背景干扰、营销诱饵、缺失模态时，模型仍保持稳定排序。

**我们的符合情况**：

- 传统平衡对齐会强制所有节点吸收质量，使 nuisance 证据被动进入匹配。
- 本方案显式控制 transported mass budget \(m_{ui}\)，并通过容量 prior \(q(\mathbf r)\) 限定每个证据节点最多能承载的质量。
- reliability 同时以两种形式进入优化：
  - 作为 target-side capacity prior；
  - 作为 feature cost penalty，抬高低可靠节点的匹配成本。
- `positive-preserving nuisance` 与 `negative-preserving lure` 在训练和验证中显式出现，使 reject semantics 可被直接验证。
- 所有主结果在 `clean / high-conflict / missing-modality / long-tail / usage diagnosis` 五种条件下分别报告。

#### **特征3：Counterfactual Faithfulness（反事实忠实度）**

**要求**：重要证据必须在干预下维持充分性、必要性与 nuisance 不变性，而非只给出热力图解释。

**我们的符合情况**：

- 解释对象从 attention map 转为 transport support：\(s_j = \sum_k T_{kj}\)。
- support 不是直接当概率使用，而是先做 capacity normalization：
\[
\tilde s_j = \frac{\sum_k T_{kj}}{q_j(\mathbf r) + \epsilon}
\]
再将 \(\tilde s_j\) 裁剪到 \((\epsilon, 1-\epsilon)\) 后映射到 logit 空间。
- Leakage 不再使用绝对量，而采用 ratio 形式：
\[
\mathrm{LR} = \frac{\sum_j \tilde s_j \nu_j}{\sum_j \tilde s_j + \epsilon}
\]
其中 \(\nu_j\) 为 nuisance mask。
- 在外部审计集上报告 `SupportPrecision / SupportRecall / SupportF1`，避免模型对自身解释自证合理。

## AAAI 2027 命中率评估

| 评估维度 | 上一版风险 | 当前修订方案 | 预期评审反馈 |
| --- | --- | --- | --- |
| 论文主线 | 过度 solver-centric，像 OT paper 套 rec 壳 | 主线回到 `minimal evidence + reject semantics` | 问题更像 AAAI paper |
| 方法定义 | objective、伪代码、指标不完全对齐 | \(p, q(\mathbf r), m_{ui}\)、normalized support、LR 全部显式对齐 | 数学与实现一致 |
| Gromov 叙事 | Gromov 项过于喧宾夺主 | Gromov 仅是结构正则，不再是 headline | 技术更克制 |
| 评估协议 | MLR 可被总质量收缩 exploit | 改为 Leakage Ratio + normalized support | 指标更可信 |
| 时间切分 | 文本描述与 RecBole 配置不一致 | 全局 80/10/10 在预处理离线完成 | protocol 干净 |
| Benchmark | Amazon 与短视频并列主战场，范围过大 | Amazon Reviews 2023 主表，短视频仅 appendix 跨域 | 主文更收敛 |

**总体判断**：  
当前版本的主要任务不是再强化 solver，而是把 `reject semantics + audited minimal evidence` 立住。  
只要目标函数、伪代码、指标和时间切分真正统一，这篇 paper 才会从 borderline reject 进入可投区间。

------

## RecBole + Capacity-Calibrated Partial Transport 集成方案

## 框架核心价值分析

本项目的 novelty 必须来自 **显式 reject semantics** 和 **可审计最小证据选择**，而不是来自 OT 求解器复杂度本身。

- `RecBole` 负责：
  - 预处理后的 full-sort 评估
  - 基线对齐与日志记录
  - 召回候选与 rerank 框架
- `Capacity-Calibrated Partial Transport Layer` 负责：
  - partial mass budget \(m_{ui}\)
  - target capacity prior \(q(\mathbf r)\)
  - 结构化 intent-evidence matching
  - support-based intervention learning

**关键原则**：

- 主文的问题定义使用 `partial / hybrid partial` 语义，不再把完整 non-balanced solver 作为 headline。
- 若工程上需要 relaxed solver，可作为实现细节或 appendix variant。
- 不在主训练环路中调用 `POT`；`POT` 只允许用于 toy numeric sanity check。

## 我们可以复用的组件

#### **组件1：预处理阶段完成的全局时间切分**

**关键修正**：  
主结果不再依赖 RecBole 内部 `LS` 配置做 temporal split。  
全局 `80/10/10` 时间切分必须在预处理脚本里离线完成，直接生成 `train / valid / test` 文件，RecBole 只负责读取。

```python
def global_temporal_split(interactions):
    interactions = interactions.sort_values("timestamp")
    n = len(interactions)
    train = interactions.iloc[: int(0.8 * n)]
    valid = interactions.iloc[int(0.8 * n): int(0.9 * n)]
    test = interactions.iloc[int(0.9 * n):]
    return train, valid, test
```

**RecBole 配置只保留评估设置**：

```python
config_dict = {
    "eval_args": {
        "order": "TO",
        "mode": "full"
    },
    "repeatable": True,
    "metrics": ["Recall", "NDCG", "MRR"],
    "topk": [10, 20]
}
```

#### **组件2：容量校准的局部传输层**

```python
import torch
import torch.nn as nn

class CapacityCalibratedPartialTransport(nn.Module):
    def __init__(self, eps=0.05, alpha=0.5, outer_iters=3):
        super().__init__()
        self.eps = eps
        self.alpha = alpha
        self.outer_iters = outer_iters

    def forward(self, C_feat, C_u_topo, C_i_topo, p, q_cap, mass_budget, mask_u, mask_i):
        T = init_partial_plan(p, q_cap, mass_budget, mask_u, mask_i)

        for t in range(self.outer_iters):
            grad_gw = gw_gradient(C_u_topo, C_i_topo, T, mask_u, mask_i)
            linear_cost = (1.0 - self.alpha) * C_feat + self.alpha * grad_gw

            T_tilde = entropic_partial_projection(
                linear_cost=linear_cost,
                p=p,
                q=q_cap,
                mass_budget=mass_budget,
                mask_u=mask_u,
                mask_i=mask_i,
                eps=self.eps,
            )

            gamma = 2.0 / (t + 2.0)
            T = (1.0 - gamma) * T + gamma * T_tilde

        return T
```

**实施要求**：

- 若使用 `Frank-Wolfe` 一词，必须保留显式 direction/update，而不是“重算 cost 然后直接覆盖 T”的伪 FW。
- 若完整 partial projection 工程成本过高，可在实现中使用 hybrid relaxed projection，但主文中的问题定义仍然以 partial mass 为核心。
- `p` 和 `q_cap` 必须作为输入进入求解，不能只写在公式里不进代码。

#### **组件3：严格块对角拓扑缓存器**

```python
def build_topological_graph_cache(item):
    text_nodes, text_dist = parse_text_1d_distance(item.title, item.meta, item.ocr)
    vision_nodes, vision_dist = parse_visual_2d_distance(item.image)

    n_t, n_v = len(text_nodes), len(vision_nodes)
    C_item_topo = torch.zeros((n_t + n_v, n_t + n_v))

    C_item_topo[:n_t, :n_t] = normalize_cost(text_dist)
    C_item_topo[n_t:, n_t:] = normalize_cost(vision_dist)
    C_item_topo[:n_t, n_t:] = 1e4
    C_item_topo[n_t:, :n_t] = 1e4

    nodes = encode_nodes(text_nodes + vision_nodes)
    reliability = compute_reliability_prior(nodes)
    return {
        "nodes": nodes,
        "C_item_topo": C_item_topo,
        "reliability": reliability,
    }
```

**实施要求**：

- 文本与视觉拓扑分别定义、分别归一化。
- 跨模态块不学习几何边。
- 跨模态一致性仅在 \(C_{\text{feat}}\) 中建模。

#### **组件4：正规化支持集与单次干预层**

```python
def normalized_support(T, q_cap, eps=1e-6):
    raw_support = T.sum(dim=1)
    norm_support = raw_support / (q_cap + eps)
    return norm_support.clamp(eps, 1.0 - eps)

def leakage_ratio(norm_support, nuisance_mask, eps=1e-6):
    return (norm_support * nuisance_mask).sum(dim=1) / (norm_support.sum(dim=1) + eps)

def single_pass_intervention(score_full, T, q_cap, item_nodes, user_repr, nuisance_mask, global_step):
    norm_support = normalized_support(T, q_cap)
    logits = torch.log(norm_support) - torch.log(1.0 - norm_support)

    tau = max(0.2, 1.0 * (0.999 ** global_step))
    gate = binary_gumbel_ste(logits, tau=tau)

    score_sel = lightweight_scorer(user_repr, item_nodes * gate.unsqueeze(-1))
    score_del = lightweight_scorer(user_repr, item_nodes * (1.0 - gate).unsqueeze(-1))

    L_suff = (score_full.detach() - score_sel).abs().mean()
    L_comp = torch.relu(0.1 - (score_full.detach() - score_del)).mean()
    L_leak = leakage_ratio(norm_support, nuisance_mask).mean()
    return L_suff + 0.5 * L_comp + 0.5 * L_leak
```

**实施要求**：

- 先 capacity-normalize，再进入 logit。
- Leakage 必须使用 ratio，不再使用绝对质量总和。
- 温度退火用于训练稳定，不作为核心 scientific claim。

------

## 基于现有论文的技术路线

## 核心基础论文（必须在引言和 Related Work 中对标）

#### 1. **结构化传输与推荐（OT for Recommendation）**

- 对标方向：`RecGOAT`、`Fused Partial Gromov-Wasserstein for Structured Objects`
- 我们的站位：
  - 现有工作已经证明 OT 可用于 MMRec。
  - 我们要解决的不是“写一个更重的 solver”，而是“如何让 transport 自带 reject semantics，并能审计最小充分证据”。
  - partial mass 的显式可解释性优先于 solver 炫技。

#### 2. **去噪、去冗余与不变学习（Denoising / Invariance / De-redundancy）**

- 对标方向：`Teach Me How to Denoise`、`I3-MRec`、`CLEAR`
- 我们的站位：
  - 这些工作主要在表示层做稳健性增强。
  - 本工作进一步关注“哪些节点应被拒绝，以及被拒绝的语义是否可审计”。

#### 3. **可信推荐与反事实解释（Trustworthy Recommendation and Counterfactual Explanation）**

- 对标方向：`Towards Trustworthy Multimodal Recommendation`、`Comparative Explanations via Counterfactual Reasoning in Recommendations`
- 我们的站位：
  - 解释必须进入可审计干预协议，而不是止于热力图。
  - `SupportF1`、`Leakage Ratio`、`Image Shuffle Drop` 是比漂亮案例更强的证据。

#### 4. **多模态内容使用诊断（Content Usage Diagnosis）**

- 对标方向：`Do Recommender Systems Really Leverage Multimodal Content?`
- 我们的站位：
  - 论文必须回答模型是否真的使用图像、文本和 OCR。
  - usage diagnosis 是主文实验的一部分，不再是附属检查。

------

## 技术实施详细方案

## 阶段1：最小充分证据图与容量先验（Week 1-3）

**修订目标**：构建真实拓扑图、可靠性先验和可解释容量 prior，为局部传输提供问题定义基础。

**实现原则**：

- 用户侧 intent 由历史 graph encoder + cross-attention 抽取，控制在 `K <= 6`。
- 商品侧 evidence nodes 控制在 `M <= 16`。
- reliability 由三部分组成：
  - `corroboration`
  - `stability`
  - `vulnerability`
- 基础容量 prior 定义为：
\[
q_j(\mathbf r) = \frac{r_j a_j}{\sum_l r_l a_l + \epsilon}
\]
其中 \(a_j\) 为基础容量，默认可取均匀或信息密度加权。

```python
def build_evidence_graph(item):
    text_nodes, text_topo = parse_text_graph(item.title, item.meta, item.ocr)
    vision_nodes, vision_topo = parse_visual_graph(item.image)
    nodes = encode_nodes(text_nodes + vision_nodes)

    reliability = reliability_head(
        corroboration=cross_modal_corroboration(nodes),
        stability=augmentation_stability(nodes),
        vulnerability=corruption_vulnerability(nodes),
    )
    q_cap = capacity_prior(reliability)
    C_item_topo = build_block_diagonal_topology(text_topo, vision_topo)
    return nodes, C_item_topo, reliability, q_cap
```

**阶段产物**：

- `evidence_graph.pt`
- `item_topology_cost.pt`
- `reliability_prior.pt`
- `capacity_prior.pt`
- `nuisance_mask.pt`
- `intent_anchor_cache.pt`

**退出条件**：

- reliability 对 injected nuisance nodes 的 AUROC 明显高于随机。
- 容量 prior 在 clean nodes 与 nuisance nodes 之间存在稳定分离。

## 阶段2：容量校准的局部传输算子 (Week 4-6)

**修订目标**：回到 `partial / hybrid partial` 主问题，solver 只作为支撑实现。

**核心设计点**：

- 引入显式 transported mass budget：
\[
m_{ui} = m_{\min} + (m_{\max} - m_{\min}) \sigma(g(h_u, h_i, \gamma_i, \mu_i))
\]
- 通过 \(m_{ui}\) 定义 reject semantics：未被运输的质量即被拒绝证据。
- 通过 \(q(\mathbf r)\) 与 feature cost penalty 控制每个证据节点最多承载多少质量。
- Gromov 项仅作为结构正则项，不再成为论文 headline。

```python
class PartialTransportReranker(nn.Module):
    def __init__(self, eps=0.05):
        super().__init__()
        self.transport = CapacityCalibratedPartialTransport(eps=eps)

    def forward(self, user_graph, item_graph, C_u_topo, C_i_topo, p, q_cap, mass_budget, mask_u, mask_i):
        C_feat = compute_feature_cost(user_graph.nodes, item_graph.nodes)
        C_feat = C_feat + reliability_penalty(q_cap)
        T = self.transport(C_feat, C_u_topo, C_i_topo, p, q_cap, mass_budget, mask_u, mask_i)
        score = score_from_transport(T, C_feat)
        return score, T
```

**退出条件**：

- `BatchSize >= 256` 下稳定反传。
- 无大规模 NaN / Inf。
- 主结果中的 reject semantics 不依赖额外 utilization regularizer 才成立。

## 阶段3：正规化支持集干预 (Week 7-9)

**修订目标**：用 normalized support 做单次干预，并让干预指标与容量 prior 语义一致。

**执行原则**：

- 训练阶段使用 capacity-normalized support 的 Gumbel 掩码近似 `selected-only` / `selected-removed`。
- 验证和测试阶段可额外执行精确反事实评估。
- `Leakage Ratio` 直接约束 nuisance 节点吸收的相对质量，而不是绝对质量。

```python
def intervention_loss(score_full, T, q_cap, item_nodes, user_repr, nuisance_mask, step):
    return single_pass_intervention(
        score_full=score_full,
        T=T,
        q_cap=q_cap,
        item_nodes=item_nodes,
        user_repr=user_repr,
        nuisance_mask=nuisance_mask,
        global_step=step,
    )
```

**退出条件**：

- `Leakage Ratio` 在 lure negative 上显著下降。
- `SupportF1` 明显优于随机和简单 attention baseline。

## 阶段4：主排序目标与附属实验降级 (Week 10-11)

**修订策略**：

- 主训练目标保持 `confidence-weighted ListMLE`。
- `S-DPO` 明确降级为 appendix-only sanity check。
- 若 solver variant 太多，只保留一个主文版本，其他全部放 appendix。

```python
def confidence_weighted_listmle(pos_score, neg_scores, weight, tau=0.2):
    logits = torch.cat([pos_score.unsqueeze(1), neg_scores], dim=1) / tau
    log_prob = logits[:, 0] - torch.logsumexp(logits, dim=1)
    return -(weight * log_prob).mean()
```

------

## 数据集配置方案

## 1. 核心评估数据集（严格时间划分）

**Legacy 对齐基准**：

- Amazon Clothing
- Amazon Sports
- Amazon Beauty

**定位**：

- 仅用于和历史 MMRec 文献保持可比性。
- 放次表或 appendix，不作为主文 headline。

**Modern 主基准**：

- Amazon Reviews 2023：
  - `Clothing_Shoes_and_Jewelry`
  - `Sports_and_Outdoors`
  - `Beauty_and_Personal_Care`
  - 资源允许时补 `Baby_Products`

**主文只保留这一条主战场**：

- high-conflict subset
- missing-modality subset
- long-tail subset
- usage diagnosis subset

这些子集全部从 Amazon Reviews 2023 主基准内部切出，保证任务形态一致。

**跨域泛化（appendix-only）**：

- `KuaiRec` 或 `MicroVideo-1.4M` 仅作为 appendix 跨域验证。
- 不与 Amazon 共同构成主文双 benchmark，避免问题形态发散。

**过滤与切分规则**：

- 全部采用预处理阶段完成的全局绝对时间切分。
- iterative `5-core` 过滤。
- 保留缺失模态 item，并显式记录 `missing modality mask`。
- 主结果使用 transductive 设定，cold-start 单独汇报。

## 2. Modality Conflict Stress Test（模态冲突压力测试）

**Positive-preserving nuisance**：

- 背景替换但保留主体
- 注入类别通用营销词
- 添加 OCR 噪声片段
- 替换非关键局部视觉块

**Negative-preserving lure**：

- 给负样本拼接用户历史高频风格词
- 给负样本加入高点击但非决策性的背景元素
- 注入相似但不决定购买的颜色、材质或视觉风格

**协议要求**：

- 精确记录 `nuisance_mask.pt`
- 扰动强度覆盖 `10% / 30% / 50%`
- 每个类目每个强度抽样人工复核，确认标签保持

## 3. VLM-in-the-loop 审计集

**推荐规模**：

- VLM 预标注样本：`10,000`
- 人工双盲仲裁子集：`500`

**最低可接受规模**：

- 若资源受限，VLM 预标注至少 `2,000`
- 人工仲裁子集至少 `300`

**执行要求**：

- VLM 只给出最小充分证据候选，不直接充当最终 gold label。
- 报告 `Cohen's kappa`。
- 覆盖不同冲突强度、类目和模态缺失情况。

------

## 评估指标详细配置

## 1. 排序主干 (Ranking Metrics)

```python
ranking_metrics = ["Recall@10", "Recall@20", "NDCG@10", "NDCG@20", "MRR@20"]
```

**统计要求**：

- 报告 5 个随机种子的均值和标准差。
- 使用 paired permutation test 或 paired bootstrap。
- 主表至少对 `NDCG@20` 给出显著性说明。

## 2. 结构忠实度与作弊诊断 (Faithfulness & Diagnosis)

```python
def compute_metrics(score_full, score_sel, score_del, T, q_cap, nuisance_mask, support_gold=None, eps=1e-6):
    norm_support = (T.sum(dim=1) / (q_cap + eps)).clamp(eps, 1.0 - eps)
    leakage = (norm_support * nuisance_mask).sum(dim=1) / (norm_support.sum(dim=1) + eps)

    metrics = {
        "SufficiencyGap": score_full - score_sel,
        "ComprehensivenessGap": score_full - score_del,
        "LeakageRatio": leakage.mean(),
    }
    if support_gold is not None:
        metrics["SupportPrecision"] = precision(norm_support, support_gold)
        metrics["SupportRecall"] = recall(norm_support, support_gold)
        metrics["SupportF1"] = f1(norm_support, support_gold)
    return metrics
```

**补充指标**：

- `Corruption Robustness AUC`
- `High-Conflict Retention`
- `Image Shuffle Drop Rate`
- `Random Caption Drop Rate`
- `Missing-Modality Drop`
- `Transported Mass Ratio`

**解释**：

- `LeakageRatio` 是核心 reject 指标，不再使用可被 exploit 的绝对 leakage。
- `Transported Mass Ratio` 用于检查模型是否把总质量压得过低。
- `Image Shuffle Drop Rate` 必须显著非零，否则说明模型并未真正使用视觉内容。

------

## 实验设计详细方案

## 实验 1：主结果表 (Main Results)

对比方法分三类：

- 经典基线：
  - LightGCN
  - VBPR
  - BM3
  - MGCN

- 稳健 / 去噪 / 缺失模态基线：
  - Teach Me How to Denoise
  - I$^3$-MRec
  - CLEAR
  - Training-free Graph-based Imputation

- 结构化 / 传输基线：
  - RecGOAT
  - IGDMRec
  - Modality-Guided Mixture of Graph Experts

**主结果要求**：

- 主表仅围绕 Amazon Reviews 2023。
- 主表至少单列：
  - `Clean`
  - `High-Conflict`
  - `Missing-Modality`
  - `Long-Tail`
- 跨域短视频结果放 appendix。

## 实验 2：对抗干预鲁棒曲线 (Robustness Curve)

- X 轴：nuisance / lure 注入强度
- Y 轴：`NDCG@20 retention`
- 报告均值和标准差阴影

## 实验 3：可审计忠实度对比 (Audited Faithfulness)

对比解释方法：

- attention map
- saliency / gradient
- transport support

报告：

- `SupportPrecision`
- `SupportRecall`
- `SupportF1`
- `LeakageRatio`
- `SufficiencyGap`
- `ComprehensivenessGap`

## 实验 4：机制消融 (Mechanism Ablation)

必须包含：

- `w/o partial mass budget`
- `w/o capacity prior q(r)`
- `w/o block-diagonal topology`
- `w/o structure term`
- `w/o normalized support`
- `w/o intervention loss`
- `ListMLE -> BPR`
- `ListMLE -> S-DPO`

**关键问题**：

- explicit transported mass 是否真的提供 reject semantics？
- capacity prior 是否比单纯的 cost penalty 更有效？
- Gromov 项是否真的因真实拓扑而有增益，而不是只是增加复杂度？

## 实验 5：内容使用诊断与协议验证 (Usage Diagnosis and Protocol Check)

必须新增：

- `Image Shuffle Drop Rate`
- `Random Caption Drop Rate`
- `OCR Drop Rate`
- 全局离线 80/10/10 切分与 leave-one-out 的对照附表

**意义**：

- 这是回应“模型到底有没有真用多模态内容”和“协议是否写对了”的直接证据。

## 实验 6：效率与可扩展性 (Efficiency and Scalability)

报告：

- 每 epoch 训练时间
- 峰值显存
- 不同 batch size 下的吞吐量
- `Top-50 / Top-100 / Top-200` rerank 成本
- relaxed solver variant 与简单 partial baseline 的效率对比

**要求**：

- 效率实验是防御性证据，不是主文 headline。
- 主文只保留最能说明可行性的 1 张表，其余可放 appendix。

## 实验 7：定性可视化 (Case Study)

- 展示 clean / nuisance / lure negative 案例
- 展示被拒绝的背景和营销词
- 展示失败案例，分析何时 reject semantics 失效

------

## 离线数据生成方案 (LMM 蒸馏)

本部分严格降级为 **“VLM 辅助审计，不进入主训练闭环”**。

```text
Step 1: 解析标题、属性、OCR，构造文本节点。
Step 2: 由 patch 或轻量 region proposal 构造视觉节点。
Step 3: 构造文本和视觉拓扑边，并缓存块对角代价矩阵。
Step 4: 生成 positive-preserving nuisance 与 negative-preserving lure 样本，并记录精确 mask。
Step 5: 用自监督稳定性与 corruption 判别任务预训练 reliability prior 与 capacity prior。
Step 6: 用 VLM 对复杂样本生成最小充分证据候选，仅用于审计集构建。
Step 7: 训练阶段只读取缓存图，不在主循环中重复提图。
```

**说明**：

- 不将任何闭源 API 作为主训练必要依赖。
- VLM 只用于评估集预标注和解释核验。

------

## 实现技术栈

```text
torch>=2.2
recbole>=1.2
transformers>=4.45
sentence-transformers>=3.0
open-clip-torch>=2.24
paddleocr>=2.8
opencv-python
scikit-learn
networkx
numpy
pandas
matplotlib
seaborn
```

**可选组件**：

- `flash-attn` 或自定义 fused kernel
- `SigLIP` 或等价开放视觉 backbone
- `BGE / e5` 文本编码器
- `POT` 仅用于 toy numeric check，不进入主训练

**建议算力**：

- 原型阶段：`2 x 24GB GPU`
- 正式实验：`4 x 24GB GPU`
- 若算力不足，先保留 Amazon 主基准 + 四个子集 + `Top-100` rerank 的闭环

------

## 详细时间规划（6-8个月收敛版）

## 月份 1：拓扑图、容量先验与协议对齐

- [ ] 跑通 global 80/10/10 数据管线
- [ ] 构建文本与视觉块对角拓扑
- [ ] 完成 reliability prior 与 capacity prior
- [ ] 在 1000 个样本上验证 nuisance 识别和容量分离

**退出条件**：  
若 protocol 仍然不一致，先停写 method，先修数据与配置。

## 月份 2：局部传输闭环

- [ ] 完成 partial / hybrid partial transport 核心算子
- [ ] 显式输入 `p, q(r), m_ui`
- [ ] 在 `BatchSize >= 256` 下稳定反传
- [ ] 验证 reject semantics 是否成立

**退出条件**：  
若 reject semantics 只能靠额外 heuristic 才成立，题目必须收缩。

## 月份 3：normalized support 干预层

- [ ] 完成 normalized support 与 logit 映射
- [ ] 接入 leakage ratio 与 intervention loss
- [ ] 跑出第一版 `SupportF1 / LeakageRatio`

**退出条件**：  
若指标体系仍然可被 exploit，必须重写 support 定义。

## 月份 4：主 benchmark 大表

- [ ] 跑完 Amazon Reviews 2023 主表
- [ ] 跑完 high-conflict / missing-modality / long-tail / usage diagnosis 子集
- [ ] 跑完 image shuffle 与 random caption 诊断

**退出条件**：  
若 usage diagnosis 不成立，立刻停止扩写论文。

## 月份 5：审计集与机制消融

- [ ] 完成 VLM 预标注审计集
- [ ] 完成人工双盲仲裁子集
- [ ] 跑完 SupportF1、LeakageRatio 与机制消融

## 月份 6：论文主稿收敛

- [ ] 把贡献点收缩为 3 条
- [ ] 补齐效率实验和失败案例
- [ ] 完成 rebuttal 预案

## 月份 7-8：投稿准备缓冲期

- [ ] 复跑关键表格
- [ ] 清理代码与脚本
- [ ] 准备 appendix 与开源包
- [ ] 按官方 CFP 时间提交

------

## 代码组织结构

```text
CIEPT-R/
├── conf/
│   ├── dataset_legacy_time.yaml
│   ├── dataset_amazon2023_presplit.yaml
│   └── model_cieptr.yaml
├── data_prep/
│   ├── build_evidence_graph.py
│   ├── build_topology_cost.py
│   ├── build_intent_anchors.py
│   ├── compute_reliability.py
│   ├── compute_capacity_prior.py
│   ├── build_corruption_benchmark.py
│   ├── build_vlm_audit_set.py
│   └── build_usage_diagnostic.py
├── src/
│   ├── dataset/
│   │   └── graph_dataset.py
│   ├── models/
│   │   ├── layers/
│   │   │   ├── partial_transport.py
│   │   │   ├── topology_encoder.py
│   │   │   ├── reliability_head.py
│   │   │   └── normalized_support_intervention.py
│   │   └── cieptr_reranker.py
│   ├── loss/
│   │   ├── listmle_loss.py
│   │   ├── intervention_loss.py
│   │   └── optional_sdpo_loss.py
│   └── eval/
│       ├── ranking_metrics.py
│       ├── faithfulness_metrics.py
│       ├── corruption_eval.py
│       ├── usage_diagnostic_eval.py
│       └── efficiency_eval.py
├── scripts/
│   ├── preprocess_amazon2023_split.py
│   ├── run_amazon2023.sh
│   ├── run_corruption.sh
│   ├── run_audit_eval.sh
│   └── run_efficiency_eval.sh
└── notebooks/
    ├── visualize_transport_support.ipynb
    ├── plot_corruption_curves.ipynb
    ├── inspect_topology_cost.ipynb
    └── analyze_failure_modes.ipynb
```

------

## 关键技术细节（用于写入 Method 的理论护城河）

令用户意图图为 \(\mathcal{G}^u = (\mathcal{V}^u, C^u)\)，商品证据图为 \(\mathcal{G}^i = (\mathcal{V}^i, C^i)\)。我们定义容量校准的局部传输目标：

\[
T^\star
= \arg\min_{T \ge 0}
\langle C_{\text{feat}}, T \rangle
+ \alpha \, \mathrm{GW}(C^u, C^i, T)
- \varepsilon H(T)
+ \tau_u \mathrm{KL}(T \mathbf 1 \,\|\, \mathbf p)
+ \tau_i \mathrm{KL}(T^\top \mathbf 1 \,\|\, \mathbf q(\mathbf r))
\]

满足：

\[
T \mathbf 1 \le \mathbf p,\quad
T^\top \mathbf 1 \le \mathbf q(\mathbf r),\quad
\mathbf 1^\top T \mathbf 1 \le m_{ui}
\]

其中：

- \(\mathbf p\) 是用户意图节点的源分布；
- \(\mathbf q(\mathbf r)\) 是由 reliability 调制的 target capacity；
- \(m_{ui}\) 是当前 user-item pair 的总运输质量预算；
- \(\mathrm{GW}(C^u, C^i, T)\) 是结构正则项，用于鼓励拓扑一致的匹配，而不是主文唯一焦点。

商品图拓扑 \(C^i\) 被定义为块对角矩阵：

\[
C^i =
\begin{bmatrix}
C^{\text{text}} & +\infty \\
+\infty & C^{\text{vision}}
\end{bmatrix}
\]

即文本拓扑和视觉拓扑在各自流形中定义，跨模态区域不承担几何意义；跨模态一致性仅通过 \(C_{\text{feat}}\) 建模。

由 \(T^\star\) 得到 raw support：

\[
s_j = \sum_k T^\star_{kj}
\]

再定义 capacity-normalized support：

\[
\tilde s_j = \frac{s_j}{q_j(\mathbf r) + \epsilon}
\]

并定义 leakage ratio：

\[
\mathrm{LR} = \frac{\sum_j \tilde s_j \nu_j}{\sum_j \tilde s_j + \epsilon}
\]

其中 \(\nu_j\) 为 nuisance mask。  
训练阶段将 \(\tilde s_j\) 映射至 logit 空间后再进入 Binary Gumbel / Hard Concrete 干预层，测试阶段则直接用 \(\tilde s_j\) 与审计集进行评估。

最终总损失：

\[
\mathcal{L}
= \mathcal{L}_{rank}
+ \lambda_{pt} \mathcal{L}_{partial}
+ \lambda_{leak} \mathcal{L}_{leak}
+ \lambda_{suff} \mathcal{L}_{suff}
+ \lambda_{comp} \mathcal{L}_{comp}
+ \lambda_{audit} \mathcal{L}_{audit}
\]

**论文中的理论解释必须强调**：

- 核心不是更复杂的 solver，而是显式 reject semantics。
- partial transported mass 直接对应最小充分证据选择，比单纯质量销毁更具可解释性。
- Gromov 项是结构正则，不应抢走论文主问题。
- normalized support 与 leakage ratio 必须和 capacity prior 一致，否则指标失真。

------

## 实验Checklist（逐项验证）

- [ ] 是否彻底移除主训练中的 `POT` 和 `stop-gradient solver`？
- [ ] 是否显式给出并使用了 `p`、`q(r)` 和 `m_ui`？
- [ ] 是否把主问题重新收回到 `reject semantics + minimal evidence`？
- [ ] 是否将商品拓扑定义为块对角矩阵？
- [ ] 是否先正规化 support 再进入 logit？
- [ ] 是否将 `MLR` 改为 `LeakageRatio`？
- [ ] 是否在预处理阶段完成了 global 80/10/10 split？
- [ ] 是否只把 Amazon Reviews 2023 作为主 benchmark？
- [ ] 是否加入 image shuffle / random caption 诊断？
- [ ] 是否构建规模化 VLM 审计集和人工仲裁子集？
- [ ] 是否报告 `SupportF1 / SufficiencyGap / ComprehensivenessGap / LeakageRatio`？
- [ ] 是否把 S-DPO 降级为 appendix-only？

------

## 风险预案

## 风险 1：局部传输实现仍不稳定

**应对方案**：

- 从 simplified partial transport 开始验证 reject semantics
- 再逐步加入结构正则项
- solver 细节优先服务于主问题，而不是反过来主导论文

## 风险 2：Gromov 项增益不稳定

**应对方案**：

- 若 Gromov 项贡献弱，则降级为结构正则附加项
- 主问题仍然保留：capacity-calibrated reject option

## 风险 3：normalized support 仍不稳定

**应对方案**：

- 检查 capacity prior 是否过小导致归一化爆炸
- 对 \(\tilde s_j\) 做稳健截断
- 在 appendix 中报告不同正规化策略的敏感性

## 风险 4：审计集标签噪声大

**应对方案**：

- VLM 只作为候选，不作为最终 gold
- 保留人工仲裁子集作为 gold subset
- 若 VLM 质量差，则收缩预标注规模，优先保证 gold subset 质量

------

## 参考文献完整清单（主文优先引用）

1. `CLEAR: Null-Space Projection for Cross-Modal De-Redundancy in Multimodal Recommendation`
2. `RecGOAT: Graph Optimal Adaptive Transport for LLM-Enhanced Multimodal Recommendation with Dual Semantic Alignment`
3. `I$^3$-MRec: Invariant Learning with Information Bottleneck for Incomplete Modality Recommendation`
4. `Teach Me How to Denoise: A Universal Framework for Denoising Multi-modal Recommender Systems via Guided Calibration`
5. `Training-free Graph-based Imputation of Missing Modalities in Multimodal Recommendation`
6. `IGDMRec: Behavior Conditioned Item Graph Diffusion for Multimodal Recommendation`
7. `Modality-Guided Mixture of Graph Experts with Entropy-Triggered Routing for Multimodal Recommendation`
8. `Binge Watch: Reproducible Multimodal Benchmarks Datasets for Large-Scale Movie Recommendation on MovieLens-10M and 20M`
9. `Do Recommender Systems Really Leverage Multimodal Content? A Comprehensive Analysis on Multimodal Representations for Recommendation`
10. `Towards Trustworthy Multimodal Recommendation`
11. `Fused Partial Gromov-Wasserstein for Structured Objects`
12. `Comparative Explanations via Counterfactual Reasoning in Recommendations`
13. `On the Definition and Detection of Cherry-Picking in Counterfactual Explanations`
14. `Bridging Language and Items for Retrieval and Recommendation`

------

## 创新亮点总结 / 论文撰写要点 (Reviewer 视角攻防)

在 Intro 中，必须把叙事压缩成三层：

> **Problem**: Existing multimodal recommenders still score overly large evidence sets, which makes them absorb nuisance cues instead of selecting the minimal evidence that is actually sufficient for ranking.

> **Gap**: Existing denoising and transport-based methods improve robustness, but they do not cleanly expose an explicit reject option with auditable minimal-evidence semantics.

> **Solution**: We propose a capacity-calibrated partial intent-evidence transport framework, where transported mass encodes a reject option, block-diagonal topology regularizes within-modality structure, and audited normalized support validates minimal sufficient evidence selection.

**贡献点建议只保留 3 条**：

1. 提出 capacity-calibrated partial transport，使 transported mass 直接刻画最小充分证据选择与 reject semantics。
2. 提出块对角拓扑和 reliability-driven capacity prior，使结构约束与证据容量定义一致。
3. 提出基于 normalized support、Leakage Ratio 和 content usage diagnosis 的审计协议，用于验证模型真实依赖的证据子集。

**严禁继续写成主贡献的内容**：

- 更复杂的 solver 命名
- 黑盒 `POT`
- `stop-gradient` OT
- 把 support 直接当 Gumbel logits
- S-DPO
- 把短视频 benchmark 和电商 benchmark 并列为主战场

------

## 最终交付物

1. **AAAI/SIGIR 口径主文初稿**：围绕 `reject semantics + minimal evidence + audited support` 三个关键词组织主文。
2. **可复现代码**：基于 RecBole 的数据与评估框架，外加 capacity-calibrated partial reranker。
3. **Amazon Reviews 2023 主 benchmark 包**：含 high-conflict、missing-modality、long-tail 和 usage diagnosis 子集。
4. **VLM-in-the-loop 审计集**：带人工仲裁子集的支持集评估数据。
5. **效率与失败案例包**：用于 rebuttal 时防御方法边界与工程可行性。

**领域主席最终行动指令（Action Item）**：

接下来 6 周只允许关注三件事：

1. 数学式、伪代码、指标三者是否彻底对齐：`p / q(r) / m_ui / normalized support / LeakageRatio`。  
2. 全局时间切分和 usage diagnosis 是否真正跑在 Amazon Reviews 2023 主表上。  
3. partial reject semantics 是否在 `SupportF1` 和 `LeakageRatio` 上同时成立。  

如果这三件事跑不通，这篇 paper 还不具备 AAAI 级投稿基础。  
如果这三件事跑通，项目才真正从“会写 OT”进入“能打 AAAI”的状态。
