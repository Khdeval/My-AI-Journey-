import streamlit as st
import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "env", ".env")
load_dotenv(dotenv_path=dotenv_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OPENAI_API_KEY is missing. Set it in env/.env without quotes or spaces.")
    st.stop()

client = OpenAI(api_key=api_key)

# --- Page Config ---
st.set_page_config(page_title="QA AI Workflow Lab", page_icon="🤖")
st.title("🚀 QA AI Workflow Orchestrator")
st.markdown("Generate requirement-specific test cases using a filtered RAG pipeline.")

# --- Sidebar / Settings ---
with st.sidebar:
    st.header("System Status")
    st.success("Database Connected")
    st.info("Model: GPT-4o")

# --- Initialize Database ---
db_client = chromadb.PersistentClient(path="./data/chroma_db")
collection = db_client.get_collection(name="engineering_docs")

# --- UI Logic ---
user_query = st.text_input("Enter a requirement to generate a test case:", 
                          placeholder="e.g., How should I test API response times?")

if st.button("Generate & Audit"):
    if user_query:
        with st.spinner("🔄 Routing & Retrieving..."):
            # 1. ROUTE
            router_prompt = f"Categorize as 'security' or 'technical': {user_query}. Return one word."
            category = client.chat.completions.create(
                model="gpt-4o", messages=[{"role": "user", "content": router_prompt}]
            ).choices[0].message.content.strip().lower()
            
            # 2. RETRIEVE
            results = collection.query(query_texts=[user_query], n_results=1, where={"category": category})
            context = results['documents'][0][0]
            
            # 3. GENERATE
            prompt = f"Using this rule: '{context}', write a test case for: {user_query}"
            response = client.chat.completions.create(
                model="gpt-4o", messages=[{"role": "user", "content": prompt}]
            )
            output = response.choices[0].message.content
            
        # --- DISPLAY RESULTS ---
        st.subheader(f"📍 Route: {category.upper()}")
        st.info(f"**Context Used:** {context}")
        st.markdown("### AI Generated Test Case")
        st.write(output)
    else:
        st.warning("Please enter a query first.")