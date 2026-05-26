import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from graph.workflow import build_workflow
from utils.helpers import verify_environment, setup_logging

setup_logging()

if not verify_environment():
    print("Warning: Missing environment configurations.")

app = FastAPI(
    title="Agentic Research API",
    description="Backend API exposing the LangGraph multi-agent research pipeline",
    version="1.0.0"
)

# CORS middleware for potential frontend cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared graph is built once on startup
workflow = build_workflow()

class ResearchRequest(BaseModel):
    topic: str = Field(..., example="Quantum Computing")
    question: str = Field(..., example="What are the recent milestones in quantum supremacy?")
    detailed_prompt: Optional[str] = Field(default="", example="Write in an academic tone.")

class ResearchResponse(BaseModel):
    topic: str
    question: str
    draft_answer: str
    sources: List[str]
    critic_score: int
    critic_feedback: str
    revision_count: int
    revision_history: List[Dict[str, Any]]
    search_queries: List[str]
    status: str

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/research", response_model=ResearchResponse)
def execute_research(request: ResearchRequest):
    initial_state = {
        "topic": request.topic,
        "question": request.question,
        "detailed_prompt": request.detailed_prompt,
        "search_queries": [],
        "raw_research_results": [],
        "research_notes": "",
        "draft_answer": "",
        "critic_score": 0,
        "critic_feedback": "",
        "revision_count": 0,
        "revision_history": [],
        "sources": [],
        "status": "Starting workflow"
    }

    try:
        final_state = workflow.invoke(initial_state)
        
        # Ensure we return valid fields matching the Response schema
        return ResearchResponse(
            topic=final_state.get("topic", ""),
            question=final_state.get("question", ""),
            draft_answer=final_state.get("draft_answer", ""),
            sources=final_state.get("sources", []),
            critic_score=final_state.get("critic_score", 0),
            critic_feedback=final_state.get("critic_feedback", ""),
            revision_count=final_state.get("revision_count", 0),
            revision_history=final_state.get("revision_history", []),
            search_queries=final_state.get("search_queries", []),
            status=final_state.get("status", "Completed")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Default local dev port
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
