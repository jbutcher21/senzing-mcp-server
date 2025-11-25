# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an MCP (Model Context Protocol) server that exposes Senzing SDK entity resolution capabilities to AI assistants like Claude, ChatGPT, and Amazon Q Developer. The server wraps the synchronous Senzing Python SDK with an async interface and provides 7 read-only tools for entity search and relationship analysis.

**Key Concepts:**
- **Entity ID**: Senzing's internal identifier (small integers like 1, 2, 3...) assigned after entity resolution
- **Record ID**: Your source system's identifier (like "1001", "1002") in a specific data source (like "CUSTOMERS")
- Most tools require Entity IDs. Use `search_entities` or `get_source_record` to find Entity IDs first.

**Important**: When interpreting HOW and WHY results from `explain_how_resolved` and `explain_why_related` tools, follow the formatting guidelines in `RESPONSE_FORMATTING.md` for clear, professional presentation of entity resolution explanations.

## Development Commands

### Installation
```bash
# Clone repository to your server
git clone https://github.com/jbutcher21/senzing-mcp-server.git
cd senzing-mcp-server

# Make launch script executable
chmod +x launch_senzing_mcp.sh

# Environment variables are configured in your AI assistant's MCP config
# (see Configuration section in the setup documentation)
```

### Running the Server
```bash
# Start MCP server (uses stdio transport)
senzing-mcp

# Or run directly as module
python -m senzing_mcp.server

# With debug logging
export SENZING_LOG_LEVEL=1
senzing-mcp
```

### Testing Examples
```bash
# Unified test client in examples/ directory
python examples/senzing_test.py list-tools         # List available tools
python examples/senzing_test.py search "Name"      # Search entities
python examples/senzing_test.py get 1              # Get entity by ID
python examples/senzing_test.py get-record CUSTOMERS 1001  # Get by record
python examples/senzing_test.py find-path 1 2      # Find relationship path
python examples/senzing_test.py expand 1           # Expand network
python examples/senzing_test.py why 1 2            # Explain why related
python examples/senzing_test.py how 1              # Explain how resolved
```

## Architecture

### Core Components

**src/senzing_mcp/server.py** (server.py:1)
- MCP server implementation using the `mcp` package
- Defines 7 read-only tools exposed to AI assistants
- Tool categories:
  - Entity search/retrieval: `search_entities`, `get_entity`, `get_source_record`
  - Relationship analysis: `find_path`, `expand_network`, `explain_why_related`, `explain_how_resolved`
- Uses stdio transport for Claude Desktop integration
- All tool calls are routed through `call_tool()` handler

**src/senzing_mcp/sdk_wrapper.py** (sdk_wrapper.py:1)
- Async wrapper around synchronous Senzing SDK
- Uses ThreadPoolExecutor for non-blocking SDK calls (sdk_wrapper.py:37)
- Initialization from environment variables (sdk_wrapper.py:40)
- Key pattern: All SDK methods are wrapped with `_run_async()` to execute in thread pool (sdk_wrapper.py:83)
- Factory pattern initialization through SzAbstractFactoryCore (sdk_wrapper.py:68)

### SDK Integration

The Senzing SDK requires environment variables to be set before the MCP server starts. These environment variables are passed from the AI assistant's MCP configuration through the launch script to the server.

The SDK provides the core component initialized through the factory:
- `SzEngine`: Entity operations (search, get, relationships, explanations)

### Flag Management

Entity operations use specific flag combinations to control detail level. The wrapper uses the same flags as `sz_explorer` for consistency:

- **get_entity** (sdk_wrapper.py:99): Comprehensive entity info with relations, features, matching data
- **search_entities** (sdk_wrapper.py:129): Base search flags, automatically enhanced with feature flags if <11 results (sdk_wrapper.py:152)
- **why_entities** (sdk_wrapper.py:203): Includes internal features and scoring details
- **how_entity** (sdk_wrapper.py:223): Shows resolution steps with all features

### Environment Configuration

Required:
- `SENZING_ENGINE_CONFIGURATION_JSON`: JSON string with database connection and resource paths

Optional:
- `SENZING_MODULE_NAME`: Module identifier (default: "senzing-mcp")
- `SENZING_INSTANCE_NAME`: Instance name (default: "senzing-mcp-server")
- `SENZING_LOG_LEVEL`: Verbosity (default: 0)

Example SENZING_ENGINE_CONFIGURATION_JSON format:
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

## Key Patterns

### Async Wrapper Pattern
All SDK operations follow this pattern:
1. Check initialization state (sdk_wrapper.py:85)
2. Run sync SDK call in ThreadPoolExecutor via `_run_async()` (sdk_wrapper.py:89)
3. Return result or catch SzError and return JSON error (e.g., sdk_wrapper.py:119)

