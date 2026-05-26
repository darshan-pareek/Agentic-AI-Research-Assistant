import logging
from langgraph.graph import StateGraph, START, END

from state.graph_state import AgentState
from agents.research_agent import research_node
from agents.answer_agent import answer_node
from agents.critic_agent import critic_node

logger = logging.getLogger(__name__)

def should_continue(state: AgentState) -> str:
    score = state.get("critic_score", 0)
    revisions = state.get("revision_count", 0)
    
    logger.info(f"Routing check: Score={score}/10, Revisions={revisions}/3")
    
    if score >= 8 or revisions >= 3:
        return "end"
    return "revise"

def build_workflow():
    logger.info("Building LangGraph StateGraph...")
    
    builder = StateGraph(AgentState)
    
    builder.add_node("research_agent", research_node)
    builder.add_node("answer_agent", answer_node)
    builder.add_node("critic_agent", critic_node)
    
    builder.add_edge(START, "research_agent")
    builder.add_edge("research_agent", "answer_agent")
    builder.add_edge("answer_agent", "critic_agent")
    
    builder.add_conditional_edges(
        "critic_agent",
        should_continue,
        {
            "end": END,
            "revise": "answer_agent"
        }
    )
    
    return builder.compile()
