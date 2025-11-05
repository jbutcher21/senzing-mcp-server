#!/usr/bin/env python3
"""Example client to test the Senzing MCP server."""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    """Test the Senzing MCP server."""

    # Configure server parameters
    server_params = StdioServerParameters(
        command="/data/etl/senzing/er/v4beta/senzingMCP/venv/bin/senzing-mcp",
        env={
            "SENZING_ENGINE_CONFIGURATION_JSON": '{"PIPELINE":{"SUPPORTPATH":"/data/etl/senzing/er/v4beta/data","CONFIGPATH":"/data/etl/senzing/er/v4beta/etc","RESOURCEPATH":"/data/etl/senzing/er/v4beta/resources"},"SQL":{"CONNECTION":"sqlite3://na:na@/data/etl/senzing/er/v4beta/var/sqlite/G2C.db"}}'
        }
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Example: Get stats
            print("\nGetting Senzing stats...")
            result = await session.call_tool("get_stats", {})
            print("Stats:", json.dumps(json.loads(result.content[0].text), indent=2))

            # Example: Search for an entity
            print("\nSearching for entities...")
            result = await session.call_tool("search_entities", {
                "attributes": {
                    "NAME_FULL": "John Smith"
                }
            })
            print("Search results:", result.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())
