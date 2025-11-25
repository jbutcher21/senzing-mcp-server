#!/usr/bin/env python3
"""
Unified test client for Senzing MCP server.

Usage:
  senzing_test.py list-tools
  senzing_test.py search <name>
  senzing_test.py get <entity_id>
  senzing_test.py get-record <data_source> <record_id>
  senzing_test.py find-path <entity_id1> <entity_id2> [max_degrees]
  senzing_test.py expand <entity_id> [max_degrees] [max_entities]
  senzing_test.py why <entity_id1> <entity_id2>
  senzing_test.py how <entity_id>

Examples:
  # List available MCP tools
  senzing_test.py list-tools

  # Search for entities by name
  senzing_test.py search "John Smith"

  # Get entity details by ID
  senzing_test.py get 1

  # Get entity by source record
  senzing_test.py get-record CUSTOMERS 1001

  # Find relationship path between entities
  senzing_test.py find-path 1 2
  senzing_test.py find-path 1 2 3  # with max_degrees

  # Expand entity network
  senzing_test.py expand 1
  senzing_test.py expand 1 2    # with max_degrees
  senzing_test.py expand 1 2 20 # with max_degrees and max_entities

  # Explain why entities are related
  senzing_test.py why 1 2

  # Explain how entity was resolved
  senzing_test.py how 1

Environment Variables:
  SENZING_ENGINE_CONFIGURATION_JSON  Required: Senzing database config
  LD_LIBRARY_PATH                    Required: Path to Senzing libraries
  SENZING_MCP_COMMAND                Optional: Path to senzing-mcp (default: "senzing-mcp")
"""

import asyncio
import json
import os
import sys
from contextlib import asynccontextmanager
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SENZING_MCP_COMMAND = os.getenv("SENZING_MCP_COMMAND", "senzing-mcp")


@asynccontextmanager
async def get_mcp_session():
    """Context manager for MCP client session - handles all connection boilerplate."""
    config_json = os.getenv("SENZING_ENGINE_CONFIGURATION_JSON")
    if not config_json:
        raise RuntimeError(
            "SENZING_ENGINE_CONFIGURATION_JSON environment variable is not set!\n"
            "Set it in your shell environment or MCP configuration."
        )

    server_params = StdioServerParameters(
        command=SENZING_MCP_COMMAND,
        env={
            "SENZING_ENGINE_CONFIGURATION_JSON": config_json,
            "LD_LIBRARY_PATH": os.getenv("LD_LIBRARY_PATH", ""),
            "PYTHONPATH": os.getenv("PYTHONPATH", "")
        }
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def cmd_list_tools():
    """List all available MCP tools."""
    async with get_mcp_session() as session:
        tools = await session.list_tools()
        print(f"📋 Available MCP Tools ({len(tools.tools)}):\n")
        for i, tool in enumerate(tools.tools, 1):
            print(f"{i}. {tool.name}")
            print(f"   {tool.description}\n")


async def cmd_search(name):
    """Search for entities by name."""
    print(f"🔍 Searching for entities named '{name}'...\n")
    async with get_mcp_session() as session:
        result = await session.call_tool("search_entities", {
            "attributes": {"NAME_FULL": name}
        })
        data = json.loads(result.content[0].text)
        print(json.dumps(data, indent=2))


async def cmd_get_entity(entity_id):
    """Get entity details by ID."""
    print(f"📄 Getting details for Entity ID {entity_id}...\n")
    async with get_mcp_session() as session:
        result = await session.call_tool("get_entity", {
            "entity_id": int(entity_id)
        })
        data = json.loads(result.content[0].text)
        print(json.dumps(data, indent=2))


async def cmd_get_record(data_source, record_id):
    """Get entity by source record ID."""
    print(f"🔍 Getting entity for record {data_source}:{record_id}...\n")
    async with get_mcp_session() as session:
        result = await session.call_tool("get_source_record", {
            "data_source": data_source,
            "record_id": record_id
        })
        data = json.loads(result.content[0].text)
        print(json.dumps(data, indent=2))


async def cmd_find_path(entity_id1, entity_id2, max_degrees=3):
    """Find relationship path between entities."""
    print(f"🔗 Finding path between entities {entity_id1} and {entity_id2}...\n")
    async with get_mcp_session() as session:
        result = await session.call_tool("find_path", {
            "start_entity_id": int(entity_id1),
            "end_entity_id": int(entity_id2),
            "max_degrees": int(max_degrees)
        })
        data = json.loads(result.content[0].text)
        print(json.dumps(data, indent=2))


async def cmd_expand(entity_id, max_degrees=1, max_entities=10):
    """Expand entity network."""
    print(f"🌐 Expanding network for entity {entity_id} (degrees={max_degrees}, max={max_entities})...\n")
    async with get_mcp_session() as session:
        result = await session.call_tool("expand_network", {
            "entity_ids": [int(entity_id)],
            "max_degrees": int(max_degrees),
            "max_entities": int(max_entities)
        })
        data = json.loads(result.content[0].text)
        print(json.dumps(data, indent=2))


async def cmd_why(entity_id1, entity_id2):
    """Explain why entities are related."""
    print(f"❓ Explaining why entities {entity_id1} and {entity_id2} are related...\n")
    async with get_mcp_session() as session:
        result = await session.call_tool("explain_why_related", {
            "entity_id1": int(entity_id1),
            "entity_id2": int(entity_id2)
        })
        data = json.loads(result.content[0].text)
        print(json.dumps(data, indent=2))


async def cmd_how(entity_id):
    """Explain how entity was resolved."""
    print(f"🔬 Explaining how entity {entity_id} was resolved...\n")
    async with get_mcp_session() as session:
        result = await session.call_tool("explain_how_resolved", {
            "entity_id": int(entity_id)
        })
        data = json.loads(result.content[0].text)
        print(json.dumps(data, indent=2))


def main():
    """Parse CLI arguments and dispatch to appropriate command."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    try:
        if command == "list-tools":
            asyncio.run(cmd_list_tools())

        elif command == "search" and len(sys.argv) >= 3:
            asyncio.run(cmd_search(sys.argv[2]))

        elif command == "get" and len(sys.argv) >= 3:
            asyncio.run(cmd_get_entity(sys.argv[2]))

        elif command == "get-record" and len(sys.argv) >= 4:
            asyncio.run(cmd_get_record(sys.argv[2], sys.argv[3]))

        elif command == "find-path" and len(sys.argv) >= 4:
            max_degrees = int(sys.argv[4]) if len(sys.argv) > 4 else 3
            asyncio.run(cmd_find_path(sys.argv[2], sys.argv[3], max_degrees))

        elif command == "expand" and len(sys.argv) >= 3:
            max_degrees = int(sys.argv[3]) if len(sys.argv) > 3 else 1
            max_entities = int(sys.argv[4]) if len(sys.argv) > 4 else 10
            asyncio.run(cmd_expand(sys.argv[2], max_degrees, max_entities))

        elif command == "why" and len(sys.argv) >= 4:
            asyncio.run(cmd_why(sys.argv[2], sys.argv[3]))

        elif command == "how" and len(sys.argv) >= 3:
            asyncio.run(cmd_how(sys.argv[2]))

        else:
            print("❌ Invalid command or missing arguments\n")
            print(__doc__)
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
