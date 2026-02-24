import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def architect_agent(requirement):
    print("🎨 Architect: Drafting the test plan...")
    prompt = f"Create a detailed QA test plan for this requirement: {requirement}. Focus on edge cases."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def auditor_agent(test_plan):
    print("⚖️ Auditor: Reviewing the plan for gaps...")
    prompt = f"""
    Act as a Senior QA Auditor. Review this test plan:
    {test_plan}
    
    Identify any missing security or performance edge cases. 
    If the plan is perfect, say 'APPROVED'. 
    If not, provide 'FEEDBACK' on what to improve.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def run_multi_agent_workflow(requirement):
    draft = architect_agent(requirement)
    review = auditor_agent(draft)

    refined_draft = None
    if "APPROVED" not in review.upper():
        refinement_prompt = f"""
        Revise the following QA test plan based on this auditor feedback.

        Original plan:
        {draft}

        Auditor feedback:
        {review}

        Return only the improved test plan.
        """
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": refinement_prompt}]
        )
        refined_draft = response.choices[0].message.content

    return {
        "requirement": requirement,
        "initial_plan": draft,
        "auditor_review": review,
        "refined_plan": refined_draft,
        "approved": "APPROVED" in review.upper()
    }

if __name__ == "__main__":
    requirement = "A login system that requires MFA and SHA-256 password hashing."
    result = run_multi_agent_workflow(requirement)

    print("\n--- INITIAL PLAN ---")
    print(result["initial_plan"])
    print("\n--- AUDITOR REVIEW ---")
    print(result["auditor_review"])

    if result["refined_plan"]:
        print("\n--- REFINED PLAN ---")
        print(result["refined_plan"])