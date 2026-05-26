import os
import logging
from typing import List, Dict, Any
from tavily import TavilyClient

logger = logging.getLogger(__name__)

def search_tavily(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web using the Tavily API.
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
        return results
        
    except Exception as e:
        logger.error(f"Tavily search failed: {e}")
        return []
