import os
import sys
import logging
from dotenv import load_dotenv

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

def verify_environment():
    load_dotenv()
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    missing = []
    if not gemini_key or gemini_key == "your_gemini_api_key_here":
        missing.append("GEMINI_API_KEY")
    if not tavily_key or tavily_key == "your_tavily_api_key_here":
        missing.append("TAVILY_API_KEY")
        
    if missing:
        print("\n" + "="*50)
        print("MISSING CONFIGURATION:")
        for key in missing:
            print(f" - {key}")
        print("Please configure these in your .env file.")
        print("="*50 + "\n")
        return False
        
    return True

def print_agent_update(state: dict, node_name: str):
    print(f"\n>>> State Update: {node_name}")
    
    if node_name == "research_agent":
        print(f"Queries: {state.get('search_queries', [])}")
        print(f"Sources gathered: {len(state.get('sources', []))}")
        notes = state.get("research_notes", "")
        if notes:
            print(f"Notes extract preview:\n{notes[:200]}...")
            
    elif node_name == "answer_agent":
        draft = state.get("draft_answer", "")
        if draft:
            print(f"Draft report preview:\n{draft[:200]}...")
            
    elif node_name == "critic_agent":
        print(f"Critic Score: {state.get('critic_score', 0)}/10")
        print(f"Critic Feedback: {state.get('critic_feedback', '')}")
        print(f"Revision Count: {state.get('revision_count', 0)}")
    print("-" * 40)
