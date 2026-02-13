import os
from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=dotenv_path)

api_key = (os.getenv("OPENAI_API_KEY") or "").strip().strip('"').strip("'")
if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is missing. Set it in .env in the project root."
    )

def audit_ai_output(user_query, context, ai_response):
    print("⚖️ Starting AI Audit...")
    
    # 1. Define the Test Case
    test_case = LLMTestCase(
        input=user_query,
        actual_output=ai_response,
        retrieval_context=[context]
    )
    
    # 2. Define the Metric (Threshold 0.7 means 70% accuracy required)
    metric = FaithfulnessMetric(threshold=0.7)
    
    # 3. Measure
    metric.measure(test_case)
    
    print(f"📊 Faithfulness Score: {metric.score}")
    print(f"📝 Reason: {metric.reason}")
    
    if metric.is_successful():
        print("✅ PASS: The AI stayed faithful to the requirements.")
    else:
        print("❌ FAIL: Potential Hallucination detected!")

# --- SIMULATED TEST ---
# Imagine our RAG system gave this output:
mock_context = "Rule: Passwords must be encrypted using SHA-256."
mock_ai_output = "The test case should verify that passwords are saved in plain text." # INTENTIONAL ERROR

audit_ai_output("Write a password security test.", mock_context, mock_ai_output)