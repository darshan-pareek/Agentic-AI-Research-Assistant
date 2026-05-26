import os
import logging
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from state.graph_state import AgentState
from prompts.answer_prompt import ANSWER_GENERATION_TEMPLATE, ANSWER_REVISION_TEMPLATE

logger = logging.getLogger(__name__)

def answer_node(state: AgentState) -> Dict[str, Any]:
    """
    Builds the technical report, either drafting from scratch or incorporating critic feedback.
    """
    logger.info("Executing answer node...")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY is not set.")
        
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=gemini_key,
        temperature=0.3
    )
    
    topic = state.get("topic", "")
    question = state.get("question", "")
    detailed_prompt = state.get("detailed_prompt", "") or "No additional instructions."
    research_notes = state.get("research_notes", "")
    
    original_draft = state.get("draft_answer", "")
    critic_score = state.get("critic_score")
    critic_feedback = state.get("critic_feedback", "")
    
    # Decide if generating or revising
    if original_draft and critic_score is not None:
        logger.info(f"Revising draft. Previous score: {critic_score}")
        prompt = PromptTemplate.from_template(ANSWER_REVISION_TEMPLATE).format(
            topic=topic,
            question=question,
            original_draft=original_draft,
            critic_score=critic_score,
            critic_feedback=critic_feedback,
            research_notes=research_notes
        )
        status_msg = f"Revision #{state.get('revision_count', 0) + 1} completed"
    else:
        logger.info("Generating first draft report...")
        prompt = PromptTemplate.from_template(ANSWER_GENERATION_TEMPLATE).format(
            topic=topic,
            question=question,
            detailed_prompt=detailed_prompt,
            research_notes=research_notes
        )
        status_msg = "First Draft Completed"
        
    response = llm.invoke(prompt)
    logger.info("Report drafted.")
    
    return {
        "draft_answer": response.content,
        "status": status_msg
    }
