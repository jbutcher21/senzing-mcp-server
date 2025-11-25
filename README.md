# Senzing MCP Server

Model Context Protocol (MCP) server for the Senzing SDK, providing entity resolution capabilities to Claude and other MCP clients.

## Overview

This MCP server exposes Senzing SDK functionality through the Model Context Protocol, enabling AI assistants like Claude to:
- Search for entities by attributes
- Retrieve detailed entity information
- Analyze relationships and networks
- Explain entity resolution decisions (HOW and WHY analysis)

## Features

This is a **read-only** MCP server providing 7 tools for entity resolution analysis:

### Entity Search & Retrieval
- **search_entities**: Search by name, address, phone, email, etc.
- **get_entity**: Retrieve detailed entity information by entity ID
- **get_source_record**: Look up entity by source record ID (e.g., CUSTOMERS:1001)

### Relationship Analysis
- **find_path**: Discover paths between entities
- **expand_network**: Expand networks of related entities to (n) degrees (max 3)
- **explain_why_related**: Explain why two entities are related (WHY analysis)
- **explain_how_resolved**: See how entities were resolved (HOW analysis)

## Installation

### Prerequisites

- Python 3.10 or higher
- Senzing SDK version 4 installed and environment initialized
- Senzing database configured and accessible

### Setup

1. Clone the repository to your server:
```bash
git clone https://github.com/jbutcher21/senzing-mcp-server.git
cd senzing-mcp-server
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Make the launch script executable:
```bash
chmod +x launch_senzing_mcp.sh
```

**Note**: The server runs directly from source after installing dependencies. Environment variables are configured in your AI assistant's MCP configuration (see Configuration section below).

## Usage

### Running the Server

Start the MCP server using the launch script:
```bash
./launch_senzing_mcp.sh
```

Or run directly from source:
```bash
cd src
python -m senzing_mcp.server
```

Or if installed via pip:
```bash
senzing-mcp
```

### Configuration for AI Assistants

This MCP server works with any MCP-compatible AI assistant. Below are detailed instructions for Claude (Desktop and Code), plus guidance for other assistants.

#### Claude Desktop Configuration

Add to your Claude Desktop MCP settings file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "senzing": {
      "command": "/path/to/senzing-mcp-server/launch_senzing_mcp.sh",
      "env": {
        "SENZING_ENGINE_CONFIGURATION_JSON": "{\"PIPELINE\": {\"CONFIGPATH\": \"/etc/opt/senzing\", \"RESOURCEPATH\": \"/opt/senzing/g2/resources\", \"SUPPORTPATH\": \"/opt/senzing/data\"}, \"SQL\": {\"CONNECTION\": \"sqlite3://na:na@/var/opt/senzing/sqlite/G2C.db\"}}",
        "LD_LIBRARY_PATH": "/opt/senzing/lib",
        "PYTHONPATH": "/opt/senzing/sdk/python"
      }
    }
  }
}
```

**Configuration Notes:**
- `command`: Full path to the `launch_senzing_mcp.sh` script
- `SENZING_ENGINE_CONFIGURATION_JSON`: Your Senzing database configuration (must be escaped JSON)
- `LD_LIBRARY_PATH`: Path to Senzing shared libraries
- `PYTHONPATH`: Path to Senzing Python SDK (if not system-wide installed)

**Optional environment variables:**
- `SENZING_MODULE_NAME`: Module identifier (default: "senzing-mcp")
- `SENZING_INSTANCE_NAME`: Instance name (default: "senzing-mcp-server")
- `SENZING_LOG_LEVEL`: Verbosity level (default: 0)

#### Claude Code Configuration

Claude Code (the CLI tool at claude.ai/code) uses the same MCP configuration as Claude Desktop. Configure in your VS Code settings or `~/.config/claude-code/config.json` with the same format as above.

