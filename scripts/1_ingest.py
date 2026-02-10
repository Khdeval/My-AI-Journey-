import chromadb
import uuid

# Initialize DB in the 'data' folder
client = chromadb.PersistentClient(path="./data/chroma_db")
collection = client.get_or_create_collection(name="engineering_docs")

# Requirement Data with Metadata for Workflow Routing
raw_data = [
    {
        "text": "Rule: All admin accounts must use Multi-Factor Authentication (MFA).", 
        "metadata": {"category": "security", "priority": "high"}
    },
    {
        "text": "Rule: API response time for login must be under 200ms.", 
        "metadata": {"category": "technical", "priority": "medium"}
    },
    {
        "text": "Rule: Passwords must be encrypted using SHA-256.", 
        "metadata": {"category": "security", "priority": "high"}
    }
]

print("📥 Starting professional ingestion...")

for item in raw_data:
    collection.add(
        documents=[item["text"]],
        metadatas=[item["metadata"]],
        ids=[str(uuid.uuid4())]
    )

print(f"✅ Ingested {len(raw_data)} documents into 'my-ai-journey-' memory.")