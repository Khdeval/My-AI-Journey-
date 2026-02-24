import streamlit as st
import os
import chromadb
from openai import OpenAI, AuthenticationError
from dotenv import load_dotenv
from pathlib import Path
import time
from importlib.util import module_from_spec, spec_from_file_location


def load_script_module(script_filename: str, module_name: str):
    script_path = Path(__file__).resolve().parent / "scripts" / script_filename
    module_spec = spec_from_file_location(module_name, script_path)
    if module_spec is None or module_spec.loader is None:
        raise ImportError(f"Could not load module from {script_path}")
    module = module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module

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

st.divider()
st.subheader("🧪 Integrated Scripts")

left_col, right_col = st.columns(2)

with left_col:
    st.markdown("#### Batch Evaluation (`test_suite.py`)")
    if st.button("Run Batch Test Suite"):
        try:
            with st.spinner("Running batch tests..."):
                test_suite_module = load_script_module("test_suite.py", "test_suite_module")
                batch_results = test_suite_module.run_batch_test()

            if batch_results:
                st.success(f"Completed {len(batch_results)} test scenarios")
                st.dataframe(batch_results, use_container_width=True)
            else:
                st.warning("Batch test completed, but no results were returned.")
        except Exception as error:
            st.error(f"Batch test suite failed: {error}")

with right_col:
    st.markdown("#### Multi-Agent Review (`5_multi_agent.py`)")
    multi_agent_requirement = st.text_area(
        "Requirement for multi-agent review:",
        value="A login system that requires MFA and SHA-256 password hashing.",
        key="multi_agent_requirement"
    )

    if st.button("Run Multi-Agent Workflow"):
        try:
            with st.spinner("Running multi-agent workflow..."):
                multi_agent_module = load_script_module("5_multi_agent.py", "multi_agent_module")
                review_result = multi_agent_module.run_multi_agent_workflow(multi_agent_requirement)

            st.markdown("##### Architect Plan")
            st.write(review_result["initial_plan"])

            st.markdown("##### Auditor Review")
            st.info(review_result["auditor_review"])

            if review_result["refined_plan"]:
                st.markdown("##### Refined Plan")
                st.write(review_result["refined_plan"])
            else:
                st.success("Plan approved in first pass.")
        except Exception as error:
            st.error(f"Multi-agent workflow failed: {error}")

    st.markdown("---")
    st.markdown("#### LangGraph Auditor Loop (`6_langgraph_flow.py`)")
    langgraph_requirement = st.text_area(
        "Requirement for LangGraph flow:",
        value="A login system that requires MFA and SHA-256 password hashing.",
        key="langgraph_requirement"
    )

    if st.button("Run LangGraph Workflow"):
        try:
            with st.spinner("Running LangGraph workflow..."):
                langgraph_module = load_script_module("6_langgraph_flow.py", "langgraph_flow_module")
                flow_result = langgraph_module.run_langgraph_workflow(langgraph_requirement)

            st.markdown("##### Final Test Plan")
            st.write(flow_result["test_plan"])

            st.markdown("##### Auditor Feedback")
            st.info(flow_result["feedback"])

            st.markdown("##### Workflow Summary")
            st.json(
                {
                    "revisions_used": flow_result["revision_count"],
                    "auditor_decision": flow_result["auditor_decision"],
                }
            )
        except Exception as error:
            st.error(f"LangGraph workflow failed: {error}")

    if st.button("Run LangGraph + Final Audit"):
        try:
            with st.spinner("Running LangGraph and final audit..."):
                langgraph_module = load_script_module("6_langgraph_flow.py", "langgraph_flow_eval_module")
                final_eval_module = load_script_module("7_final_eval.py", "final_eval_module")
                flow_result = langgraph_module.run_langgraph_workflow(langgraph_requirement)
                audit_scores = final_eval_module.run_final_audit(
                    query=langgraph_requirement,
                    context=langgraph_requirement,
                    output=flow_result["test_plan"],
                )

            st.markdown("##### Final Test Plan")
            st.write(flow_result["test_plan"])

            st.markdown("##### Auditor Feedback")
            st.info(flow_result["feedback"])

            st.markdown("##### System Health Report")
            st.json(
                {
                    "retrieval_quality": audit_scores["retrieval_quality"],
                    "generation_honesty": audit_scores["generation_honesty"],
                    "user_satisfaction": audit_scores["user_satisfaction"],
                    "revisions_used": flow_result["revision_count"],
                    "auditor_decision": flow_result["auditor_decision"],
                }
            )
        except Exception as error:
            st.error(f"LangGraph + final audit failed: {error}")