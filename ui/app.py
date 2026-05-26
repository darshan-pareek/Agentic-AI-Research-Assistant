import os
import sys
from pathlib import Path

# Add project root to path to resolve imports when running from subdirectories
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import requests
from dotenv import load_dotenv

from graph.workflow import build_workflow
from state.graph_state import AgentState


st.set_page_config(
    page_title="Agentic Research Assistant",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style injection
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 2rem;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    .main-banner h1 {
        color: #ffffff;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
    }
    .main-banner p {
        color: #94a3b8;
        margin-top: 0.5rem;
        font-size: 1rem;
    }
    
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .badge-approved {
        background-color: #065f46;
        color: #34d399;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-revision {
        background-color: #991b1b;
        color: #fca5a5;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .stButton>button {
        background: #3b82f6;
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 6px;
        font-weight: 600;
        transition: background 0.2s ease;
    }
    .stButton>button:hover {
        background: #2563eb;
    }
    </style>
""", unsafe_allow_html=True)

load_dotenv()
gemini_ok = bool(os.getenv("GEMINI_API_KEY") and os.getenv("GEMINI_API_KEY") != "your_gemini_api_key_here")
tavily_ok = bool(os.getenv("TAVILY_API_KEY") and os.getenv("TAVILY_API_KEY") != "your_tavily_api_key_here")

with st.sidebar:
    st.markdown("### Pipeline Settings")
    min_score = st.slider(
        "Min Score Threshold", 
        min_value=6, 
        max_value=10, 
        value=8, 
        step=1,
        help="Minimum critic score needed to accept the report."
    )
    max_revisions = st.slider(
        "Max Revision Loops", 
        min_value=1, 
        max_value=5, 
        value=3, 
        step=1,
        help="Max refinement loops to run."
    )
    
    st.divider()
    
    st.markdown("### Execution Mode")
    run_mode = st.selectbox(
        "Workflow Engine",
        ["Direct (Local)", "API Service (FastAPI Backend)"],
        help="Select whether to run the graph locally or decouple execution via our FastAPI backend."
    )
    
    st.divider()
    
    st.markdown("### API Verification")
    if gemini_ok:
        st.success("Gemini API: Connected")
    else:
        st.error("Gemini API: Missing Key")
        
    if tavily_ok:
        st.success("Tavily API: Connected")
    else:
        st.error("Tavily API: Missing Key")

# Header section
st.markdown("""
    <div class="main-banner">
        <h1>Agentic Research Assistant</h1>
        <p>A multi-agent research synthesis tool powered by LangGraph, Tavily Search, and Google Gemini.</p>
    </div>
""", unsafe_allow_html=True)

col_inputs, col_visual = st.columns([2, 1])

with col_inputs:
    st.markdown("### Research Configuration")
    topic = st.text_input(
        "Research Topic", 
        value="Quantum Computing",
        placeholder="E.g., Agentic AI, Quantum Computing..."
    )
    question = st.text_area(
        "Research Question", 
        value="What is quantum supremacy and what are the major milestones achieved by Google and IBM in this space?",
        placeholder="Enter the specific research prompt..."
    )
    detailed_prompt = st.text_area(
        "Style Guidelines (Optional)", 
        value="Focus on architectural achievements and qubit metrics. Include a summary table of achievements.",
        placeholder="E.g., academic tone, focus on code examples..."
    )

with col_visual:
    st.markdown("### System Architecture")
    st.markdown("""
    The execution flow runs through three cooperative nodes:
    1. **Research Agent**: Collects search details from Tavily and structures fact notes.
    2. **Answer Agent**: Drafts the markdown technical report.
    3. **Critic Agent**: Audits notes vs draft, assigns 1-10 score. Routes back for revisions if below threshold.
    """)
    st.markdown("""
    ```
      [START] ──► [Research Agent] ──► [Answer Agent]
                                            │
                                            ▼
      [END] ◄── [Score >= Threshold?] ◄── [Critic]
                       │ (No)
                       ▼
                 [Answer Agent] (Revision)
    ```
    """)

st.divider()
start_research = st.button("Start Research Pipeline", use_container_width=True)

if start_research:
    if not (gemini_ok and tavily_ok):
        st.error("Missing API key configurations in .env file.")
    elif not topic or not question:
        st.warning("Please fill out the Topic and Question inputs.")
    else:
        if run_mode == "API Service (FastAPI Backend)":
            try:
                with st.spinner("Requesting research synthesis from FastAPI backend..."):
                    response = requests.post(
                        "http://127.0.0.1:8000/research",
                        json={
                            "topic": topic,
                            "question": question,
                            "detailed_prompt": detailed_prompt
                        }
                    )
                    
                    if response.status_code == 200:
                        st.success("API Response Received Successfully.")
                        st.session_state["results"] = response.json()
                    else:
                        st.error(f"API Backend Error ({response.status_code}): {response.text}")
                        
            except Exception as e:
                st.error(f"Failed to connect to FastAPI: {e}")
                st.info("Ensure server.py is running on http://127.0.0.1:8000")
        else:
            # Direct (Local) Graph stream execution
            try:
                workflow_graph = build_workflow()
                
                initial_state = {
                    "topic": topic,
                    "question": question,
                    "detailed_prompt": detailed_prompt,
                    "search_queries": [],
                    "raw_research_results": [],
                    "research_notes": "",
                    "draft_answer": "",
                    "critic_score": 0,
                    "critic_feedback": "",
                    "revision_count": 0,
                    "revision_history": [],
                    "sources": [],
                    "status": "Initializing workflow..."
                }
                
                st.markdown("### Research Execution Trace")
                
                with st.status("Running multi-agent pipeline...", expanded=True) as status_box:
                    final_state = initial_state
                    
                    for event in workflow_graph.stream(initial_state, stream_mode="updates"):
                        for node_name, state_updates in event.items():
                            final_state.update(state_updates)
                            
                            if node_name == "research_agent":
                                st.write("✓ **Research Agent**: Analyzed query and generated search queries.")
                                st.caption(f"Queries used: `{', '.join(state_updates.get('search_queries', []))}`")
                                st.write(f"✓ **Research Agent**: Collected data from {len(state_updates.get('sources', []))} sources.")
                                
                            elif node_name == "answer_agent":
                                rev_c = final_state.get('revision_count', 0)
                                if rev_c > 0:
                                    st.write(f"✓ **Answer Agent**: Completed revision #{rev_c}.")
                                else:
                                    st.write("✓ **Answer Agent**: Drafted initial report.")
                                    
                            elif node_name == "critic_agent":
                                score = state_updates.get("critic_score", 0)
                                feedback = state_updates.get("critic_feedback", "")
                                st.write(f"✓ **Critic Agent**: Finished evaluation. Score: **{score}/10**")
                                if score >= min_score:
                                    st.success(f"Report approved (Score: {score} >= {min_score})")
                                else:
                                    st.warning(f"Revision required (Score: {score} < {min_score}). Loop back to Answer Agent.")
                                    with st.expander("Feedback Details"):
                                        st.write(feedback)
                                        
                    final_state = workflow_graph.invoke(initial_state)
                    status_box.update(label="Workflow Finished", state="complete", expanded=False)
                
                st.session_state["results"] = final_state
                
            except Exception as e:
                st.error(f"Pipeline error: {e}")
                import traceback
                st.code(traceback.format_exc(), language="python")

if "results" in st.session_state:
    results = st.session_state["results"]
    
    final_report = results.get("draft_answer", "")
    sources_used = results.get("sources", [])
    research_notes = results.get("research_notes", "")
    final_score = results.get("critic_score", 0)
    history = results.get("revision_history", [])
    queries = results.get("search_queries", [])
    
    st.divider()
    st.markdown("## Results & Review Logs")
    
    col_score, col_rev, col_sources = st.columns(3)
    with col_score:
        score_class = "badge-approved" if final_score >= min_score else "badge-revision"
        st.markdown(f"""
            <div class="metric-card">
                <span style="color:#94a3b8; font-size:0.85rem; font-weight:500;">CRITIC SCORE</span>
                <h2 style="margin: 5px 0; color:#fff;">{final_score} / 10</h2>
                <span class="{score_class}">{"Approved" if final_score >= min_score else "Needs Revision"}</span>
            </div>
        """, unsafe_allow_html=True)
    with col_rev:
        st.markdown(f"""
            <div class="metric-card">
                <span style="color:#94a3b8; font-size:0.85rem; font-weight:500;">REVISIONS MADE</span>
                <h2 style="margin: 5px 0; color:#fff;">{results.get('revision_count', 0)} / {max_revisions}</h2>
                <span style="color:#3b82f6; font-size:0.85rem; font-weight:500;">Loops executed</span>
            </div>
        """, unsafe_allow_html=True)
    with col_sources:
        st.markdown(f"""
            <div class="metric-card">
                <span style="color:#94a3b8; font-size:0.85rem; font-weight:500;">WEB SOURCES</span>
                <h2 style="margin: 5px 0; color:#fff;">{len(sources_used)}</h2>
                <span style="color:#a855f7; font-size:0.85rem; font-weight:500;">Unique links analyzed</span>
            </div>
        """, unsafe_allow_html=True)
        
    tab_report, tab_notes, tab_history, tab_sources = st.tabs([
        "Report Output", 
        "Research Notes", 
        "Evaluation History", 
        "Sources"
    ])
    
    with tab_report:
        st.markdown(final_report)
        st.divider()
        st.download_button(
            label="Download Markdown Report",
            data=final_report,
            file_name=f"report_{topic.lower().replace(' ', '_')}.md",
            mime="text/markdown"
        )
        
    with tab_notes:
        st.markdown("### Raw Note Synthesis")
        st.markdown(research_notes)
        
    with tab_history:
        st.markdown("### Evaluation Loop History")
        
        st.write("**Queries searched:**")
        for idx, q in enumerate(queries):
            st.markdown(f"{idx+1}. `{q}`")
            
        st.divider()
        
        st.markdown("### Audit History")
        for step in history:
            num = step.get("revision_number", 1)
            sc = step.get("score", 0)
            fb = step.get("feedback", "")
            badge = "Approved" if sc >= min_score else "Needs Revision"
            st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin:0 0 10px 0; color:#fff;">Loop #{num} (Score: {sc}/10 - {badge})</h4>
                    <p style="color:#cbd5e1; font-size:0.9rem; margin:0;"><strong>Feedback:</strong> {fb}</p>
                </div>
            """, unsafe_allow_html=True)
            
    with tab_sources:
        st.markdown("### Referenced URLs")
        for idx, url in enumerate(sources_used):
            st.markdown(f"**[{idx+1}]** [{url}]({url})")
