import streamlit as st
import os
import chromadb
from openai import OpenAI, AuthenticationError
from dotenv import load_dotenv
from pathlib import Path
import time

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

api_key = (os.getenv("OPENAI_API_KEY") or "").strip().strip('"').strip("'")
if not api_key:
    st.error("Missing OPENAI_API_KEY. Add it to .env in the project root.")
    st.stop()

client = OpenAI(api_key=api_key)

if "openai_auth_ok" not in st.session_state:
    try:
        client.models.list()
        st.session_state["openai_auth_ok"] = True
        st.session_state["openai_auth_error"] = ""
    except AuthenticationError:
        st.session_state["openai_auth_ok"] = False
        st.session_state["openai_auth_error"] = (
            "OpenAI authentication failed (401). Your OPENAI_API_KEY appears invalid, revoked, "
            "or from a different project. Generate a fresh key in OpenAI, update .env, then restart Streamlit."
        )
    except Exception as error:
        st.session_state["openai_auth_ok"] = False
        st.session_state["openai_auth_error"] = f"OpenAI preflight check failed: {error}"

st.set_page_config(page_title="QA AI Workflow Lab", page_icon="🤖")
st.title("🚀 QA AI Workflow Orchestrator")

if not st.session_state.get("openai_auth_ok", False):
    st.error(st.session_state.get("openai_auth_error", "OpenAI authentication check failed."))
    st.stop()

# --- Initialize Database ---
db_client = chromadb.PersistentClient(path="./data/chroma_db")
collection = db_client.get_collection(name="engineering_docs")

user_query = st.text_input("Enter a requirement to generate a test case:")

if st.button("Generate & Trace"):
    if user_query:
        # Start a timer for the trace
        start_time = time.time()
        
        try:
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
        except AuthenticationError:
            st.error(
                "OpenAI authentication failed (401). Your OPENAI_API_KEY appears invalid, revoked, or from a different project. "
                "Generate a fresh key in OpenAI, update .env, then restart Streamlit."
            )
            st.stop()

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