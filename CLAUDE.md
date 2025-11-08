# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an MCP (Model Context Protocol) server that exposes Senzing SDK entity resolution capabilities to AI assistants like Claude, ChatGPT, and Amazon Q Developer. The server wraps the synchronous Senzing Python SDK with an async interface and provides 7 read-only tools for entity search and relationship analysis.

**Key Concepts:**
- **Entity ID**: Senzing's internal identifier (small integers like 1, 2, 3...) assigned after entity resolution
- **Record ID**: Your source system's identifier (like "1001", "1002") in a specific data source (like "CUSTOMERS")
- Most tools require Entity IDs. Use `search` or `get_source_record` to find Entity IDs first.

**Important**: When interpreting HOW and WHY results from `how_entity_resolved` and `explain_why_entities_related` tools, follow the formatting guidelines in `RESPONSE_FORMATTING.md` for clear, professional presentation of entity resolution explanations.

## Development Commands

### Installation
```bash
# Clone repository to your server
git clone https://github.com/yourusername/senzing-mcp-server.git
cd senzing-mcp-server

# Ensure your .bashrc has Senzing environment variables:
# - SENZING_ENGINE_CONFIGURATION_JSON (required)
# - LD_LIBRARY_PATH including Senzing libraries
# - PYTHONPATH including Senzing Python SDK

# Install in development mode
pip install -e .

# The server command becomes available after installation
senzing-mcp
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
# Test scripts are in examples/ directory
python examples/quick_test.py              # List available tools
python examples/search_entity.py "Name"    # Search entities
python examples/get_entity.py 1            # Get entity by ID
```

## Architecture

### Core Components

**src/senzing_mcp/server.py** (server.py:1)
- MCP server implementation using the `mcp` package
- Defines 7 read-only tools exposed to AI assistants
- Tool categories:
  - Entity search/retrieval: `search`, `get_entity`, `get_source_record`
  - Relationship analysis: `find_relationship_path`, `expand_entity_network`, `explain_why_entities_related`, `how_entity_resolved`
- Uses stdio transport for Claude Desktop integration
- All tool calls are routed through `call_tool()` handler

**src/senzing_mcp/sdk_wrapper.py** (sdk_wrapper.py:1)
- Async wrapper around synchronous Senzing SDK
- Uses ThreadPoolExecutor for non-blocking SDK calls (sdk_wrapper.py:37)
- Initialization from environment variables (sdk_wrapper.py:40)
- Key pattern: All SDK methods are wrapped with `_run_async()` to execute in thread pool (sdk_wrapper.py:83)
- Factory pattern initialization through SzAbstractFactoryCore (sdk_wrapper.py:68)

### SDK Integration

The Senzing SDK must be initialized in the environment before the MCP server starts. The launch scripts handle this by sourcing the user's .bashrc file, which should contain Senzing initialization.

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

Example configuration from .env.example:
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

The codebase is designed to be portable across different servers. Each deployment requires proper environment setup:

**Server-side (where Senzing is installed):**
1. Add Senzing initialization to your .bashrc file:
   - Set `SENZING_ENGINE_CONFIGURATION_JSON` with database connection and paths
   - Add Senzing libraries to `LD_LIBRARY_PATH`
   - Add Senzing Python SDK to `PYTHONPATH`
2. Clone the repository
3. Run `pip install -e .`
4. Optionally edit `launch_senzing_mcp.sh` if venv path differs from default

**For LOCAL deployment (AI assistant and Senzing on same machine):**
1. Point your AI assistant's MCP config directly to `launch_senzing_mcp.sh`
2. The script will source your .bashrc to load environment variables

**For REMOTE deployment (AI assistant on different machine):**
1. Copy `launch_senzing_mcp_ssh.sh` to your client machine
2. Edit configuration: set remote host, user, SSH key, and path to `launch_senzing_mcp.sh` on remote server
3. Update AI assistant's MCP config to point to `launch_senzing_mcp_ssh.sh`

### How MCP Servers Work

The AI assistant spawns the MCP server as a subprocess for each session:
- **Local**: AI runs `launch_senzing_mcp.sh` which sources .bashrc and starts the server
- **Remote**: AI runs `launch_senzing_mcp_ssh.sh` which SSH's to remote and calls `launch_senzing_mcp.sh` there
- Communication happens via stdio (stdin/stdout) using JSON-RPC
- The server terminates when the AI session ends

**Important**: Subprocesses do NOT automatically inherit .bashrc environment variables, which is why `launch_senzing_mcp.sh` explicitly sources it. Never point MCP config directly to `senzing-mcp` binary - always use the launch script.

## AI Assistant Integration

The MCP server is designed to be called by AI assistants through their MCP client implementations:

- **Claude Desktop**: Add to `claude_desktop_config.json` with command `senzing-mcp` (local) or path to SSH launcher (remote)
- **ChatGPT Desktop**: Uses `chatgpt_mcp_config.json` with similar configuration
- **Amazon Q Developer**: See AMAZON_Q_SETUP.md for VS Code extension setup
- **Remote Setup**: SSH tunneling approach documented in MAC_SETUP_INSTRUCTIONS.md

Configuration files in repo root show example setups for each platform.

## Project Structure

```
senzing-mcp-server/
├── src/senzing_mcp/
│   ├── server.py          # MCP server with 11 tool definitions
│   ├── sdk_wrapper.py     # Async Senzing SDK wrapper
│   └── __init__.py
├── examples/              # Test scripts using MCP client
│   ├── quick_test.py      # List available tools
│   ├── search_entity.py   # Search example
│   └── get_entity.py      # Get entity example
├── pyproject.toml         # Python package config
├── .env.example           # Environment template
├── RESPONSE_FORMATTING.md # Guidelines for presenting HOW/WHY results
└── *.md                   # Setup docs for different platforms
```

## Common Issues

**SDK Import Errors**: Ensure Senzing environment is initialized in your .bashrc file. The launch script sources .bashrc to get environment variables.

**Environment Not Set**: If you get "SENZING_ENGINE_CONFIGURATION_JSON is not set" error, add Senzing initialization to your .bashrc:
  ```bash
  export SENZING_ENGINE_CONFIGURATION_JSON='{"PIPELINE":{"CONFIGPATH":"/etc/opt/senzing",...}}'
  export LD_LIBRARY_PATH="/path/to/senzing/lib:$LD_LIBRARY_PATH"
  export PYTHONPATH="/path/to/senzing/sdk/python:$PYTHONPATH"
  ```

**Initialization Failures**: Check `SENZING_ENGINE_CONFIGURATION_JSON` is valid JSON with correct paths and database connection.

**Async Errors**: The SDK is synchronous but wrapped in async - ensure all SDK calls go through `_run_async()` method.

**Tool Call Failures**: Server logs errors but returns them as JSON - check stderr for detailed exception info.
