import streamlit as st
import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import time

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

if not os.getenv("OPENAI_API_KEY"):
    st.error("Missing OPENAI_API_KEY. Add it to .env in the project root.")
    st.stop()

client = OpenAI()

st.set_page_config(page_title="QA AI Workflow Lab", page_icon="🤖")
st.title("🚀 QA AI Workflow Orchestrator")

# --- Initialize Database ---
db_client = chromadb.PersistentClient(path="./data/chroma_db")
collection = db_client.get_collection(name="engineering_docs")

user_query = st.text_input("Enter a requirement to generate a test case:")

if st.button("Generate & Trace"):
    if user_query:
        # Start a timer for the trace
        start_time = time.time()
        
        with st.spinner("Executing Workflow..."):
            # STAGE 1: ROUTING
            router_prompt = f"Categorize as 'security' or 'technical': {user_query}. Return one word."
            category = client.chat.completions.create(
                model="gpt-4o", messages=[{"role": "user", "content": router_prompt}]
            ).choices[0].message.content.strip().lower()
            
            # STAGE 2: RETRIEVAL
            results = collection.query(query_texts=[user_query], n_results=1, where={"category": category})
            context = results['documents'][0][0]
            metadata = results['metadatas'][0][0]
            
            # STAGE 3: GENERATION
            prompt = f"Using this rule: '{context}', write a test case for: {user_query}"
            response = client.chat.completions.create(
                model="gpt-4o", messages=[{"role": "user", "content": prompt}]
            )
            output = response.choices[0].message.content
            
            end_time = time.time()

        # --- THE TRACE SECTION ---
        with st.expander("🔍 View Execution Trace"):
            st.write(f"**Total Execution Time:** {round(end_time - start_time, 2)}s")
            st.json({
                "routing": {
                    "detected_category": category,
                    "logic": "LLM-based Intent Classification"
                },
                "retrieval": {
                    "source_document": context,
                    "metadata_filter_applied": metadata,
                    "database": "ChromaDB"
                },
                "generation": {
                    "model": "gpt-4o",
                    "tokens_used": "Estimate ~200"
                }
            })

        # --- FINAL OUTPUT ---
        st.markdown("### Generated Test Case")
        st.success(output)