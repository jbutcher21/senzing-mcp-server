"""Main MCP server implementation for Senzing SDK."""

import asyncio
import json
import logging
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from senzing_mcp.sdk_wrapper import SenzingSDKWrapper

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create server instance
app = Server("senzing-mcp-server")

# Global SDK wrapper instance
sdk_wrapper = SenzingSDKWrapper()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available Senzing tools."""
    return [
        Tool(
            name="search_entities",
            description="Search for resolved entities by person/organization attributes. Returns ENTITY_IDs (Senzing's internal identifiers) with match scores. SEARCH STRATEGIES: (1) Start with available attributes - you can search by NAME_FULL, NAME_FIRST/NAME_LAST, PHONE_NUMBER, EMAIL_ADDRESS, ADDR_FULL, or DATE_OF_BIRTH. (2) Combine multiple attributes for better precision - e.g., name + address, or name + date of birth. (3) If search by name alone returns no results or too many results, add additional attributes like address, phone, email, or date of birth to narrow results. (4) You can search with just one attribute or combine many - the more attributes provided, the more precise the match. Use the returned ENTITY_IDs with get_entity for full details.",
            inputSchema={
                "type": "object",
                "properties": {
                    "attributes": {
                        "type": "object",
                        "description": "Search attributes - provide one or more fields to match against. Combine multiple attributes for better precision.",
                        "properties": {
                            "NAME_FULL": {"type": "string", "description": "Full name (e.g., 'John Smith')"},
                            "NAME_FIRST": {"type": "string", "description": "First name only"},
                            "NAME_LAST": {"type": "string", "description": "Last name only"},
                            "ADDR_FULL": {"type": "string", "description": "Complete address"},
                            "PHONE_NUMBER": {"type": "string", "description": "Phone in any format"},
                            "EMAIL_ADDRESS": {"type": "string", "description": "Email address"},
                            "DATE_OF_BIRTH": {"type": "string", "description": "Birth date (YYYY-MM-DD format)"},
                        },
                    },
                },
                "required": ["attributes"],
            },
        ),
        Tool(
            name="get_entity",
            description="Get full details for a resolved entity using its ENTITY_ID (Senzing's internal identifier, NOT your source record ID). Entity IDs are typically small integers (1, 2, 3...). Use search first to find the ENTITY_ID, then use this tool. RETURNS: Complete entity profile including (1) all source records that resolved into this entity, (2) entity features (names, addresses, phones, emails, identifiers), (3) relationships to other entities, (4) record-level matching information showing why records merged, (5) entity name and resolution metadata. Use this after search to get the full picture of an entity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "integer",
                        "description": "Senzing's ENTITY_ID (small integer like 1, 2, 3..., NOT your source system's record ID)",
                    },
                },
                "required": ["entity_id"],
            },
        ),
        Tool(
            name="get_source_record",
            description="Get entity details by looking up a specific source record using data source and record ID (e.g., 'CUSTOMERS:1001'). USE WHEN: You know the original source system record ID and want to find which resolved entity it belongs to. Common use case: 'Show me the entity for customer record 1001' or 'What entity contains vendor record ABC123'. This finds which entity the source record resolved into, then returns complete entity details (same as get_entity). Required parameters: data_source (e.g., 'CUSTOMERS', 'VENDORS') and record_id (e.g., '1001', 'ABC123'). Alternative to search when you have exact record identifiers.",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_source": {
                        "type": "string",
                        "description": "Data source code (e.g., 'CUSTOMERS', 'VENDORS')",
                    },
                    "record_id": {
                        "type": "string",
                        "description": "Record ID from the source system (e.g., '1001', '1002')",
                    },
                },
                "required": ["data_source", "record_id"],
            },
        ),
        Tool(
            name="find_path",
            description="Find how two entities are connected through relationships and shared attributes. Discovers the chain of connections (path) between entity A and entity B, including any intermediate entities that link them. USE CASES: 'How is person X connected to person Y?', 'What's the relationship between these two companies?', 'Show me the connection path between these entities'. RETURNS: The shortest path showing (1) each entity in the connection chain, (2) what they share (common addresses, phone numbers, names, etc.), (3) relationship types at each step. Useful for investigating connections, fraud rings, or business relationships. Requires two ENTITY_IDs - use search_entities to find them first. Set max_degrees to control how many steps to search (default: 3).",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_entity_id": {
                        "type": "integer",
                        "description": "Starting ENTITY_ID (Senzing's internal identifier)",
                    },
                    "end_entity_id": {
                        "type": "integer",
                        "description": "Ending ENTITY_ID (Senzing's internal identifier)",
                    },
                    "max_degrees": {
                        "type": "integer",
                        "description": "Maximum degrees of separation to search (default: 3)",
                        "default": 3,
                    },
                },
                "required": ["start_entity_id", "end_entity_id"],
            },
        ),
        Tool(
            name="expand_network",
            description="Expand a network of related entities starting from one or more seed entities, discovering all connected entities up to (n) degrees of separation (maximum 3 degrees). USE CASES: Finding fraud rings, mapping family networks, discovering business relationships, identifying connected parties. RETURNS: Network graph showing (1) all entities within the specified degrees, (2) how they're related, (3) shared attributes (addresses, phones, names), (4) relationship strengths. PARAMETERS: entity_ids (one or more starting points), max_degrees (how far to expand, default 2, max 3), build_out_degrees (expansion pattern), max_entities (result limit, default 100). More degrees = larger network but slower. Use 1-2 degrees for focused analysis, 3 degrees for comprehensive mapping. Requires ENTITY_IDs - use search_entities to find them first.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of starting ENTITY_IDs (Senzing's internal identifiers)",
                    },
                    "max_degrees": {
                        "type": "integer",
                        "description": "Maximum degrees of separation to explore (default: 2, maximum: 3)",
                        "default": 2,
                        "minimum": 1,
                        "maximum": 3,
                    },
                    "build_out_degrees": {
                        "type": "integer",
                        "description": "How many degrees to build out from each entity (default: 1)",
                        "default": 1,
                    },
                    "max_entities": {
                        "type": "integer",
                        "description": "Maximum total entities to return (default: 100)",
                        "default": 100,
                    },
                },
                "required": ["entity_ids"],
            },
        ),
        Tool(
            name="explain_why_related",
            description="Explain WHY two entities are or are not related/resolved together using Senzing's scoring analysis. USE CASES: 'Why didn't these two records merge into one entity?', 'What attributes connect these entities?', 'Why are these considered related but not the same?'. RETURNS: Detailed analysis including (1) matching features (names, addresses, phones that match), (2) conflicting features (different values that prevented merge), (3) match scores and confidence levels, (4) feature-level scoring details, (5) resolution rules applied. This is the WHY analysis - explaining Senzing's decision about whether entities should be related, resolved together, or kept separate. Essential for understanding entity resolution decisions and investigating merge/non-merge reasons. Requires two ENTITY_IDs - use search_entities to find them first. For formatting guidelines, see RESPONSE_FORMATTING.md.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id_1": {
                        "type": "integer",
                        "description": "First ENTITY_ID (Senzing's internal identifier)",
                    },
                    "entity_id_2": {
                        "type": "integer",
                        "description": "Second ENTITY_ID (Senzing's internal identifier)",
                    },
                },
                "required": ["entity_id_1", "entity_id_2"],
            },
        ),
        Tool(
            name="explain_how_resolved",
            description="Explain HOW an entity was resolved from its source records, showing the step-by-step resolution timeline. USE CASES: 'How did these records merge together?', 'Show me the resolution history', 'What was the sequence of merges?', auditing resolution decisions, understanding entity formation. RETURNS: Complete resolution story including (1) step-by-step merge sequence (which records merged when), (2) match drivers at each step (what attributes caused the merge), (3) all source records involved, (4) features from each record, (5) final resolved entity state. This is the HOW analysis - the chronological story of how individual records were progressively merged into the final entity. Essential for auditing, debugging resolution issues, and understanding entity composition. Requires one ENTITY_ID - use search_entities to find it first. For formatting guidelines, see RESPONSE_FORMATTING.md.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "integer",
                        "description": "ENTITY_ID to explain (Senzing's internal identifier)",
                    },
                },
                "required": ["entity_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    try:
        # Ensure SDK is initialized
        if not sdk_wrapper._initialized:
            await sdk_wrapper.initialize()

        # Entity Search and Retrieval
        if name == "search_entities":
            attributes_dict = arguments.get("attributes", {})
            attributes_json = json.dumps(attributes_dict)
            result = await sdk_wrapper.search_by_attributes(attributes_json)

            # Prepend formatting instructions
            formatting_note = """[FORMATTING INSTRUCTIONS FOR SEARCH RESULTS]
