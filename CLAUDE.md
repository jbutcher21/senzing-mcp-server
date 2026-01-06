# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an MCP (Model Context Protocol) server that exposes Senzing SDK entity resolution capabilities to AI assistants. The server wraps the synchronous Senzing Python SDK with an async interface and provides 7 read-only tools for entity search and relationship analysis.

**Critical Concept - Entity ID vs Record ID:**
- **Entity ID**: Senzing's internal identifier (small integers like 1, 2, 3...) assigned after entity resolution. Most tools require this.
- **Record ID**: Your source system's identifier (like "1001") in a data source (like "CUSTOMERS").
- Use `search_entities` or `get_source_record` to find Entity IDs first, then use other tools.

**Response Formatting**: When interpreting HOW and WHY results from `explain_how_resolved` and `explain_why_related` tools, follow `RESPONSE_FORMATTING.md` for clear presentation.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run server with STDIO transport (default)
python -m senzing_mcp.server          # From src/ directory
./launch_senzing_mcp.sh               # Or use launch script

# Run server with HTTP/SSE transport
python -m senzing_mcp.server --http                    # Default: localhost:8000
python -m senzing_mcp.server --http --port 3000        # Custom port
python -m senzing_mcp.server --http --host 0.0.0.0     # All interfaces

# Debug logging
export SENZING_LOG_LEVEL=1

# Test via CLI client (requires env vars set)
python examples/senzing_test.py list-tools
python examples/senzing_test.py search "John Smith"
python examples/senzing_test.py get 1
python examples/senzing_test.py get-record CUSTOMERS 1001
python examples/senzing_test.py find-path 1 2
python examples/senzing_test.py expand 1
python examples/senzing_test.py why 1 2
python examples/senzing_test.py how 1
```

## Transport Options

**STDIO (default)**: AI assistant spawns server as subprocess, communicates via stdin/stdout.
- Use: `python -m senzing_mcp.server` or `./launch_senzing_mcp.sh`
- Server lifecycle tied to AI session

**HTTP/SSE**: Server runs independently, AI connects via HTTP.
- Use: `python -m senzing_mcp.server --http --port 8000`
- Server URL: `http://localhost:8000/sse`
- Server persists across AI sessions, SDK stays initialized

## Architecture

### Core Components

**server.py** - MCP server using the `mcp` package
- `list_tools()`: Defines 7 read-only tools with detailed schemas
- `call_tool()`: Routes all tool calls, ensures SDK initialization, handles errors
- Tool categories:
  - Entity search/retrieval: `search_entities`, `get_entity`, `get_source_record`
  - Relationship analysis: `find_path`, `expand_network`, `explain_why_related`, `explain_how_resolved`
- Each tool response prepends formatting instructions before raw JSON

**sdk_wrapper.py** - Async wrapper around synchronous Senzing SDK
- `SenzingSDKWrapper` class with ThreadPoolExecutor for non-blocking SDK calls
- `_run_async()`: Core pattern - all sync SDK calls run through this
- `initialize()`: Loads config from env vars, creates factory and engine
- Factory pattern via `SzAbstractFactoryCore` creates `SzEngine` component

### Key Patterns

**Async Wrapper Pattern** (all SDK operations):
1. Check `_initialized` state
2. Run sync SDK call in ThreadPoolExecutor via `_run_async()`
3. Catch `SzError`/`SzNotFoundError` and return JSON error
4. **Auto-reinitialize on stale config**: If error contains `SENZ2062` or `SENZ0033`, automatically reinitialize SDK and retry once

**Tool Handler Pattern** (`call_tool()`):
1. Ensure SDK initialized (lazy init on first call)
2. Extract and transform arguments (e.g., entity_ids list → JSON)
3. Call async wrapper method
4. Return TextContent with formatting instructions + result

**Flag Management** - SDK operations use `SzEngineFlags` combinations matching `sz_explorer`:
- `get_entity`/`get_entity_by_record_id`: Comprehensive entity info with relations, features, matching data
- `search_by_attributes`: Base search flags, auto-enhanced with feature flags if <11 results
- `why_entities`: Internal features and scoring details
- `how_entity_by_entity_id`: Resolution steps with all features

### Environment Configuration

Required:
- `SENZING_ENGINE_CONFIGURATION_JSON`: JSON with database connection and resource paths

Optional:
- `SENZING_LOG_LEVEL`: Verbosity (default: 0)
- `SENZING_INSTANCE_NAME`: Instance name (default: "senzing-mcp-server")

Example config JSON:
```json
{
  "PIPELINE": {
    "CONFIGPATH": "/etc/opt/senzing",
    "RESOURCEPATH": "/opt/senzing/g2/resources",
    "SUPPORTPATH": "/opt/senzing/data"
  },
  "SQL": {
    "CONNECTION": "sqlite3://na:na@/var/opt/senzing/sqlite/G2C.db"
  }
}
```

## Common Issues

**SDK Import Errors**: `LD_LIBRARY_PATH` and `PYTHONPATH` must be set for Senzing SDK to load. Set in MCP config's `env` section.

**"SENZING_ENGINE_CONFIGURATION_JSON is not set"**: Add env vars to MCP config's `env` section (see README.md for full config example).

**Initialization Failures**: Verify `SENZING_ENGINE_CONFIGURATION_JSON` is valid JSON with correct paths.

**Async Errors**: All SDK calls must go through `_run_async()` method - the SDK is synchronous.
