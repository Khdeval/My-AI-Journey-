import os
from openai import OpenAI
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=dotenv_path)

api_key = (os.getenv("OPENAI_API_KEY") or "").strip().strip('"').strip("'")
if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is missing. Set it in .env in the project root."
    )

client = OpenAI(api_key=api_key)

def route_query(user_query):
    print(f"🚦 Routing query: '{user_query}'")
    
    # The 'Router' Prompt: We ask the AI to categorize the query
    router_prompt = f"""
    Analyze the following user query and categorize it into exactly one of these two categories:
    1. 'security' (if it relates to MFA, encryption, or access)
    2. 'technical' (if it relates to API performance, status codes, or formatting)
    
    Query: {user_query}
    
    Return ONLY the category name in lowercase.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": router_prompt}]
    )
    
    category = response.choices[0].message.content.strip()
    return category

# Test the Router
query_1 = "How do I test the login speed?"
category_1 = route_query(query_1)
print(f"➡️ Route selected: {category_1}\n")

query_2 = "What are the MFA requirements?"
category_2 = route_query(query_2)
print(f"➡️ Route selected: {category_2}")