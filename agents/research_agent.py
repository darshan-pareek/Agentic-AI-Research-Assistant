import os
import re
import logging
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from state.graph_state import AgentState
from tools.tavily_tool import search_tavily
from prompts.research_prompt import QUERY_GENERATION_TEMPLATE, RESEARCH_EXTRACTION_TEMPLATE

logger = logging.getLogger(__name__)

def research_node(state: AgentState) -> Dict[str, Any]:
    """
    Analyzes user query, runs targeted web searches, and builds a synthesized notes summary.
    """
    logger.info("Executing research node...")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY is not set.")
        
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=gemini_key,
        temperature=0.2
    )
    
    topic = state.get("topic", "")
    question = state.get("question", "")
    detailed_prompt = state.get("detailed_prompt", "") or "No additional instructions."
    
    # Generate search queries
    query_prompt = PromptTemplate.from_template(QUERY_GENERATION_TEMPLATE).format(
        topic=topic,
        question=question,
        detailed_prompt=detailed_prompt
    )
    query_response = llm.invoke(query_prompt)
    
    # Parse queries from output (look for numbered list or plain lines)
    queries = []
    for line in query_response.content.strip().split("\n"):
        match = re.match(r"^\d+[\s\.\)-]+(.*)", line.strip())
        if match:
            queries.append(match.group(1).strip())
        elif line.strip() and len(line.strip()) > 5 and not line.strip().startswith("Here"):
            queries.append(line.strip())
            
    queries = queries[:3]
    if not queries:
        queries = [f"{topic} {question}"]
        
    logger.info(f"Target queries generated: {queries}")
    
    # Run Tavily search queries
    all_results = []
    unique_sources = set()
    source_links = []
    
    for q in queries:
        results = search_tavily(q, max_results=3)
        for r in results:
            url = r.get("url")
            if url and url not in unique_sources:
                unique_sources.add(url)
                source_links.append(url)
                all_results.append({
                    "title": r.get("title", "Untitled"),
                    "url": url,
                    "content": r.get("content", "")
                })
                
    logger.info(f"Retrieved {len(all_results)} search results.")
    
    # Format snippets for prompt
    formatted_raw_results = ""
    for idx, r in enumerate(all_results):
        formatted_raw_results += f"[{idx+1}] Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content']}\n\n"
        
    # Extract clean notes
    notes_prompt = PromptTemplate.from_template(RESEARCH_EXTRACTION_TEMPLATE).format(
        topic=topic,
        question=question,
        raw_results=formatted_raw_results
    )
    notes_response = llm.invoke(notes_prompt)
    
    logger.info("Research synthesis complete.")
    
    return {
        "search_queries": queries,
        "raw_research_results": all_results,
        "research_notes": notes_response.content,
        "sources": source_links,
        "status": "Research Completed"
    }
