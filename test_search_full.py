#!/usr/bin/env python3
"""Test search with full output to see enhanced flags."""

import asyncio
import json
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_search(name):
    """Test search and show full JSON output."""

    config_json = os.getenv("SENZING_ENGINE_CONFIGURATION_JSON")
    ld_library_path = os.getenv("LD_LIBRARY_PATH", "")

    if not config_json:
        print("ERROR: SENZING_ENGINE_CONFIGURATION_JSON not set!")
        return

    server_params = StdioServerParameters(
        command="/data/etl/senzing/er/v4beta/senzingMCP/venv/bin/senzing-mcp",
        env={
            "SENZING_ENGINE_CONFIGURATION_JSON": config_json,
            "LD_LIBRARY_PATH": ld_library_path
        }
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                print(f"🔍 Searching for entities named '{name}'...\n")

                result = await session.call_tool("search_entities", {
                    "attributes": {"NAME_FULL": name}
                })

                search_result = json.loads(result.content[0].text)

                print("📄 Full Search Results:\n")
                print(json.dumps(search_result, indent=2))

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "Robert Smith"
    asyncio.run(test_search(name))