Present as clear search results:
1. Search Summary:
   - Number of entities found
   - Search criteria used
   - Score range
2. Results Table grouped by score ranges:
   - Strong Matches (90-100%)
   - Good Matches (70-89%)
   - Possible Matches (below 70%)
   Columns: Entity ID | Name | Score | Data Sources | Key Matches
3. Analysis:
   - Explain what scores mean
   - Why certain entities scored higher
   - Notable patterns in results

[RAW JSON DATA FOLLOWS]
"""
            return [TextContent(type="text", text=formatting_note + result)]

        elif name == "get_entity":
            entity_id = arguments.get("entity_id")
            result = await sdk_wrapper.get_entity_by_entity_id(entity_id)

            # Prepend formatting instructions
            formatting_note = """[FORMATTING INSTRUCTIONS FOR ENTITY DETAILS]
Present as comprehensive entity profile:
1. Entity Overview:
   - Entity ID and resolved name
   - Number of source records and data sources
2. Source Records Section:
   - Group by data source
   - Show record IDs with key info and dates
3. Resolved Features Section:
   - Names (primary and variants)
   - Contact Information (email, phone, address)
   - Identifiers (DOB, SSN, employee IDs, etc.)
4. Relationships Section (if present):
   - Group by relationship type (Possibly Related, Possibly Same)
   - Show entity ID, name, and connection reason
