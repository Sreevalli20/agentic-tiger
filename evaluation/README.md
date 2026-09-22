# Evaluation Directory

This directory contains the evaluation and benchmarking infrastructure for GraphProbe AI.

## Structure

- `datasets/` - Evaluation datasets and questions
- `runners/` - Benchmark execution runners
- `metrics/` - Metric calculation utilities
- `reports/` - Generated evaluation reports
- `schemas/` - Data schemas for evaluation

## Benchmark Runner

Run the benchmark:

```bash
python scripts/benchmark.py
```

Options:
- `--limit N` - Limit to N questions
- `--pipeline P` - Run specific pipeline (rag, graphrag, agentic)
- `--question-id ID` - Run specific question
- `--output PATH` - Output directory
- `--resume` - Resume from previous run

## Metrics

The evaluation system calculates:

- **Accuracy**: Correct answers / total questions
- **Completeness**: Required facts supported / expected facts
- **Citation Coverage**: Supported claims with citations / claims requiring evidence
- **Token Efficiency**: Tokens per successfully answered question
- **Retrieval Metrics**: Steps, chunks, nodes, edges
- **Agentic Behavior**: Iterations, strategy changes, tool usage

## Results

Benchmark results are saved in JSON/JSONL format in `evaluation/results/`.

Each result includes:
- Question ID and text
- Pipeline used
- Answer and citations
- Evidence and graph context
- Metrics (latency, tokens, retrieval)
- Agent trace (for agentic)
- Evaluation scores
