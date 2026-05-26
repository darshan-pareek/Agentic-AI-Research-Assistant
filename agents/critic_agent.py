import os
import logging
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from state.graph_state import AgentState
from prompts.critic_prompt import CriticEvaluation, CRITIC_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

def critic_node(state: AgentState) -> Dict[str, Any]:
    """
    Evaluates report quality and returns structured score + feedback.
    """
    logger.info("Executing critic node...")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY is not set.")
        
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=gemini_key,
        temperature=0.1
    )
    
    topic = state.get("topic", "")
    question = state.get("question", "")
    research_notes = state.get("research_notes", "")
    draft_answer = state.get("draft_answer", "")
    revision_count = state.get("revision_count", 0)
    revision_history = state.get("revision_history", []) or []
    
    structured_llm = llm.with_structured_output(CriticEvaluation)
    
    prompt = PromptTemplate.from_template(CRITIC_SYSTEM_PROMPT).format(
        topic=topic,
        question=question,
        research_notes=research_notes,
        draft_answer=draft_answer
    )
    
    try:
        evaluation = structured_llm.invoke(prompt)
        score = evaluation.score
        feedback = evaluation.feedback
    except Exception as e:
        logger.error(f"Structured output failed: {e}. Falling back.")
        score = 7
        feedback = "The draft matches basic requirements. Please add more depth."
        
    logger.info(f"Evaluation complete. Score: {score}/10")
    
    new_revision_count = revision_count + 1
    current_eval = {
        "revision_number": new_revision_count,
        "score": score,
        "feedback": feedback
    }
    
    new_history = list(revision_history)
    new_history.append(current_eval)
    
    return {
        "critic_score": score,
        "critic_feedback": feedback,
        "revision_count": new_revision_count,
        "revision_history": new_history,
        "status": f"Evaluation Completed (Score: {score})"
    }
