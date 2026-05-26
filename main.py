import argparse
import sys

from utils.helpers import setup_logging, verify_environment, print_agent_update
from graph.workflow import build_workflow

def run_cli():
    setup_logging()
    if not verify_environment():
        print("Error: Environment check failed. Make sure your .env file is set up correctly.")
        sys.exit(1)
        
    parser = argparse.ArgumentParser(description="Multi-Agent Research Assistant (LangGraph)")
    parser.add_argument("--topic", type=str, required=True, help="Topic of research")
    parser.add_argument("--question", type=str, required=True, help="Specific question to answer")
    parser.add_argument("--prompt", type=str, default="", help="Additional style guidelines")
    
    args = parser.parse_args()
    
    graph = build_workflow()
    
    initial_state = {
        "topic": args.topic,
        "question": args.question,
        "detailed_prompt": args.prompt,
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
    
    print("\n" + "=" * 60)
    print("STARTING GRAPH RUN")
    print(f"Topic: {args.topic}")
    print(f"Question: {args.question}")
    print("=" * 60 + "\n")
    
    try:
        # Stream updates from the workflow nodes
        for event in graph.stream(initial_state, stream_mode="updates"):
            for node_name, state_updates in event.items():
                print_agent_update(state_updates, node_name)
                
        # Get the final completed state
        final_state = graph.invoke(initial_state)
        
        print("\n" + "=" * 60)
        print("WORKFLOW COMPLETED")
        print(f"Critic Score: {final_state.get('critic_score', 0)}/10")
        print(f"Revisions: {final_state.get('revision_count', 0)}")
        print(f"Total Sources: {len(final_state.get('sources', []))}")
        print("=" * 60 + "\n")
        
        print("FINAL COMPILED REPORT:")
        print("-" * 50)
        print(final_state.get("draft_answer", "No draft answer available."))
        print("-" * 50 + "\n")
        
        print("CITED SOURCES:")
        for idx, url in enumerate(final_state.get("sources", [])):
            print(f" [{idx+1}] {url}")
            
    except Exception as e:
        print(f"\nWorkflow error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_cli()
