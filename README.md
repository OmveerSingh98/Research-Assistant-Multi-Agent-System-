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
               │                 (Agents.py)                   │
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
SETUP_INSTRUCTIONS
1.## Setup Instructions

1. Create & activate a virtualenv (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate    
   venv\Scripts\activate       
