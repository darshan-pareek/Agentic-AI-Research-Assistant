import os
import logging
from typing import List, Dict, Any
from tavily import TavilyClient
from ddgs import DDGS

logger = logging.getLogger(__name__)

def search_tavily(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web using the Tavily API.
    and using duckduckgo as fallback if Tavily fails or returns no results.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        logger.error("TAVILY_API_KEY is not set.")
        raise ValueError("TAVILY_API_KEY missing from environment.")

    try:
        client = TavilyClient(api_key=api_key)
        logger.info(f"Searching Tavily: {query}")
        
        response = client.search(
            query=query, 
            max_results=max_results, 
            search_depth="advanced"
        )
        
        results = response.get("results", [])
        if results:
            return results
        
        logger.warning("Tavily returned no results. Falling back to DuckDuckGo.")
        
    except Exception as e:
        logger.exception(f"Tavily failed: {e}")
        logger.info("Using DuckDuckGo fallback.")

    
    # fallback to duckduckgo
    try:
        with DDGS() as ddgs:
            ddgs_results= ddgs.text(query, max_results=max_results)

        # normalize the format
        normalized = [
            {
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "content": r.get("body", "")
            }
            for r in ddgs_results
        ]

        return normalized
    except Exception as e:
        logger.exception(f"DuckDuckGo search failed: {e}")
        return []
