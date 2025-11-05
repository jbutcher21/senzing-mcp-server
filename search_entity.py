#!/usr/bin/env python3
"""Search for entities by name."""

import asyncio
import json
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def search_entity(name):
    """Search for entities by name."""

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

                if "RESOLVED_ENTITIES" in search_result and search_result["RESOLVED_ENTITIES"]:
                    print(f"✅ Found {len(search_result['RESOLVED_ENTITIES'])} matching entities:\n")

                    for i, entity in enumerate(search_result["RESOLVED_ENTITIES"], 1):
                        resolved_entity = entity.get("ENTITY", {}).get("RESOLVED_ENTITY", {})
                        entity_id = resolved_entity.get("ENTITY_ID", "N/A")
                        entity_name = resolved_entity.get("ENTITY_NAME", "N/A")
                        records = resolved_entity.get("RECORDS", [])
                        features = resolved_entity.get("FEATURES", {})

                        match_info = entity.get("MATCH_INFO", {})
                        match_key = match_info.get("MATCH_KEY", "N/A")
                        match_score = entity.get("MATCH_SCORE", "N/A")

                        print(f"{i}. Entity ID: {entity_id}")
                        print(f"   Name: {entity_name}")
                        print(f"   Match Key: {match_key}")
                        print(f"   Match Score: {match_score}")
                        print(f"   Records: {len(records)} from {', '.join(set(r['DATA_SOURCE'] for r in records))}")

                        # Show all entity features
                        if features:
                            print(f"   Features:")
                            for feat_type, feat_list in features.items():
                                if feat_type == "RECORD_TYPE":
                                    continue  # Skip RECORD_TYPE
                                for feat in feat_list:
                                    feat_desc = feat.get("FEAT_DESC", "")
                                    usage_type = feat.get("USAGE_TYPE", "")
                                    usage_str = f" ({usage_type})" if usage_type else ""
                                    print(f"      {feat_type}: {feat_desc}{usage_str}")
                        print()
                else:
                    print("❌ No entities found matching that name.")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "Robert Johnson"
    asyncio.run(search_entity(name))