Keep organized with clear section headers.

[RAW JSON DATA FOLLOWS]
"""
            return [TextContent(type="text", text=formatting_note + result)]

        elif name == "get_source_record":
            data_source = arguments.get("data_source")
            record_id = arguments.get("record_id")
            result = await sdk_wrapper.get_entity_by_record_id(data_source, record_id)

            # Prepend formatting instructions
            formatting_note = """[FORMATTING INSTRUCTIONS FOR SOURCE RECORD LOOKUP]
Present as entity profile (same format as get_entity):
1. Start by noting which source record was queried
2. Entity Overview:
   - Entity ID and resolved name
   - Number of source records and data sources
3. Source Records Section:
   - Highlight the queried record
   - Group by data source
   - Show record IDs with key info
4. Resolved Features Section:
   - Names, Contact Information, Identifiers
5. Relationships Section (if present)
Keep organized with clear section headers.

[RAW JSON DATA FOLLOWS]
"""
            return [TextContent(type="text", text=formatting_note + result)]

        # Relationship Analysis
        elif name == "find_path":
            start_id = arguments.get("start_entity_id")
            end_id = arguments.get("end_entity_id")
            max_degrees = arguments.get("max_degrees", 3)
            result = await sdk_wrapper.find_path_by_entity_id(
                start_id, end_id, max_degrees
            )

            # Prepend formatting instructions
            formatting_note = """[FORMATTING INSTRUCTIONS FOR RELATIONSHIP PATH]
Present as connection path visualization:
1. Path Summary:
   - Degrees of separation
   - Total entities in path
   - Primary connection types
2. Path Visualization with arrows:
   Entity A (Name)
       ↓ [Connection Type: details]
   Entity B (Name)
       ↓ [Connection Type: details]
   Entity C (Name)
