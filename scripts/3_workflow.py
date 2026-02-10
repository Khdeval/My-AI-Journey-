import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "..", "env", ".env")
load_dotenv(dotenv_path=dotenv_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is missing. Set it in env/.env without quotes or spaces."
    )

client = OpenAI(api_key=api_key)

# Initialize Database Connection
db_client = chromadb.PersistentClient(path="./data/chroma_db")
collection = db_client.get_collection(name="engineering_docs")

def run_integrated_workflow(user_query):
    # --- STAGE 1: ROUTING ---
    # Determine the category to filter our database
    router_prompt = f"Categorize this as 'security' or 'technical': {user_query}. Return only the word."
    category = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": router_prompt}]
    ).choices[0].message.content.strip().lower()
    
    print(f"🚦 Router categorized this as: {category}")

    # --- STAGE 2: FILTERED RETRIEVAL ---
    # We only look for documents that match the category identified by the router
    results = collection.query(
        query_texts=[user_query],
        n_results=1,
        where={"category": category} # This is Metadata Filtering
    )
    context = results['documents'][0][0]
    source = results['metadatas'][0][0]['source'] if 'source' in results['metadatas'][0][0] else "Unknown"

    # --- STAGE 3: GENERATION ---
    prompt = f"""
    You are a QA Specialist. Using the rule from {source}: '{context}', 
    write a detailed test case for: {user_query}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

# Execute the workflow
print("🤖 AI Workflow starting...")
result = run_integrated_workflow("I need to test our encryption standard.")
print("\n--- FINAL TEST CASE ---")
print(result)