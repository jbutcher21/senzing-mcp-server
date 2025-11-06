"""Main MCP server implementation for Senzing SDK."""

import asyncio
import json
import logging
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .sdk_wrapper import SenzingSDKWrapper

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
            description="Search for entities by attributes (name, address, phone, email, etc.). Returns matching entities with scores.",
            inputSchema={
                "type": "object",
                "properties": {
                    "attributes": {
                        "type": "object",
                        "description": "Entity attributes to search for",
                        "properties": {
                            "NAME_FULL": {"type": "string", "description": "Full name"},
                            "NAME_FIRST": {"type": "string", "description": "First name"},
                            "NAME_LAST": {"type": "string", "description": "Last name"},
                            "ADDR_FULL": {"type": "string", "description": "Full address"},
                            "PHONE_NUMBER": {"type": "string", "description": "Phone number"},
                            "EMAIL_ADDRESS": {"type": "string", "description": "Email address"},
                            "DATE_OF_BIRTH": {"type": "string", "description": "Date of birth (YYYY-MM-DD)"},
                        },
                    },
                },
                "required": ["attributes"],
            },
        ),
        Tool(
            name="get_entity",
            description="Retrieve detailed information about a specific entity by its entity ID. Returns entity details including all records and relationships.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "integer",
                        "description": "The unique entity ID",
                    },
                },
                "required": ["entity_id"],
            },
        ),
        Tool(
            name="find_relationship_path",
            description="Find the relationship path between two entities. Shows how entities are connected through intermediate entities and shared attributes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_entity_id": {
                        "type": "integer",
                        "description": "Starting entity ID",
                    },
                    "end_entity_id": {
                        "type": "integer",
                        "description": "Ending entity ID",
                    },
                    "max_degrees": {
                        "type": "integer",
                        "description": "Maximum degrees of separation (default: 3)",
                        "default": 3,
                    },
                },
                "required": ["start_entity_id", "end_entity_id"],
            },
        ),
        Tool(
            name="find_network",
            description="Discover a network of related entities starting from a list of entity IDs. Useful for analyzing connections and relationships.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of entity IDs to start from",
                    },
                    "max_degrees": {
                        "type": "integer",
                        "description": "Maximum degrees of separation (default: 2)",
                        "default": 2,
                    },
                    "build_out_degrees": {
                        "type": "integer",
                        "description": "Degrees to build out from each entity (default: 1)",
                        "default": 1,
                    },
                    "max_entities": {
                        "type": "integer",
                        "description": "Maximum entities to return (default: 100)",
                        "default": 100,
                    },
                },
                "required": ["entity_ids"],
            },
        ),
        Tool(
            name="explain_relationship",
            description="Explain why two entities are related or resolved together (WHY analysis). Returns matching attributes, conflicts, and scoring details. For presentation guidelines, see RESPONSE_FORMATTING.md.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id_1": {
                        "type": "integer",
                        "description": "First entity ID",
                    },
                    "entity_id_2": {
                        "type": "integer",
                        "description": "Second entity ID",
                    },
                },
                "required": ["entity_id_1", "entity_id_2"],
            },
        ),
        Tool(
            name="explain_entity_resolution",
            description="Explain how an entity was resolved from its source records (HOW analysis). Shows the step-by-step resolution process, merge decisions, and match drivers. For presentation guidelines, see RESPONSE_FORMATTING.md.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "integer",
                        "description": "Entity ID to explain",
                    },
                },
                "required": ["entity_id"],
            },
        ),
        Tool(
            name="get_stats",
            description="Get Senzing engine statistics including record counts, entity counts, and performance metrics.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_config_info",
            description="Get information about the current Senzing configuration including version and settings.",
            inputSchema={
                "type": "object",
                "properties": {},
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
            return [TextContent(type="text", text=result)]

        elif name == "get_entity":
            entity_id = arguments.get("entity_id")
            result = await sdk_wrapper.get_entity_by_entity_id(entity_id)
            return [TextContent(type="text", text=result)]

        # Relationship Analysis
        elif name == "find_relationship_path":
            start_id = arguments.get("start_entity_id")
            end_id = arguments.get("end_entity_id")
            max_degrees = arguments.get("max_degrees", 3)
            result = await sdk_wrapper.find_path_by_entity_id(
                start_id, end_id, max_degrees
            )
            return [TextContent(type="text", text=result)]

        elif name == "find_network":
            entity_ids = arguments.get("entity_ids", [])
            max_degrees = arguments.get("max_degrees", 2)
            build_out = arguments.get("build_out_degrees", 1)
            max_entities = arguments.get("max_entities", 100)
            entity_list_json = json.dumps({"ENTITIES": [{"ENTITY_ID": eid} for eid in entity_ids]})
            result = await sdk_wrapper.find_network_by_entity_id(
                entity_list_json, max_degrees, build_out, max_entities
            )
            return [TextContent(type="text", text=result)]

        elif name == "explain_relationship":
            entity_id_1 = arguments.get("entity_id_1")
            entity_id_2 = arguments.get("entity_id_2")
            result = await sdk_wrapper.why_entities(entity_id_1, entity_id_2)
            return [TextContent(type="text", text=result)]

        elif name == "explain_entity_resolution":
            entity_id = arguments.get("entity_id")
            result = await sdk_wrapper.how_entity_by_entity_id(entity_id)
            return [TextContent(type="text", text=result)]

        # Configuration and Stats
        elif name == "get_stats":
            result = await sdk_wrapper.get_stats()
            return [TextContent(type="text", text=result)]

        elif name == "get_config_info":
            config_id = await sdk_wrapper.get_active_config_id()
            version = await sdk_wrapper.get_version()
            combined = {
                "config": json.loads(config_id),
                "product": json.loads(version),
            }
            return [TextContent(type="text", text=json.dumps(combined, indent=2))]

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
