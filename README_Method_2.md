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
