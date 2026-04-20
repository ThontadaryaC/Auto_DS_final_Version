from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
import time

def research_industry_context(domain_query: str, max_results: int = 3) -> str:
    """
    Searches DuckDuckGo for industry context and extracts snippets.
    """
    print(f"Researching industry context for: {domain_query}")
    results_text = []
    
    try:
        with DDGS() as ddgs:
            # text(query, region, safesearch, timelimit, backend)
            results = list(ddgs.text(domain_query, max_results=max_results))
            
            for i, r in enumerate(results):
                title = r.get('title', 'No Title')
                snippet = r.get('body', '')
                href = r.get('href', '#')
                
                # Append basic results
                results_text.append(f"Source {i+1}: {title}\nSummary: {snippet}\nURL: {href}\n")
                
                # Optionally try to scrape a bit more from the page if snippet is too short
                # But for speed, we stick to body for now as requested top 3 for speed.
                
        if not results_text:
            return "No recent industry context found via web search."
            
        return "\n".join(results_text)
        
    except Exception as e:
        print(f"Web research failed: {e}")
        return "Industry web research was unavailable at this time."

if __name__ == "__main__":
    # Test
    print(research_industry_context("Recent trends in global semiconductor industry 2024"))
