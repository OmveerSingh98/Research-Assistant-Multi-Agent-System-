import os
import re
import datetime
import logging
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableLambda

# ==================================
# Configure logging
# ==================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("agent_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================================
# Setup
# ==================================
load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
search_tool = DuckDuckGoSearchResults()

# ==================================
# Pydantic Models for Structure
# ==================================
class Source(BaseModel):
    title: str
    link: str

class ResearchData(BaseModel):
    topic: str
    research: str
    sources: List[Source] = []

class AnalysisData(BaseModel):
    topic: str
    analysis: str
    sources: List[Source] = []

# ==================================
# Agent 1 – Research
# ==================================
def research_agent(topic: str) -> ResearchData:
    logger.info(f"[ResearchAgent] Searching DuckDuckGo for: {topic}")
    try:
        results = search_tool.invoke(topic)
        logger.debug(f"Raw search_tool output type: {type(results)}")
        logger.debug(f"Raw search_tool output:\n{str(results)[:500]}...")  # first 500 chars

        snippets = []
        sources: List[Source] = []

        if isinstance(results, str):
            pattern = re.compile(r"title: (.*?), link: (https?://[^\s,]+)")
            for match in pattern.finditer(results):
                title, link = match.groups()
                domain_match = re.search(r"https?://(?:www\.)?([^/]+)", link)
                domain_name = domain_match.group(1) if domain_match else "Unknown Source"
                clean_title = title if title.strip() else domain_name.split(".")[0].capitalize()
                sources.append(Source(title=clean_title, link=link))
                snippets.append(f"- {title} (Source: {link})")

            research_text = "\n".join(snippets) if snippets else results
            return ResearchData(topic=topic, research=research_text, sources=sources)

        elif isinstance(results, list):
            for r in results[:5]:
                if isinstance(r, dict) and "snippet" in r and "link" in r:
                    snippet = r["snippet"]
                    link = r["link"]
                    title = r.get("title", "")
                    domain_match = re.search(r"https?://(?:www\.)?([^/]+)", link)
                    domain_name = domain_match.group(1) if domain_match else "Unknown Source"
                    clean_title = title if title.strip() else domain_name.split(".")[0].capitalize()
                    sources.append(Source(title=clean_title, link=link))
                    snippets.append(f"- {snippet} (Source: {link})")
            research_text = "\n".join(snippets)
            return ResearchData(topic=topic, research=research_text, sources=sources)

        else:
            return ResearchData(topic=topic, research="Unexpected result type.", sources=[])

    except Exception as e:
        logger.error(f"[ResearchAgent] Search failed: {e}")
        return ResearchData(topic=topic, research=f"Search failed: {e}", sources=[])

# ==================================
# Agent 2 – Analysis
# ==================================
def analysis_agent(data: ResearchData) -> AnalysisData:
    logger.info("[AnalysisAgent] Analyzing research data...")
    try:
        prompt = (
            f"Analyze the following research on '{data.topic}'. "
            f"Extract key developments, trends, and insights:\n\n{data.research}"
        )
        response = llm.invoke(prompt)
        analysis_text = getattr(response, "content", str(response))
        return AnalysisData(topic=data.topic, analysis=analysis_text, sources=data.sources)
    except Exception as e:
        logger.error(f"[AnalysisAgent] Analysis failed: {e}")
        return AnalysisData(topic=data.topic, analysis=f"Analysis failed: {e}", sources=data.sources)

# ==================================
# Agent 3 – Summary
# ==================================
def summary_agent(data: AnalysisData) -> str:
    logger.info("[SummaryAgent] Creating structured summary...")

    sources_text = (
        "\n".join([f"* **{s.title}** — {s.link}" for s in data.sources])
        if data.sources else "No valid sources available."
    )

    try:
        prompt = f"""
        You are a research summarization assistant.
        Summarize the topic '{data.topic}' based on this analysis.
        Use structured markdown with:
        - Key Developments
        - Main Themes
        - Sources (using the provided URLs)
        
        === RESEARCH SUMMARY FOR: '{data.topic}' ===
        Use these sources as reference:
        {sources_text}

        ANALYSIS:
        {data.analysis}
        """

        response = llm.invoke(prompt)
        summary_text = getattr(response, "content", str(response))  
        generated_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        summary_text += f"\n\nGenerated at: {generated_at}"

        logger.info("[SummaryAgent] Summary generation completed.")
        return summary_text

    except Exception as e:
        logger.error(f"[SummaryAgent] Summary generation failed: {e}")
        return f"Summary generation failed: {e}"

# ==================================
# Build Runnable Chain
# ==================================
pipeline = (
    RunnableLambda(research_agent)
    | RunnableLambda(analysis_agent)
    | RunnableLambda(summary_agent)
)

# ==================================
# Run the System
# ==================================
if __name__ == "__main__":
    topic = input("Enter a research topic: ").strip()
    logger.info(f"=== Starting Research Pipeline for Topic: {topic} ===")

    try:
        final_output = pipeline.invoke(topic)
        logger.info("=== FINAL OUTPUT ===")
        logger.info(f"\n{final_output}")
        print(final_output)
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
