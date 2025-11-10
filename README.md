# Research-Assistant-Multi-Agent-System-
Research assistant multi-agent system collaborates to research a topic, gather information, and produce a structured summary. The user provides a topic, and the system autonomously coordinates between agents to deliver results. 

ARCHITECTURE DIAGRAM
                      ┌────────────────────────────┐
                      │         Client / UI        │
                      │  (curl / Postman / Front)  │
                      └──────────────┬─────────────┘
                                     │  (POST /research_summary)
                                     ▼
                       ┌──────────────────────────┐
                       │        FastAPI App       │
                       │         (app.py)         │
                       └──────────────┬───────────┘
                                      │
                                      ▼
               ┌──────────────────────────────────────────────┐
               │              Multi-Agent Pipeline             │
               │                 (Agents3.py)                   │
               ├──────────────────────────────────────────────┤
               │   Research Agent  -> Analysis Agent -> Summary│
               │   (DuckDuckGo)      (Gemini)       (Gemini)  │
               └──────────────────────────────────────────────┘
                                      │
                                      ▼
                          ┌──────────────────────────┐
                          │   JSON Response to API   │
                          │ { topic, key_devs, ... } │
                          └──────────────────────────┘

## HOW IT WORKS / AGENTS COMMUNICATION

1. FastAPI receives a `POST` with `{ "topic": "..." }`.
2. `app.py` calls `pipeline.invoke(topic)` (a RunnableLambda chain).
3. The pipeline which is created using Agents3.py runs three agents in order, pydantic is used to generate structured output for the agents:
   - research_agent(topic) — uses `DuckDuckGoSearchResults` websearch to gather raw search output and extracts URLs into      `ResearchData.sources`.
   - analysis_agent(ResearchData) — sends the research text to Gemini (`ChatGoogleGenerativeAI`) to extract trends/insights, returns `AnalysisData`.
   - summary_agent(AnalysisData) — prompts Gemini to return a strict JSON object with `key_developments`, `main_themes`, and `sources`. The agent also merges model-provided sources with research-derived links and returns a final dict.
4. `app.py` returns a clean JSON response with `topic`, `key_developments`, `main_themes`, `sources`, `generated_at`.
5. Communication between agents is via typed Python objects (`ResearchData`, `AnalysisData`) passed along the RunnableLambda chain.
6. Each agent writes detailed logs (start, success, and error events) into both the console and a agent_pipeline.log file.

## SETUP_INSTRUCTIONS

1. Create & activate a virtualenv (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate    # macOS/Linux
   venv\Scripts\activate       # Windows

2. Install dependencies
   pip install -r requirements.txt
   
3. Create .env and add your Google API key(s) / credentials

4. Run the app
   command: uvicorn app:app --reload
   Open: http://127.0.0.1:8000/docs for Swagger UI
   <img width="944" height="263" alt="image" src="https://github.com/user-attachments/assets/5059b413-a816-4e75-b62c-2faa069ac5fb" />

5. Hit the expand button as shown in red box
   <img width="926" height="55" alt="image" src="https://github.com/user-attachments/assets/bbed9a9c-7cea-4c92-b142-77f11fe9b4d1" />

6. Add your topic and Hit the execute button
   <img width="882" height="344" alt="image" src="https://github.com/user-attachments/assets/fdd8b905-f726-4285-8ba4-b56253d51c64" />
   
7. Scroll down to see output in the response body.
   <img width="892" height="325" alt="image" src="https://github.com/user-attachments/assets/d2d8de9f-28a8-47f5-8831-6678c8df0cb2" />

8. **To directly see the output in the console directly run Agents.py after step 3**



    
