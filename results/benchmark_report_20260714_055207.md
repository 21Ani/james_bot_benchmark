# James Bot Enterprise Knowledge Base QA Benchmark

**Run:** 2026-07-14T05:52:07.548183+00:00
**Dataset:** Enterprise Knowledge Base QA Dataset

## Benchmark Goal
Evaluate James Bot's accuracy on enterprise knowledge-base question answering compared to household AI (ChatGPT without document grounding). James Bot uses TalkingDB for structured document indexing — this benchmark tests whether that provides a measurable advantage on multi-document, domain-specific QA tasks that customer-support teams routinely face.

## Aggregated Metrics

| System | Strict Accuracy | Fuzzy Accuracy | Avg Grounding | Avg Response (ms) |
|--------|-----------------|----------------|---------------|-------------------|
| James Bot (TalkingDB) | 94.44% | 61.11% | 100.0 | 350.06 |
| ChatGPT (Household AI) | 0.0% | 0.0% | 40.91 | 800.0 |

## James Bot vs Competitor

- Accuracy delta (fuzzy): **61.11%**
- James Bot grounding: **100.0**
- Competitor grounding: **40.91**

## Per-Question Results

- [PASS] `james_bot` **Q001**: fuzzy=100.0, grounding=100.0
- [PASS] `james_bot` **Q002**: fuzzy=100.0, grounding=100.0
- [PASS] `james_bot` **Q003**: fuzzy=100.0, grounding=100.0
- [FAIL] `james_bot` **Q004**: fuzzy=83.0, grounding=100.0
- [PASS] `james_bot` **Q005**: fuzzy=100.0, grounding=100.0
- [PASS] `james_bot` **Q006**: fuzzy=93.6, grounding=100.0
- [PASS] `james_bot` **Q007**: fuzzy=100.0, grounding=100.0
- [PASS] `james_bot` **Q008**: fuzzy=100.0, grounding=100.0
- [PASS] `james_bot` **Q009**: fuzzy=100.0, grounding=100.0
- [FAIL] `james_bot` **Q010**: fuzzy=81.5, grounding=100.0
- [FAIL] `james_bot` **Q011**: fuzzy=27.8, grounding=100.0
- [PASS] `james_bot` **Q012**: fuzzy=87.8, grounding=100.0
- [PASS] `james_bot` **Q013**: fuzzy=100.0, grounding=100.0
- [PASS] `james_bot` **Q014**: fuzzy=89.2, grounding=100.0
- [FAIL] `james_bot` **Q015**: fuzzy=25.0, grounding=100.0
- [FAIL] `james_bot` **Q016**: fuzzy=69.2, grounding=100.0
- [FAIL] `james_bot` **Q017**: fuzzy=45.5, grounding=100.0
- [FAIL] `james_bot` **Q018**: fuzzy=59.3, grounding=100.0
- [FAIL] `chatgpt` **Q001**: fuzzy=47.1, grounding=38.5
- [FAIL] `chatgpt` **Q002**: fuzzy=44.4, grounding=75.0
- [FAIL] `chatgpt` **Q003**: fuzzy=34.8, grounding=61.5
- [FAIL] `chatgpt` **Q004**: fuzzy=30.9, grounding=66.7
- [FAIL] `chatgpt` **Q005**: fuzzy=17.3, grounding=45.5
- [FAIL] `chatgpt` **Q006**: fuzzy=40.6, grounding=45.5
- [FAIL] `chatgpt` **Q007**: fuzzy=15.2, grounding=27.3
- [FAIL] `chatgpt` **Q008**: fuzzy=27.4, grounding=27.3
- [FAIL] `chatgpt` **Q009**: fuzzy=13.0, grounding=27.3
- [FAIL] `chatgpt` **Q010**: fuzzy=23.3, grounding=27.3
- [FAIL] `chatgpt` **Q011**: fuzzy=33.6, grounding=27.3
- [FAIL] `chatgpt` **Q012**: fuzzy=30.1, grounding=27.3
- [FAIL] `chatgpt` **Q013**: fuzzy=17.4, grounding=58.3
- [FAIL] `chatgpt` **Q014**: fuzzy=36.0, grounding=36.4
- [FAIL] `chatgpt` **Q015**: fuzzy=13.0, grounding=36.4
- [FAIL] `chatgpt` **Q016**: fuzzy=25.3, grounding=36.4
- [FAIL] `chatgpt` **Q017**: fuzzy=25.3, grounding=36.4
- [FAIL] `chatgpt` **Q018**: fuzzy=18.0, grounding=36.4