3. Analysis:
   - Explain what the connections mean
   - Relationship strength/confidence
   - Notable patterns or concerns
Alternative: Use table format for complex paths.

[RAW JSON DATA FOLLOWS]
"""
            return [TextContent(type="text", text=formatting_note + result)]

        elif name == "expand_network":
            entity_ids = arguments.get("entity_ids", [])
            max_degrees = arguments.get("max_degrees", 2)
            # Enforce maximum of 3 degrees
            max_degrees = min(max_degrees, 3)
            build_out = arguments.get("build_out_degrees", 1)
            max_entities = arguments.get("max_entities", 100)
            entity_list_json = json.dumps({"ENTITIES": [{"ENTITY_ID": eid} for eid in entity_ids]})
            result = await sdk_wrapper.find_network_by_entity_id(
                entity_list_json, max_degrees, build_out, max_entities
            )

            # Prepend formatting instructions
            formatting_note = """[FORMATTING INSTRUCTIONS FOR NETWORK EXPANSION]
Present as organized network analysis:
1. Network Summary:
   - Number of entities and relationships
   - Degrees explored
   - Key clusters identified
2. Organize by connection strength:
   - Core Entities (starting points)
   - Direct Connections (1 degree)
   - Secondary Connections (2 degrees)
   - For each: show entity, data sources, connection type
3. Highlight Clusters:
   - Group related entities (e.g., Household, Business)
   - Explain common attributes
Optional: Include table showing entity connections and relationship types.

[RAW JSON DATA FOLLOWS]
"""
            return [TextContent(type="text", text=formatting_note + result)]

        elif name == "explain_why_related":
            entity_id_1 = arguments.get("entity_id_1")
            entity_id_2 = arguments.get("entity_id_2")
            result = await sdk_wrapper.why_entities(entity_id_1, entity_id_2)

            # Prepend formatting instructions
            formatting_note = """[FORMATTING INSTRUCTIONS FOR WHY ANALYSIS]
Present as relationship analysis:
1. Summary:
   - ✅ Confirmations: features that matched
   - ❌ Denials: features that conflicted
   - Match key used
   - ➡️ Bottom line: final decision statement
2. Side-by-side comparison table:
   - Columns: Feature | Entity 1 | Entity 2 | Result
   - Always include DATA_SOURCE row showing record counts (e.g., "CUSTOMERS:4, WATCHLIST:1")
   - Mark matching features with ✅, conflicts with ❌
   - Do NOT show or explain ERRULE_CODE
Keep tone professional and concise.

[RAW JSON DATA FOLLOWS]
"""
            return [TextContent(type="text", text=formatting_note + result)]

        elif name == "explain_how_resolved":
            entity_id = arguments.get("entity_id")
            result = await sdk_wrapper.how_entity_by_entity_id(entity_id)

            # Prepend formatting instructions
            formatting_note = """[FORMATTING INSTRUCTIONS FOR HOW ANALYSIS]
Present as step-by-step resolution timeline:
1. Summary: Which records merged, how many steps, match drivers, any conflicts
2. Resolution Steps: For each step show:
   - Step header with verb rules: "with" for single-to-single, "into" for single-to-group
   - Group notation: "CUSTOMERS:1002 +3 more" not full lists
   - Confirming features with ✅ and scores
   - Denying features with ❌
   - Match keys used
3. Bottom line: Concise final decision statement with ➡️
Keep tone professional and clear.

[RAW JSON DATA FOLLOWS]
"""
            return [TextContent(type="text", text=formatting_note + result)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Main entry point for the MCP server."""
    try:
        logger.info("Starting Senzing MCP server...")

        # Initialize SDK
        await sdk_wrapper.initialize()
        logger.info("Senzing SDK initialized successfully")

        # Run server
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options(),
            )

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise
    finally:
        # Cleanup
        await sdk_wrapper.cleanup()
        logger.info("Senzing MCP server stopped")


def run():
    """Entry point for console script."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
