# Training And Evaluation Entrypoint Design

## Context

The repository now has:

- a graph layer
- heuristic priors
- a toy transport sanity solver
- a torch reranker skeleton
- an intervention module with normalized support and leakage-ratio losses

What it still lacks is a single executable training-oriented path that proves these parts can be combined into one coherent forward/loss/backward/eval loop.

`T008` provides that bridge. It should not attempt to be a full trainer or experiment framework, but it must be real enough to run a toy training step and a toy evaluation step end-to-end.

## Goal

Create a minimal training/evaluation entrypoint that:

- uses the torch reranker on positive and negative items
- computes `confidence-weighted ListMLE`
- optionally adds intervention loss
- runs a single backward pass
- reports toy ranking metrics

## Scope

### In scope

- toy-batch generation
- ranking loss implementation
- a train step
- an eval step
- a small CLI for `train` and `eval`
- toy ranking metrics such as `Recall@1` and `MRR`

### Out of scope

- real dataset loading
- checkpointing
- optimizer factories beyond what is needed for a toy run
- large-scale training orchestration
- appendix-only objectives such as `S-DPO`

## Design Decisions

### 1. Prefer a real executable path over framework placeholders

The task should produce a toy training/evaluation path that actually runs. That is more valuable than building a large trainer skeleton that does nothing.

### 2. Keep the batch schema explicit and tiny

The training engine should consume a hand-crafted batch structure that directly matches the current transport/intervention interfaces. This keeps the wiring visible and avoids premature data-loader abstractions.

### 3. Use the project’s main ranking objective now

The main ranking loss should be the repository’s first real implementation of:

`confidence-weighted ListMLE`

This keeps `T008` aligned with the paper direction and prevents the codebase from drifting toward placeholder losses.

### 4. Intervention remains positive-path only for now

To keep the first training loop narrow, intervention loss should be computed on the positive item path only. This is sufficient to prove the modules connect without overcomplicating the first trainer.

### 5. Evaluation should stay toy but meaningful

`eval_step` should compute at least simple ranking diagnostics such as:

- `Recall@1`
- `MRR`

These do not need to be benchmark-grade metrics yet. They just need to show that the toy batch produces sensible ranking outputs.

## Proposed Module Layout

- `src/ciept/train/losses.py`
  - `confidence_weighted_listmle()`
  - `combined_training_loss()`

- `src/ciept/train/engine.py`
  - `train_step()`
  - `eval_step()`
  - toy-batch validation helpers

- `src/ciept/train/cli.py`
  - `--mode train`
  - `--mode eval`

- `src/ciept/eval/metrics.py`
  - `recall_at_1()`
  - `mean_reciprocal_rank()`

## Toy Batch Schema

The toy batch should include:

- `user_nodes`
- `pos_item_nodes`
- `neg_item_nodes`
- `source_mass`
- `pos_target_capacity`
- `neg_target_capacity`
- `mass_budget`
- `pos_nuisance_mask`
- `sample_weight`

This is enough to run the reranker, intervention loss, and ranking objective together.

## Train Step Flow

1. run the reranker on the positive item
2. run the reranker on each negative item
3. compute ranking loss with `confidence-weighted ListMLE`
4. compute intervention loss on the positive path
5. combine losses:

`total_loss = ranking_loss + lambda_intervention * intervention_loss`

6. backpropagate once

## Evaluation Step Flow

1. run positive and negative reranker scores
2. rank the positive score among negatives
3. compute toy `Recall@1`
4. compute toy `MRR`

## Validation Rules

The module should fail fast for:

- empty negative items
- non-positive sample weights
- mismatch between item tensors and capacity masks
- non-finite losses
- invalid CLI mode values

## Testing Strategy

Tests will verify:

- ranking loss directionality
- train-step output structure
- backward pass execution
- eval-step metric computation
- CLI success for both `train` and `eval`

Tests will not verify:

- long training runs
- real benchmark performance
- checkpointing
- distributed execution

## Follow-on Integration

This design gives later tasks:

- a real training-oriented entrypoint
- a place to integrate experiment runners
- a stable bridge between reranking, intervention, and optimization
