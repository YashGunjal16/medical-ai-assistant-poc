import os
from typing import Dict, List, Any
import requests
from app.utils.logger import log_retrieval_attempt


class WebSearchTool:
    """Web search tool for queries requiring current information"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY", "")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
    
    def search(self, query: str, max_results: int = 3) -> Dict[str, Any]:
        """Perform web search using Google Custom Search API"""
        
        if not self.api_key or not self.search_engine_id:
            log_retrieval_attempt("web_search", query, False, "google_custom_search")
            return {
                "success": False,
                "results": [],
                "message": "Web search not configured. API keys missing.",
                "error": "SEARCH_NOT_CONFIGURED"
            }
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "q": query,
                "key": self.api_key,
                "cx": self.search_engine_id,
                "num": max_results
            }
            
            log_retrieval_attempt("web_search", query, False, "google_custom_search")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if "items" in data:
                for item in data["items"]:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", "")
                    })
            
            log_retrieval_attempt("web_search", query, len(results) > 0, "google_custom_search")
            
            return {
                "success": True,
                "results": results,
                "message": f"Found {len(results)} web results"
            }
        
        except Exception as e:
            log_retrieval_attempt("web_search", query, False, "google_custom_search")
            return {
                "success": False,
                "results": [],
                "message": f"Web search error: {str(e)}",
                "error": "SEARCH_ERROR"
            }
    
    def search_pubmed(self, query: str, max_results: int = 3) -> Dict[str, Any]:
        """Search PubMed for medical research"""
        try:
            url = "https://pubmed.ncbi.nlm.nih.gov/api/search"
            params = {
                "term": query,
                "format": "json",
                "max": max_results
            }
            
            log_retrieval_attempt("web_search", f"pubmed: {query}", False, "pubmed_api")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if "result" in data and "uids" in data["result"]:
                for uid in data["result"]["uids"][:max_results]:
                    results.append({
                        "pubmed_id": uid,
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"
                    })
            
            log_retrieval_attempt("web_search", f"pubmed: {query}", len(results) > 0, "pubmed_api")
            return {
                "success": True,
                "results": results,
                "message": f"Found {len(results)} PubMed articles"
            }
        
        except Exception as e:
            log_retrieval_attempt("web_search", f"pubmed: {query}", False, "pubmed_api")
            return {
                "success": False,
                "results": [],
                "message": f"PubMed search error: {str(e)}",
                "error": "PUBMED_SEARCH_ERROR"
            }
