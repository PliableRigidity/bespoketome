import requests
import xml.etree.ElementTree as ET
import asyncio
import os
import shutil
from config import USE_ARXIV_MCP, ARXIV_MCP_COMMAND, ARXIV_MCP_ARGS

# MCP Imports
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

# Fallback function (Original Implementation)
def _search_arxiv_api(query: str, max_results: int = 5) -> str:
    """Fallback: Standard ArXiv API search"""
    base_url = "http://export.arxiv.org/api/query"
    query = query.replace(" ", "+")
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate", # Changed from relevance to submittedDate
        "sortOrder": "descending"
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=15)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('atom:entry', ns)
        
        if not entries:
            return "I couldn't find any papers matching that query via API."
            
        result_text = f"Here are the latest {len(entries)} ArXiv papers for '{query.replace('+', ' ')}':\n\n"
        for i, entry in enumerate(entries):
            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
            summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
            published = entry.find('atom:published', ns).text[:10]
            link = entry.find('atom:id', ns).text
            
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns).text
                authors.append(name)
            author_str = ", ".join(authors[:3])
            if len(authors) > 3:
                author_str += " et al."
                
            result_text += f"**{i+1}. {title}**\n"
            result_text += f"*Authors:* {author_str} ({published})\n"
            result_text += f"*Link:* {link}\n"
            result_text += f"*Summary:* {summary[:300]}...\n\n"
            
        return result_text
    except Exception as e:
        return f"Error searching ArXiv API: {str(e)}"

async def _mcp_search(query: str, max_results: int = 5) -> str:
    """Search using MCP Server"""
    # Check if docker is available
    docker_path = shutil.which("docker")
    if not docker_path:
        return "Docker not found. Cannot run MCP server."

    server_params = StdioServerParameters(
        command=ARXIV_MCP_COMMAND[0], # "docker"
        args=ARXIV_MCP_ARGS,
        env=None
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # List tools to find the search tool
                tools_result = await session.list_tools()
                search_tool = None
                for tool in tools_result.tools:
                    if "search" in tool.name: # Usually "arxiv_search" or "search"
                        search_tool = tool.name
                        break
                
                if not search_tool:
                    return "Could not find a search tool in the ArXiv MCP server."
                
                # Call tool
                # Try to pass sort criteria if supported, otherwise just query
                # We attempt to hint sorting in the query itself if the tool is smart,
                # or pass common args. 
                arguments = {"query": query, "max_results": max_results}
                
                # Optimistically try to pass sort params (may be ignored if not supported)
                arguments["sort_by"] = "submittedDate"
                arguments["sort_order"] = "descending"

                result = await session.call_tool(
                    search_tool,
                    arguments=arguments
                )
                
                # Format result
                # MCP results are list of content blocks (TextContent or ImageContent)
                output_text = f"Results from ArXiv MCP for '{query}':\n\n"
                
                has_content = False
                for content in result.content:
                    if content.type == "text":
                        output_text += content.text + "\n"
                        has_content = True
                
                if not has_content:
                    return "No text content returned from MCP server."
                    
                return output_text

    except Exception as e:
        return f"MCP connection failed: {e}. Is the Docker image 'ghcr.io/modelcontextprotocol/servers/arxiv:latest' pulled?"


def search_arxiv(query: str, max_results: int = 5) -> str:
    """
    Search ArXiv for academic papers.
    Uses MCP if configured, otherwise falls back to direct API.
    """
    if USE_ARXIV_MCP and HAS_MCP:
        try:
            # Run async function in sync context
            return asyncio.run(_mcp_search(query, max_results))
        except Exception as e:
            # Fallback if MCP fails (e.g. docker not running)
            print(f"MCP Search failed ({e}), falling back to API.")
            return _search_arxiv_api(query, max_results)
    
    return _search_arxiv_api(query, max_results)
