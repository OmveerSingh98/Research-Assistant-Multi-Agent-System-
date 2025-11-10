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
