# AI Workflow Orchestrator: Requirements-to-Test Engine

An enterprise-grade RAG (Retrieval-Augmented Generation) pipeline that automates generation of software test cases from technical requirements.

This project demonstrates the transition from traditional QA to AI Workflow Engineering with:
- intelligent routing,
- metadata-filtered retrieval,
- and automated AI-as-a-Judge evaluation.

## Stack

- Orchestration: Python, OpenAI GPT-4o
- Vector Database: ChromaDB (persistent)
- Evaluation: DeepEval (unit-style evaluation for LLM outputs)
- Frontend: Streamlit
- Environment: GitHub Codespaces / dev container

## Architectural Decisions

### 1) Metadata-Aware Routing

Instead of flat retrieval, the system uses an intent router.

- Problem: large contexts can introduce prompt noise and reduce precision.
- Solution: a router classifies each query (for example, `security` vs `technical`) before retrieval.
- Benefit: better context precision and lower token cost by narrowing ChromaDB search scope.

### 2) Hallucination Guardrails (AI-as-a-Judge)

An evaluation layer audits generated outputs with a faithfulness metric.

- Mechanism: compare generated output against retrieval context.
- Validation threshold: if score is < 0.7, output is flagged for human review.

### 3) CDC + Upsert Ingestion

To avoid knowledge regression, ingestion supports updates.

- Process: requirements are inserted/updated with upsert behavior in persistent ChromaDB via `scripts/1_ingest.py`.
- Benefit: generation stays aligned with latest source-of-truth docs.

## Project Structure

```text
.
├── app.py
├── config/
├── data/
│   └── chroma_db/
├── notes/
├── scripts/
│   ├── 0_healthcheck.py
│   ├── 1_ingest.py
│   ├── 2_router.py
│   ├── 3_workflow.py
│   ├── 4_evaluator.py
│   ├── 5_multi_agent.py
│   ├── 6_langgraph_flow.py
│   ├── 7_final_eval.py
│   └── test_suite.py
├── snippets/
├── requirements.txt
└── README.md
```

## Getting Started

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set environment variables in `.env` (including `OPENAI_API_KEY`).

3. Run preflight auth check (recommended):

```bash
python scripts/0_healthcheck.py
```

4. Ingest requirements/documents:

```bash
python scripts/1_ingest.py
```

5. Launch the Streamlit app:

```bash
streamlit run app.py
```

## Running the Batch Test Suite

Run:

```bash
python scripts/test_suite.py
```

What it does:
- Executes the integrated workflow across three predefined scenarios.
- Evaluates faithfulness with DeepEval.
- Prints a final pass/fail report with scores.

Note:
- `scripts/test_suite.py` dynamically loads `scripts/3_workflow.py` via `importlib` because module filenames starting with a digit cannot be imported with standard `from ... import ...` syntax.

## LangGraph Auditor Loop

Run:

```bash
python scripts/6_langgraph_flow.py
```

What it does:
- Runs an Architect → Auditor cycle using LangGraph.
- Auditor either approves or requests a revision.
- Loop ends when approved or max revision count is reached.

## Final System Audit (DeepEval)

`scripts/7_final_eval.py` provides `run_final_audit(query, context, output)` to score:
- retrieval quality (`ContextualRelevancyMetric`)
- generation honesty (`FaithfulnessMetric`)
- user satisfaction (`AnswerRelevancyMetric`)

In the Streamlit app, this is integrated as **Run LangGraph + Final Audit**, which:
- runs `scripts/6_langgraph_flow.py`
- evaluates the final test plan with `scripts/7_final_eval.py`
- shows the system health report in the UI

## Observability & Traceability

The app surfaces execution trace details, including:
- total latency,
- router classification,
- metadata filters applied,
- and retrieved chunks used for generation.
