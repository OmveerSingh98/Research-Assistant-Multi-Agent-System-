from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import wikipedia
import logging

#  Logging Setup 
logging.basicConfig(
    filename="mcp_tools.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

mcp = FastMCP("ResearchAgent")

@mcp.tool()
def search_web(query: str, max_results: int = 5):
    """Search Wikipedia for relevant information."""
    logging.info("search_web invoked with query: '%s', max_results=%d", query, max_results)
    results = []
    try:
        wikipedia.set_lang("en")
        search_results = wikipedia.search(query, results=max_results)
        logging.info("Found %d Wikipedia search results", len(search_results))
        for title in search_results:
            try:
                page = wikipedia.page(title, auto_suggest=False)
                snippet = page.summary[:500]
                results.append({
                    "title": page.title,
                    "snippet": snippet,
                    "url": page.url
                })
                logging.info("Fetched page: %s | URL: %s", page.title, page.url)
            except Exception as e:
                logging.error("Error fetching page '%s': %s", title, e)
    except Exception as e:
        logging.error("Wikipedia search error: %s", e)
    
    if not results:
        logging.warning("No results found for query '%s'", query)
        results = [{"title": query, "snippet": "No results", "url": ""}]
    
    logging.info("search_web results: %s", results)
    return results

@mcp.tool()
def analyze_snippets(snippets: list) -> dict:
    """Analyze snippets and extract key points and main themes."""
    logging.info("analyze_snippets invoked with %d snippets", len(snippets))
    key_points = [s.get("snippet", "") for s in snippets]
    # Placeholder themes; could later use an LLM to extract real themes
    main_themes = ["Theme extraction placeholder"]
    result = {"key_points": key_points, "main_themes": main_themes, "snippets": snippets}
    logging.info("analyze_snippets result: %s", result)
    return result

@mcp.tool()
def summarize_analysis(key_points: list, main_themes: list, snippets: list, topic: str) -> str:
    """Generate structured research summary."""
    logging.info("summarize_analysis invoked for topic: '%s'", topic)
    summary = f"Topic: {topic}\n=== RESEARCH SUMMARY ===\n"
    summary += "Key Developments:\n"
    for i, kp in enumerate(key_points, 1):
        summary += f"{i}. {kp}\n"
    summary += "Main Themes:\n"
    for theme in main_themes:
        summary += f"- {theme}\n"
    summary += "Sources:\n"
    for i, s in enumerate(snippets, 1):
        summary += f"- [Source {i}]: {s.get('url', 'N/A')}\n"
    summary += f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    logging.info("summarize_analysis result generated:\n%s", summary)
    return summary

if __name__ == "__main__":
    logging.info("Starting MCP FastMCP server for ResearchAgent")
    mcp.run(transport="stdio")
    logging.info("MCP FastMCP server stopped")