### Tool Handler Pattern
Server tool handlers (server.py:172):
1. Ensure SDK is initialized (server.py:176)
2. Extract arguments from tool call
3. Transform arguments to SDK format (e.g., JSON strings for entity lists)
4. Call async wrapper method
5. Return TextContent with result or error

### Initialization Flow
1. Server starts via `run()` entry point (server.py:274)
2. `main()` calls `sdk_wrapper.initialize()` (server.py:251)
3. Wrapper loads config from env vars and initializes factory (sdk_wrapper.py:46)
4. Factory creates all SDK components (sdk_wrapper.py:75-78)
5. Server starts stdio transport and runs MCP protocol (server.py:255)

## Deployment Guide

### Portable Configuration

The codebase is designed to be portable across different servers. Each deployment requires proper environment configuration in the MCP client:

**Server-side (where Senzing is installed):**
1. Clone the repository
2. Make launch script executable: `chmod +x launch_senzing_mcp.sh`

**For LOCAL deployment (AI assistant and Senzing on same machine):**
1. Point your AI assistant's MCP config to `launch_senzing_mcp.sh`
2. Set environment variables in the MCP config's `env` section:
   - `SENZING_ENGINE_CONFIGURATION_JSON` (required)
   - `LD_LIBRARY_PATH` (required)
   - `PYTHONPATH` (required)

**For REMOTE deployment (AI assistant on different machine):**
1. Copy `launch_senzing_mcp_ssh.sh` to your client machine
2. Edit configuration: set remote host, user, SSH key, and path to `launch_senzing_mcp.sh` on remote server
3. Update AI assistant's MCP config to point to `launch_senzing_mcp_ssh.sh`
4. Set environment variables in the MCP config's `env` section (same as local deployment)

### How MCP Servers Work

The AI assistant spawns the MCP server as a subprocess for each session:
- **Local**: AI runs `launch_senzing_mcp.sh` with environment variables from MCP config's `env` section
- **Remote**: AI runs `launch_senzing_mcp_ssh.sh` which passes environment variables via SSH to the remote server
- Communication happens via stdio (stdin/stdout) using JSON-RPC
- The server terminates when the AI session ends

**Important**: Environment variables must be set in the MCP configuration's `env` section. The MCP client passes these to the launch script, which then passes them to the Python server process.

## AI Assistant Integration

The MCP server is designed to be called by AI assistants through their MCP client implementations:

- **Claude Desktop/Code**: Detailed configuration in README.md
- **Other AI Assistants**: Generic MCP configuration pattern documented in README.md
- **Remote Setup**: SSH-based approach documented in `launch_senzing_mcp_ssh.sh` comments

## Project Structure

```
senzing-mcp-server/
├── src/senzing_mcp/
│   ├── server.py          # MCP server with 7 tool definitions
│   ├── sdk_wrapper.py     # Async Senzing SDK wrapper
│   └── __init__.py
├── examples/              # Test client for MCP server
│   ├── senzing_test.py    # Unified CLI for all 7 tools
│   └── README.md          # Test client documentation
├── pyproject.toml         # Python package config
├── requirements.txt       # Python dependencies
├── RESPONSE_FORMATTING.md # Guidelines for presenting HOW/WHY results
└── README.md              # Main documentation
```

## Common Issues

**SDK Import Errors**: Ensure `LD_LIBRARY_PATH` and `PYTHONPATH` are correctly set in your MCP config's `env` section. These are required for the Senzing SDK to load properly.

**Environment Not Set**: If you get "SENZING_ENGINE_CONFIGURATION_JSON is not set" error, add the environment variables to your MCP config's `env` section:
  ```json
  {
    "mcpServers": {
      "senzing": {
        "command": "/path/to/launch_senzing_mcp.sh",
        "env": {
          "SENZING_ENGINE_CONFIGURATION_JSON": "{\"PIPELINE\":{\"CONFIGPATH\":\"/etc/opt/senzing\",...}}",
          "LD_LIBRARY_PATH": "/opt/senzing/lib",
          "PYTHONPATH": "/opt/senzing/sdk/python"
        }
      }
    }
  }
  ```

**Initialization Failures**: Check `SENZING_ENGINE_CONFIGURATION_JSON` is valid JSON with correct paths and database connection.

**Async Errors**: The SDK is synchronous but wrapped in async - ensure all SDK calls go through `_run_async()` method.

**Tool Call Failures**: Server logs errors but returns them as JSON - check stderr for detailed exception info.
