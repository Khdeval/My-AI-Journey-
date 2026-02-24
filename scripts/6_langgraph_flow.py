from typing import TypedDict
from langgraph.graph import StateGraph, END
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# 1. Define the Shared Memory (State)
class AgentState(TypedDict):
    requirement: str
    test_plan: str
    feedback: str
    revision_count: int
    auditor_decision: str

# 2. Define the Nodes (The Agents)
def architect_node(state: AgentState):
    print(f"🎨 Architect (Attempt {state['revision_count'] + 1})")
    prompt = f"Requirement: {state['requirement']}\nFeedback: {state['feedback']}\nCreate a test plan."
    response = client.chat.completions.create(
        model="gpt-4o", messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content
    return {"test_plan": response, "revision_count": state['revision_count'] + 1}

def auditor_node(state: AgentState):
    print("⚖️ Auditor Checking...")
    prompt = f"Review this: {state['test_plan']}. If perfect, say 'APPROVED'. Otherwise, list missing cases."
    response = client.chat.completions.create(
        model="gpt-4o", messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content
    decision = "approved" if "APPROVED" in response.upper() else "revise"
    return {"feedback": response, "auditor_decision": decision}

# 3. Define the Logic Gate (The Router)
def decide_to_continue(state: AgentState):
    if state.get("auditor_decision") == "approved" or state['revision_count'] >= 3:
        return "end"
    return "revise"

# 4. Build the Graph
workflow = StateGraph(AgentState)

workflow.add_node("architect", architect_node)
workflow.add_node("auditor", auditor_node)

workflow.set_entry_point("architect")
workflow.add_edge("architect", "auditor")

workflow.add_conditional_edges(
    "auditor",
    decide_to_continue,
    {
        "revise": "architect",
        "end": END,
    }
)

app = workflow.compile()


def run_langgraph_workflow(requirement: str):
    initial_state: AgentState = {
        "requirement": requirement,
        "test_plan": "",
        "feedback": "",
        "revision_count": 0,
        "auditor_decision": "revise",
    }
    return app.invoke(initial_state)


if __name__ == "__main__":
    requirement = "A login system that requires MFA and SHA-256 password hashing."
    result = run_langgraph_workflow(requirement)

    print("\n--- FINAL TEST PLAN ---")
    print(result["test_plan"])
    print("\n--- FINAL FEEDBACK ---")
    print(result["feedback"])
    print(f"\n--- REVISIONS USED ---\n{result['revision_count']}")
    print(f"\n--- AUDITOR DECISION ---\n{result['auditor_decision']}")