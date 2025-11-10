import os
import re
import datetime
import logging
import json
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableLambda


# Configure logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("agent_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Setup

load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
search_tool = DuckDuckGoSearchResults()


# Pydantic Models for Structure

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


# Agent 1 – Research

def research_agent(topic: str) -> ResearchData:
    logger.info(f"[ResearchAgent] Searching DuckDuckGo for: {topic}")
    try:
        results = search_tool.invoke(topic)
        snippets = []
        sources: List[Source] = []

        # Handle string output format (most recent LangChain versions)
        if isinstance(results, str):
            # Extract any "title" and "https://" patterns
            link_matches = re.findall(r"(https?://[^\s\)\]]+)", results)
            for idx, link in enumerate(link_matches[:5]):
                sources.append(Source(title=f"Source {idx+1}", link=link))
                snippets.append(f"- Reference link: {link}")

            research_text = results[:3000]  # truncate long output for LLM safety
            return ResearchData(topic=topic, research=research_text, sources=sources)

        # Handle dict/list structure if DuckDuckGo ever returns it
        elif isinstance(results, list):
            for r in results[:5]:
                if isinstance(r, dict) and "link" in r:
                    sources.append(Source(title=r.get("title", "Untitled"), link=r["link"]))
                    snippets.append(f"- {r.get('snippet', '')} (Source: {r['link']})")
            research_text = "\n".join(snippets)
            return ResearchData(topic=topic, research=research_text, sources=sources)

        else:
            return ResearchData(topic=topic, research=str(results), sources=[])

    except Exception as e:
        logger.error(f"[ResearchAgent] Search failed: {e}")
        return ResearchData(topic=topic, research=f"Search failed: {e}", sources=[])



# Agent 2 – Analysis

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


# Agent 3 – Summary (Improved JSON Parsing)

def summary_agent(data: AnalysisData) -> dict:
    """
    Generate structured JSON summary with separate key_developments, main_themes, and sources.
    Always includes sources from the research stage, even if LLM output omits them.
    """
    logger.info("[SummaryAgent] Creating structured summary...")

    # Clean and validate source URLs from data.sources
    extracted_sources = [s.link for s in data.sources if s.link.startswith("http")]
    if not extracted_sources:
        logger.warning("[SummaryAgent] No valid sources found in data.sources.")
        extracted_sources = []

    sources_text = (
        "\n".join([f"* **{s.title}** — {s.link}" for s in data.sources])
        if data.sources else "No valid sources available."
    )

    prompt = f"""
    You are a research summarization assistant.
    Summarize the topic '{data.topic}' based on this analysis.
    Return output ONLY in valid JSON with these exact keys:
    {{
        "key_developments": "...",
        "main_themes": "...",
        "sources": ["url1", "url2", ...]
    }}

    Do NOT include Markdown fences or extra commentary.

    Sources to reference:
    {sources_text}

    ANALYSIS:
    {data.analysis}
    """

    try:
        response = llm.invoke(prompt)
        summary_content = getattr(response, "content", str(response)).strip()

        # Clean markdown wrappers (```json etc.)
        summary_content = summary_content.replace("```json", "").replace("```", "").strip()

        import json
        try:
            summary_dict = json.loads(summary_content)
        except json.JSONDecodeError:
            logger.warning("[SummaryAgent] LLM did not return valid JSON. Using fallback parsing.")
            summary_dict = {"key_developments": summary_content, "main_themes": "", "sources": []}

        # Ensure proper fields exist
        key_dev = summary_dict.get("key_developments", "").strip()
        main_themes = summary_dict.get("main_themes", "").strip()

        # Try to recover any source URLs from LLM text if missing
        llm_sources = summary_dict.get("sources", [])
        if isinstance(llm_sources, str):
            llm_sources = re.findall(r"https?://[^\s\"']+", llm_sources)

        # Combine and deduplicate
        final_sources = sorted(set(extracted_sources + llm_sources))

        summary_dict = {
            "key_developments": key_dev,
            "main_themes": main_themes,
            "sources": final_sources
        }

        logger.info(f"[SummaryAgent] Summary complete with {len(final_sources)} sources.")
        return summary_dict

    except Exception as e:
        logger.error(f"[SummaryAgent] Summary generation failed: {e}")
        return {
            "key_developments": f"Summary generation failed: {e}",
            "main_themes": "",
            "sources": extracted_sources
        }




# Build Runnable Chain

pipeline = (
    RunnableLambda(research_agent)
    | RunnableLambda(analysis_agent)
    | RunnableLambda(summary_agent)
)