See [Claude Code MCP documentation](https://docs.claude.com/claude-code) for platform-specific details.

#### Other AI Assistants (ChatGPT, Amazon Q, etc.)

This MCP server works with any MCP-compatible assistant. The setup pattern is similar:

1. **Locate your assistant's MCP config file**:
   - ChatGPT Desktop: `~/Library/Application Support/ChatGPT/mcp_config.json` (macOS)
   - Amazon Q Developer: VS Code settings → Amazon Q → MCP Servers
   - See official MCP documentation: https://modelcontextprotocol.io

2. **Add server configuration** with these key environment variables:
   ```json
   {
     "mcpServers": {
       "senzing": {
         "command": "/path/to/senzing-mcp-server/launch_senzing_mcp.sh",
         "env": {
           "SENZING_ENGINE_CONFIGURATION_JSON": "{...}",
           "LD_LIBRARY_PATH": "/opt/senzing/lib",
           "PYTHONPATH": "/opt/senzing/sdk/python"
         }
       }
     }
   }
   ```

3. **Restart your AI assistant** to load the MCP server

**Remote Setup**: For SSH-based remote server access, see [MAC_SETUP_INSTRUCTIONS.md](MAC_SETUP_INSTRUCTIONS.md) for an example pattern.

### Example Queries in Claude

Once configured, you can ask Claude natural language questions using any of the 7 read-only tools:

#### Entity Search & Retrieval

```
Search for entities with the name "John Smith" and phone "555-1234"
```

```
Get the full details for entity 1234
```

```
Show me the entity for customer record 1001 in the CUSTOMERS data source
```

#### Relationship Analysis

```
Find the relationship path between entity 100 and entity 200
```

```
Expand the network of related entities starting from entity 50, up to 2 degrees
```

#### Entity Resolution Explanations

```
Explain why entities 100 and 200 are related (or not merged together)
```

```
Show me how entity 1234 was resolved - what records merged and why
```

## Response Formatting Guide

For better interpretation of HOW and WHY analysis results, this repository includes a **Response Formatting Guide** (`RESPONSE_FORMATTING.md`) that helps AI assistants present entity resolution explanations in a clear, professional format.

### What It Does

The formatting guide provides instructions for:
- **HOW Analysis** (`explain_how_resolved`): Step-by-step entity resolution explanations with merge steps and match drivers
- **WHY Analysis** (`explain_why_related`): Side-by-side entity comparisons showing confirmations and conflicts

### How to Use with Your AI Assistant

The MCP server returns raw JSON data. To get nicely formatted explanations, provide the formatting guide to your AI assistant:

#### Option 1: Include in Conversation (All AI Assistants)

When asking about entity resolution, add:
```
Please format the results according to the guidelines in RESPONSE_FORMATTING.md
```

Then paste the contents of `RESPONSE_FORMATTING.md` or provide it as an uploaded file.

#### Option 2: Add to Project Instructions (Claude Desktop/Projects)

1. Open your Claude project or conversation
2. Add `RESPONSE_FORMATTING.md` to project knowledge
3. Claude will automatically apply formatting rules to all HOW/WHY results

#### Option 3: Custom Instructions (ChatGPT/Other AI)

1. Copy the content from `RESPONSE_FORMATTING.md`
2. Add to your AI assistant's custom instructions or system prompt
3. The AI will automatically format Senzing results

#### Option 4: For Amazon Q Developer

1. Include `RESPONSE_FORMATTING.md` in your workspace
2. Reference it when asking about entity resolution:
   ```
   @workspace Please explain how entity 100 was resolved, using the formatting from RESPONSE_FORMATTING.md
   ```

### Example: Before vs After Formatting

**Without formatting guide:**
```json
{"HOW_RESULTS":{"RESOLUTION_STEPS":[{"STEP":1,"VIRTUAL_ENTITY_1":...}]}
```

**With formatting guide:**
```
## Summary
Entity 1234 was resolved from 4 CUSTOMERS records through 3 merge steps.
Primary match drivers: Email address and phone number matches.

## Resolution Steps
Step 1: Merged CUSTOMERS:1001 with CUSTOMERS:1002
- ✅ EMAIL: user@example.com (Score: 95)
- ✅ PHONE: +1-555-0100 (Score: 90)
...
```

See `RESPONSE_FORMATTING.md` for complete formatting examples and guidelines.

## Architecture

```
senzing-mcp-server/
├── src/
│   └── senzing_mcp/
│       ├── server.py         # MCP server with tool definitions
│       └── sdk_wrapper.py    # Async wrapper for Senzing SDK
├── examples/                 # Example test scripts
├── launch_senzing_mcp.sh     # Server startup script (edit SENZING_ROOT)
├── launch_senzing_mcp_ssh.sh # Client-side SSH launcher
├── senzing_env.sh            # Environment setup helper
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

### Key Components

- **server.py**: MCP server implementation using the official `mcp` package
  - Defines 7 tools for entity resolution operations
  - Handles tool calls and routes to SDK wrapper
  - Uses stdio transport for Claude Desktop integration

- **sdk_wrapper.py**: Async wrapper for synchronous Senzing SDK
  - Initializes SDK from environment variables
  - Provides async interface using ThreadPoolExecutor
  - Handles error translation
  - Note: Requires Senzing environment to be initialized before import

## Development

### Running Tests

```bash
pytest tests/
```

### Debugging

Set log level for more verbose output:
```bash
export SENZING_LOG_LEVEL=1
senzing-mcp
```

### Common Issues

**SDK Initialization Failed**
- Check that `SENZING_ENGINE_CONFIGURATION_JSON` is properly formatted
- Verify database connection settings
- Ensure Senzing resources are accessible at specified paths

**Import Path Issues**
- Verify `LD_LIBRARY_PATH` and `PYTHONPATH` are set correctly in your MCP config's `env` section
- Check that you can import senzing modules with environment variables set:
  ```bash
  LD_LIBRARY_PATH=/opt/senzing/lib PYTHONPATH=/opt/senzing/sdk/python \
    python -c "import senzing"
  ```

## License

This MCP server implementation is provided as-is. Senzing SDK usage is subject to Senzing licensing terms.

## Support

For issues with:
- **MCP Server**: Check server logs and environment configuration
- **Senzing SDK**: Consult Senzing documentation
- **Claude Integration**: Verify MCP configuration in Claude Desktop settings
