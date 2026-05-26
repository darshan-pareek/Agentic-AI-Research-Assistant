from typing import List, Dict, Any
from typing_extensions import TypedDict

class AgentState(TypedDict):
    """
    Shared state schema for the research assistant graph.
    """
    topic: str
    question: str
    detailed_prompt: str
    
    search_queries: List[str]
    raw_research_results: List[Dict[str, Any]]
    research_notes: str
    sources: List[str]
    
    draft_answer: str
    
    critic_score: int
    critic_feedback: str
    revision_count: int
    revision_history: List[Dict[str, Any]]
    
    status: str
