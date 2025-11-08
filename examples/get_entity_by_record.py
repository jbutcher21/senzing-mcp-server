#!/usr/bin/env python3
"""Test getting an entity by record ID."""

import asyncio
import json
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configuration
SENZING_MCP_COMMAND = os.getenv("SENZING_MCP_COMMAND", "senzing-mcp")

async def test_get_by_record_id(data_source: str, record_id: str):
    """Test getting entity by record ID."""

    config_json = os.getenv("SENZING_ENGINE_CONFIGURATION_JSON")
    if not config_json:
        print("ERROR: SENZING_ENGINE_CONFIGURATION_JSON not set!")
        return

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
                await session.initialize()

                print(f"🔍 Getting entity for record {data_source}:{record_id}...")
                print("-" * 60)

                result = await session.call_tool("get_entity_by_record_id", {
                    "data_source": data_source,
                    "record_id": record_id
                })

                entity_data = json.loads(result.content[0].text)

                if "error" in entity_data:
                    print(f"❌ Error: {entity_data['error']}")
                else:
                    print(json.dumps(entity_data, indent=2))

                    # Show which entity this record belongs to
                    resolved_entity = entity_data.get("RESOLVED_ENTITY", {})
                    entity_id = resolved_entity.get("ENTITY_ID")
                    entity_name = resolved_entity.get("ENTITY_NAME", "Unknown")

                    print("\n" + "=" * 60)
                    print(f"✅ Record {data_source}:{record_id} belongs to:")
                    print(f"   Entity ID: {entity_id}")
                    print(f"   Entity Name: {entity_name}")

                    # Show all records in this entity
                    records = resolved_entity.get("RECORDS", [])
                    print(f"\n   This entity contains {len(records)} record(s):")
                    for record in records:
                        ds = record.get("DATA_SOURCE")
                        rid = record.get("RECORD_ID")
                        print(f"   - {ds}:{rid}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python get_entity_by_record.py <DATA_SOURCE> <RECORD_ID>")
        print("Example: python get_entity_by_record.py CUSTOMERS 1001")
        sys.exit(1)

    data_source = sys.argv[1]
    record_id = sys.argv[2]

    asyncio.run(test_get_by_record_id(data_source, record_id))
