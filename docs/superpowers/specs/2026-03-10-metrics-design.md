# Ranking, Faithfulness, And Usage Metrics Design

## Context

The repository now has:

- a reranker that produces scores, plans, transported mass, and target usage
- an intervention module that produces normalized support and intervention losses
- an audit dataset protocol
- a toy train/eval entrypoint

The next missing layer is a stable metrics package that turns those outputs into reusable evaluation quantities. `T011` should centralize the formulas, but it should stop short of significance testing or full experiment orchestration.

## Goal

Create a `ciept.metrics` package that implements:

- ranking metrics
- faithfulness metrics
- usage-diagnosis metrics

in a form that later experiment runners can reuse.

## Scope

### In scope

- `Recall@k`
- `NDCG@k`
- `MRR`
- `SufficiencyGap`
- `ComprehensivenessGap`
- `LeakageRatio`
- `SupportPrecision/Recall/F1`
- `Image Shuffle Drop`
- `Random Caption Drop`
- `Missing-Modality Drop`
- `Transported Mass Ratio`

### Out of scope

- significance testing
- multi-seed aggregation
- experiment runner orchestration
- plotting

## Design Decisions

### 1. Split metrics by family, not by call site

Metrics should be grouped by conceptual family:

- ranking
- faithfulness
- usage diagnosis

This matches the project document and keeps later experiment code easy to read.

### 2. Reuse intervention semantics rather than redefining them

Where the repository already has a canonical formula, such as `LeakageRatio`, the metrics package should either reuse it directly or mirror it exactly. This avoids silent drift between training-time and evaluation-time definitions.

### 3. Keep metrics pure and side-effect-free

Metric functions should only compute outputs from inputs. They should not read files, mutate manifests, or perform logging. That work belongs to later experiment runners.

### 4. Make outputs JSON-friendly

Dataclass wrappers such as `RankingMetrics`, `FaithfulnessMetrics`, and `UsageDiagnostics` should contain plain floats so later experiment code can serialize them easily.

## Proposed Module Layout

- `src/ciept/metrics/types.py`
  - `RankingMetrics`
  - `FaithfulnessMetrics`
  - `UsageDiagnostics`

- `src/ciept/metrics/ranking.py`
  - `recall_at_k()`
  - `ndcg_at_k()`
  - `mrr_at_k()`

- `src/ciept/metrics/faithfulness.py`
  - `sufficiency_gap()`
  - `comprehensiveness_gap()`
  - `leakage_ratio()`
  - `support_precision_recall_f1()`

- `src/ciept/metrics/usage.py`
  - `image_shuffle_drop_rate()`
  - `random_caption_drop_rate()`
  - `missing_modality_drop()`
  - `transported_mass_ratio()`

## Ranking Metrics

### `recall_at_k`

Interpretation:

- whether the positive item ranks within the top `k` against negatives

### `ndcg_at_k`

Interpretation:

- ranking quality with logarithmic discount

### `mrr_at_k`

Interpretation:

- reciprocal rank of the positive item

## Faithfulness Metrics

### `sufficiency_gap`

`score_full - score_selected`

Smaller is better.

### `comprehensiveness_gap`

`score_full - score_removed`

Larger is better if the removed content was truly important.

### `leakage_ratio`

Same ratio-based definition as the intervention module:

`(norm_support * nuisance_mask).sum() / (norm_support.sum() + eps)`

### `support_precision_recall_f1`

- threshold `norm_support`
- compare against binary support gold
- compute precision, recall, and F1

## Usage-Diagnosis Metrics

### `image_shuffle_drop_rate`

Relative drop in score when image content is shuffled.

### `random_caption_drop_rate`

Relative drop in score when captions are replaced or randomized.

### `missing_modality_drop`

Relative drop when one modality is removed.

### `transported_mass_ratio`

`transported_mass / source_mass_sum`

This helps diagnose whether the model is collapsing transported mass to artificially reduce leakage.

## Validation Rules

Metric functions should fail fast for:

- invalid `k`
- incompatible shapes
- non-finite inputs

They should use `eps` where needed to avoid zero-division, but should not silently accept obviously malformed input.

## Testing Strategy

Tests will verify:

- ranking metrics on toy score lists
- faithfulness metrics on toy support and score examples
- usage metrics on toy before/after scores and masses

Tests will not verify:

- significance testing
- benchmark-scale correctness
- multi-run aggregation

## Follow-on Integration

This design gives `T012`:

- a clean metrics layer for experiment runners
- reusable formula implementations
- consistent evaluation semantics across ranking, faithfulness, and usage diagnosis
