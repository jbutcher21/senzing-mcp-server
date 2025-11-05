#!/usr/bin/env python3
"""Get entity details by ID."""

import asyncio
import json
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def get_entity(entity_id):
    """Get details for a specific entity."""

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

                print(f"📄 Getting details for Entity ID {entity_id}...\n")

                result = await session.call_tool("get_entity", {
                    "entity_id": int(entity_id)
                })

                entity_data = json.loads(result.content[0].text)

                if "error" in entity_data:
                    print(f"❌ {entity_data['error']}")
                else:
                    print("✅ Entity Details:\n")
                    print(json.dumps(entity_data, indent=2))

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    entity_id = sys.argv[1] if len(sys.argv) > 1 else "1"
    asyncio.run(get_entity(entity_id))
