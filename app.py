from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import datetime
import logging
from Agents3 import pipeline


# Configure logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# FastAPI App Setup

app = FastAPI(
    title="Multi-Agent Research System API",
    description="FastAPI interface for the LangChain multi-agent research pipeline.",
    version="2.0"
)


# Request & Response Models

class TopicRequest(BaseModel):
    topic: str

class SummaryResponse(BaseModel):
    topic: str
    key_developments: str
    main_themes: str
    sources: List[str]
    generated_at: str


# Root Endpoint

@app.get("/")
async def root():
    return {"message": "Welcome to the Multi-Agent Research API. Use POST /research_summary"}


# Research Summary Endpoint

@app.post("/research_summary", response_model=SummaryResponse)
async def get_research_summary(request: TopicRequest):
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    try:
        logger.info(f"[API] Starting pipeline for topic: {topic}")
        result = pipeline.invoke(topic)

        # Ensure we extract clean sections
        key_dev = result.get("key_developments", "")
        main_themes = result.get("main_themes", "")
        sources = result.get("sources", [])

        return SummaryResponse(
            topic=topic,
            key_developments=key_dev,
            main_themes=main_themes,
            sources=sources,
            generated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    except Exception as e:
        logger.error(f"[API] Pipeline execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {e}")

