from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase
from dotenv import load_dotenv


def _load_run_integrated_workflow():
    workflow_file = Path(__file__).with_name("3_workflow.py")
    module_spec = spec_from_file_location("workflow_module", workflow_file)
    if module_spec is None or module_spec.loader is None:
        raise ImportError(f"Could not load workflow module from {workflow_file}")
    workflow_module = module_from_spec(module_spec)
    module_spec.loader.exec_module(workflow_module)
    return workflow_module.run_integrated_workflow


run_integrated_workflow = _load_run_integrated_workflow()

load_dotenv()

# 1. Define our Batch of Test Scenarios
test_scenarios = [
    {
        "input": "How should I test SHA-256 encryption?",
        "expected_category": "security"
    },
    {
        "input": "What is the requirement for API response timeout?",
        "expected_category": "technical"
    },
    {
        "input": "How do we handle MFA login verification?",
        "expected_category": "security"
    }
]

def run_batch_test():
    results = []
    metric = FaithfulnessMetric(threshold=0.7)
    
    print(f"🧪 Starting Batch Test for {len(test_scenarios)} scenarios...\n")

    for i, scenario in enumerate(test_scenarios):
        print(f"Running Test {i+1}: {scenario['input']}")
        
        # Execute your actual workflow
        actual_output = run_integrated_workflow(scenario['input'])
        
        # Create a Test Case for Evaluation
        # In a real batch, you'd pull the actual context retrieved by the workflow
        test_case = LLMTestCase(
            input=scenario['input'],
            actual_output=actual_output,
            retrieval_context=["Standard: Use SHA-256 for encryption and 200ms for API timeouts."] 
        )
        
        metric.measure(test_case)
        
        results.append({
            "input": scenario['input'],
            "score": metric.score,
            "passed": metric.is_successful()
        })

    # --- FINAL REPORT ---
    print("\n📊 --- BATCH TEST REPORT ---")
    for res in results:
        status = "✅ PASS" if res['passed'] else "❌ FAIL"
        print(f"{status} | Score: {res['score']} | Query: {res['input']}")

if __name__ == "__main__":
    run_batch_test()