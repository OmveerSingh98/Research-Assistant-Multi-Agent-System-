# Research-Assistant-Multi-Agent-System-
**METHOD_2: With using MCP**

## Architechture Diagram
+---------------------------------------------------------------+
|                        agent-system.py                        |
| (Main Orchestrator - Coordinates Agents via LangChain + MCP)  |
|                                                               |
|  +-------------------+     +-------------------+               |
|  | Research Agent    | --> |  Analysis Agent   | --> Summary   |
|  | (search_web tool) |     | (analyze_snippets)|     Agent     |
|  +-------------------+     +-------------------+  (summarize)  |
|                                                               |
|  Each agent communicates with MCP tools via FastMCP server.   |
+---------------------------------------------------------------+
                 |                                    
                 | stdio transport (MCP protocol)      
                 v                                    
+---------------------------------------------------------------+
|                     research-tools.py                         |
| (MCP FastMCP Server exposing tools for ResearchAgent)         |
|                                                               |
|   • search_web() -> Fetches Wikipedia info                    |
|   • analyze_snippets() -> Extracts key points                 |
|   • summarize_analysis() -> Builds structured summary         |
+---------------------------------------------------------------+


## HOW IT WORKS / AGENTS COMMUNICATION
1. agent-system.py launches the MCP FastMCP server (research-tools.py) using stdio transport — enabling tool-based communication between agents and the MCP server.
2. The server exposes tools (search_web, analyze_snippets, summarize_analysis) which are automatically loaded by the LangChain load_mcp_tools() adapter.
3. The Research Agent invokes search_web() through the MCP layer to fetch relevant Wikipedia snippets and URLs about the given topic.
4. The Analysis Agent processes the snippets by calling analyze_snippets() — extracting key insights and identifying main themes.
5. The Summary Agent uses summarize_analysis() to compile all findings into a structured, timestamped research summary.
6. All agent-to-tool communication happens via serialized JSON messages over MCP’s stdio transport — ensuring modular and language-agnostic integration.
7. The orchestrator aggregates the outputs and presents a clean JSON-formatted summary containing key developments, main themes, and source URLs.

## Setup_Instructions
1. Create & activate a virtualenv (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate    # macOS/Linux
   venv\Scripts\activate       # Windows

2. Install dependencies
   pip install -r requirements.txt
   
3. Create .env and add your API key(s) / credentials

4. Run the application using command "python agent-system.py"

5. Enter the topic name in the terminal when prompted.

6. Logs will be generated as:  research_workflow.log → logs for agents & orchestration mcp_tools.log → logs for the FastMCP server tools
