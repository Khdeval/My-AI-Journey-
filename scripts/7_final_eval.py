from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric, ContextualRelevancyMetric
from deepeval.test_case import LLMTestCase

# This script would run your compiled LangGraph app and capture the output
def run_final_audit(query, context, output):
    # Initialize metrics
    f_metric = FaithfulnessMetric(threshold=0.7)
    a_metric = AnswerRelevancyMetric(threshold=0.7)
    c_metric = ContextualRelevancyMetric(threshold=0.7)
    
    test_case = LLMTestCase(
        input=query,
        actual_output=output,
        retrieval_context=[context]
    )
    
    # Measure everything
    f_metric.measure(test_case)
    a_metric.measure(test_case)
    c_metric.measure(test_case)
    
    print(f"""
    📈 --- SYSTEM HEALTH REPORT ---
    1. Retrieval Quality (Context): {c_metric.score}
    2. Generation Honesty (Faithfulness): {f_metric.score}
    3. User Satisfaction (Relevance): {a_metric.score}
    """)

    return {
        "retrieval_quality": c_metric.score,
        "generation_honesty": f_metric.score,
        "user_satisfaction": a_metric.score,
    }

# Example usage with your Architect's output
# run_final_audit(user_requirement, retrieved_doc, final_test_plan)