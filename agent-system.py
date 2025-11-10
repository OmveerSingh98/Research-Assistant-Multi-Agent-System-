import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.messages import AIMessage, HumanMessage

import ast  # safer than eval for structured literals

#  Logging 
log_file = "research_workflow.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),  # Console
        logging.FileHandler(log_file, mode='a')  # File
    ]
)

# LLM 
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
    task="chat-completion"
    
)
model = ChatHuggingFace(llm=llm)

#  Agents 
class ResearchAgent:
    def __init__(self, tools):
        self.agent = create_agent(model, tools)

    async def run(self, topic: str):
        logging.info("Starting research for topic: %s", topic)
        prompt = f"You are the Research Agent. Use the MCP tool `search_web` to fetch top snippets and URLs for: {topic}"
        response = await self.agent.ainvoke({"messages": [HumanMessage(content=prompt)]})
        logging.info("Research completed.")
        return response

class AnalysisAgent:
    def __init__(self, tools):
        self.agent = create_agent(model, tools)

    async def run(self, snippets):
        logging.info("Starting analysis of snippets.")
        prompt = f"You are the Analysis Agent. Use the MCP tool `analyze_snippets` to extract key points and main themes from: {snippets}"
        response = await self.agent.ainvoke({"messages": [HumanMessage(content=prompt)]})
        logging.info("Analysis completed.")
        return response

class SummaryAgent:
    def __init__(self, tools):
        self.agent = create_agent(model, tools)

    async def run(self, topic, analysis, snippets):
        logging.info("Starting summary generation.")
        prompt = (
            f"You are the Summary Agent. Use the MCP tool `summarize_analysis` to generate a structured summary "
            f"for the topic '{topic}' with the analysis {analysis} and sources {snippets}. "
            f"The output MUST be a Python dictionary (JSON-like) with the following keys and types:\n\n"
            f"1. 'topic': string (the research topic)\n"
            f"2. 'key_developments': list of strings (main points from analysis)\n"
            f"3. 'main_themes': list of strings (main themes extracted from analysis)\n"
            f"4. 'sources': list of URLs only (strings), e.g., ['https://example1.com', 'https://example2.com']\n"
            f"5. 'generated_at': string in format 'YYYY-MM-DD HH:MM:SS'\n\n"
            f"Important: Only return the dictionary. DO NOT include any extra text, explanation, or quotes.\n\n"
            f"Example:\n"
            f"{{\n"
            f"  'topic': 'feminism',\n"
            f"  'key_developments': ['Point 1', 'Point 2'],\n"
            f"  'main_themes': ['Theme 1', 'Theme 2'],\n"
            f"  'sources': ['https://source1.com', 'https://source2.com'],\n"
            f"  'generated_at': '2023-02-13 12:34:56'\n"
            f"}}"
        )

        response = await self.agent.ainvoke({"messages": [HumanMessage(content=prompt)]})
        logging.info("Summary agent response received.")
        
        # Try to parse structured dict from AIMessage
        summary_dict = None
        for msg in response.get("messages", []):
            if isinstance(msg, AIMessage):
                try:
                    parsed = ast.literal_eval(msg.content)
                    if isinstance(parsed, dict):
                        summary_dict = parsed
                        break
                except Exception:
                    logging.warning("Failed to parse AIMessage content. Using fallback.")
                    continue

        # Fallback if parsing fails
        if not summary_dict:
            logging.warning("Using fallback summary due to parse failure.")
            summary_dict = {
                "topic": topic,
                "key_developments": [],
                "main_themes": [],
                "sources": [s.get("url", "N/A") if isinstance(s, dict) else str(s) for s in snippets.get("messages", [])],
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        # Extract only URLs from sources
        raw_sources = summary_dict.get("sources", [])
        urls = []
        for s in raw_sources:
            if isinstance(s, str):
                urls.append(s)
            elif isinstance(s, dict) and "url" in s:
                urls.append(s["url"])
        summary_dict["sources"] = urls

        # Add generated_at datetime
        summary_dict["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logging.info("Summary generation completed.")
        return summary_dict

#  Workflow 
async def main():
    topic = input("Enter a research topic: ").strip()
    if not topic:
        logging.error("Topic cannot be empty.")
        return

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).parent / "research-tools.py")]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)

            research_agent = ResearchAgent(tools)
            analysis_agent = AnalysisAgent(tools)
            summary_agent = SummaryAgent(tools)

            # Step 1: Research
            research_result = await research_agent.run(topic)

            # Step 2: Analysis
            analysis_result = await analysis_agent.run(research_result)

            # Step 3: Summary
            summary = await summary_agent.run(topic, analysis_result, research_result)

            # Step 4: Print nicely
        
            print(summary)
            print(f"\nTopic: {summary['topic']}")
            print("=== RESEARCH SUMMARY ===")
            print("Key Developments:")
            for i, kp in enumerate(summary['key_developments'], 1):
                print(f"{i}. {kp}")
            print("Main Themes:")
            for theme in summary['main_themes']:
                print(f"- {theme}")
            print("Sources:")
            for i, src in enumerate(summary['sources'], 1):
                print(f"- [Source {i}]: {src}")
            print(f"Generated at: {summary['generated_at']}")

            logging.info("Workflow completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())

