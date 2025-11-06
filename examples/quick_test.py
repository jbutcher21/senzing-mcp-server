#!/usr/bin/env python3
"""Quick test of Senzing MCP server."""

import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configuration: Path to senzing-mcp command
# Default assumes it's in your PATH after running: pip install -e .
# Or specify full path to venv: "/path/to/senzing-mcp-server/venv/bin/senzing-mcp"
SENZING_MCP_COMMAND = os.getenv("SENZING_MCP_COMMAND", "senzing-mcp")

async def test_server():
    """Test basic server functionality."""

    # Get the environment variable
    config_json = os.getenv("SENZING_ENGINE_CONFIGURATION_JSON")
    if not config_json:
        print("ERROR: SENZING_ENGINE_CONFIGURATION_JSON not set!")
        print("Run: source ./senzing_env.sh first")
        return

    print("🚀 Starting Senzing MCP Server Test...\n")

    server_params = StdioServerParameters(
        command=SENZING_MCP_COMMAND,
        env={
            "SENZING_ENGINE_CONFIGURATION_JSON": config_json,
            "LD_LIBRARY_PATH": os.getenv("LD_LIBRARY_PATH", "")
        }
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize
                await session.initialize()
                print("✅ Connected to MCP server\n")

                # Test 1: List available tools
                print("📋 Available Tools:")
                print("-" * 60)
                tools = await session.list_tools()
                for i, tool in enumerate(tools.tools, 1):
                    print(f"{i:2d}. {tool.name}")
                    print(f"    {tool.description[:70]}...")
                print()

                # Test 2: Get stats
                print("📊 Test: Get Senzing Statistics")
                print("-" * 60)
                result = await session.call_tool("get_stats", {})
                stats = json.loads(result.content[0].text)
                print(json.dumps(stats, indent=2))
                print()

                # Test 3: Get config info
                print("⚙️  Test: Get Configuration Info")
                print("-" * 60)
                result = await session.call_tool("get_config_info", {})
                config = json.loads(result.content[0].text)
                print(json.dumps(config, indent=2))
                print()

                # Test 4: Try a search
                print("🔍 Test: Search for entities named 'John Smith'")
                print("-" * 60)
                result = await session.call_tool("search_entities", {
                    "attributes": {"NAME_FULL": "John Smith"}
                })
                search_result = json.loads(result.content[0].text)
                print(json.dumps(search_result, indent=2))
                print()

                print("✅ All tests completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_server())
