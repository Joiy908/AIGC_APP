from llama_index.tools.mcp import (
    aget_tools_from_mcp_url,
    get_tools_from_mcp_url,
)

# async
tools = get_tools_from_mcp_url("http://127.0.0.1:9000/mcp")
