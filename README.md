🚀 AI Workflow Orchestrator: Requirements-to-Test EngineAn enterprise-grade RAG (Retrieval-Augmented Generation) pipeline that automates the generation of software test cases from technical requirements. This project demonstrates the transition from traditional QA to AI Workflow Engineering by implementing intelligent routing, metadata-filtered retrieval, and automated AI-as-a-Judge evaluation.
🛠️ The StackOrchestration: Python, OpenAI GPT-4oVector Database: ChromaDB (Persistent)Evaluation: DeepEval (Unit Testing for LLMs)Frontend: StreamlitEnvironment: GitHub Codespaces

🏗️ Architectural Decisions 

1. Metadata-Aware RoutingInstead of a "flat" search, I implemented an Intent Router.The Problem: Large context windows often lead to "Prompt Noise" where the LLM misses specific requirements.

The Solution: A specialized LLM-gate categorizes queries (e.g., Security vs. Technical) before querying the database.Benefit: Increases Context Precision and reduces token costs by filtering the search space in ChromaDB.

2. Hallucination Guardrails (AI-as-a-Judge)To solve the stochastic nature of LLMs, I integrated a formal Evaluation Layer.Mechanism: Every generated test case is audited using a Faithfulness Metric.Validation: The system cross-references the Actual Output against the Retrieval Context. If the faithfulness score is $< 0.7$, the output is flagged for human review.
   
3. Change Data Capture (CDC) & Upsert LogicTo prevent Knowledge Regression, the ingestion layer is designed for dynamic updates.Process: Using Persistent ChromaDB, requirements can be "Upserted" (updated/inserted) via the scripts/1_ingest.py pipeline. This ensures the AI always references the latest "Source of Truth."
   
📂 Project StructureBash├── data/chroma_db/      # Persistent Vector Store (Long-term memory)

├── scripts/

│   ├── 1_ingest.py      # Metadata-driven data ingestion pipeline

│   ├── 2_router.py      # Intent classification logic

│   ├── 3_workflow.py    # Integrated RAG & Generation engine

│   └── 4_evaluator.py   # DeepEval audit & faithfulness checks

├── app.py               # Streamlit UI with Execution Tracing

└── .env                 # Protected environment variables

🚦 Getting StartedClone the repo:
Bashgit clone https://github.com/your-username/my-ai-journey-.git

Install Dependencies:Bashpip install -r requirements.txt

Run the Ingestion:Bashpython scripts/1_ingest.py

Launch the Orchestrator:Bashstreamlit run app.py

📈 Observability & TracingThe application features a Custom Execution Trace. 
This provides transparency into the "Reasoning Loop," 
showing:Total LatencyRouter 
ClassificationMetadata 
filter applied
Specific database chunks retrieved
