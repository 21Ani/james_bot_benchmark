# James Bot Benchmarking Study — QE Assignment

A repeatable benchmarking framework for measuring **James Bot** (TalkingDB-powered document QA) against **household AI** (ChatGPT without proprietary document access).

## 1. Benchmarking Goal

**Goal:** Enterprise Knowledge Base Document QA

James Bot is designed for customer-support teams that query large, proprietary knowledge bases (PDFs, manuals, policies). Household AI assistants like ChatGPT answer from general training data and cannot reliably answer company-specific questions.

This study measures whether James Bot's TalkingDB document indexing provides a **differentiator** on domain-specific QA — similar to how PageIndex positioned "Long Document QA" as its benchmark focus.

| Aspect | This Study | PageIndex Reference |
|--------|------------|---------------------|
| Differentiator | Enterprise KB QA over indexed documents | Long-document financial QA |
| Competitor | ChatGPT (no document access) | ChatGPT 5.1 |
| Primary metric | Answer accuracy vs ground truth | Accuracy + response time |

## 2. Benchmark Dataset

**Dataset:** Enterprise Knowledge Base QA Dataset (18 questions, 3 documents)

Inspired by PageIndex's approach of pairing real-world documents with practitioner questions, this dataset includes:

- 3 enterprise product documents (~40 sections total)
- 18 practical support questions across warranty, SLA, compliance, billing, security
- Ground-truth answers extracted directly from source documents

Each response is marked **inaccurate** if it does not match the information in the queried document — per assignment requirements.

### Extending the dataset

Add documents to `data/documents/` and register them in `data/benchmark_dataset.json`.

## 3. Evaluation Metrics

| Metric | Description |
|--------|-------------|
| **Strict Accuracy** | Normalized expected answer appears in response |
| **Fuzzy Accuracy** | Token-set similarity ≥ 85% (RapidFuzz) |
| **Grounding Score** | % of response tokens found in source document |
| **Response Time** | End-to-end latency in milliseconds |

A response is considered **inaccurate** when fuzzy accuracy fails — i.e., it does not match document ground truth.

## 4. Project Structure

```
james_bot_benchmark/
├── config.yaml              # Benchmark configuration
├── run_benchmark.py         # CLI entry point
├── requirements.txt
├── data/
│   ├── benchmark_dataset.json
│   └── documents/           # Source knowledge-base files
├── src/
│   ├── adapters.py          # James Bot & ChatGPT integrations
│   ├── config.py
│   ├── dataset.py
│   ├── evaluator.py
│   └── runner.py
└── results/                 # Generated reports (JSON + Markdown)
```

## 5. Quick Start

```bash
cd james_bot_benchmark
pip install -r requirements.txt
python run_benchmark.py
```

### Live API mode (optional)

Create a `.env` file:

```env
OPENAI_API_KEY=sk-...
JAMES_BOT_API_URL=https://your-james-bot-endpoint
JAMES_BOT_API_KEY=your-key
```

- **James Bot adapter** calls `POST /query` with `{question, document_id}`
- **ChatGPT adapter** runs without document context by default (household AI baseline)
- Set `include_document_context: true` in `config.yaml` to test an upper-bound ChatGPT+RAG baseline

### Demo mode (no API keys)

Without API keys, the framework runs in **mock mode**:

- James Bot mock simulates grounded document retrieval (high accuracy)
- ChatGPT mock simulates generic answers (lower accuracy on domain questions)

## 6. Repeatability

This framework is designed for continuous benchmarking across James Bot versions:

1. Keep the dataset and config stable across runs
2. Run `python run_benchmark.py` after each release
3. Compare `results/benchmark_report_*.json` over time
4. Track `accuracy_delta_pct` between James Bot and competitor

## 7. Assignment Deliverables Covered

- [x] **Benchmarking goal** — Enterprise KB QA differentiator documented
- [x] **Suitable dataset** — 3 documents, 18 domain-practitioner questions
- [x] **Evaluation metrics** — Accuracy (strict + fuzzy), grounding, response time
- [x] **Repeatable study** — Config-driven, versioned reports, pluggable adapters
- [x] **James Bot vs household AI** — Side-by-side comparison with delta metrics

## 8. Methodology Notes (for submission)

When submitting this assignment, include:

1. The benchmark goal rationale (why KB QA is James Bot's differentiator)
2. Dataset selection justification (enterprise support scenarios)
3. Results from a benchmark run (`results/benchmark_report_*.md`)
4. How this framework scales to future James Bot versions

Reference: [PageIndex FinanceBench methodology](https://pageindex.ai/blog/Mafin2.5) for industry-standard benchmarking patterns.
