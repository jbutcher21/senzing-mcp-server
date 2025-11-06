# Senzing MCP Server

Model Context Protocol (MCP) server for the Senzing SDK, providing entity resolution capabilities to Claude and other MCP clients.

## Overview

This MCP server exposes Senzing SDK functionality through the Model Context Protocol, enabling AI assistants like Claude to:
- Search for entities by attributes
- Retrieve detailed entity information
- Analyze relationships and networks
- Explain entity resolution decisions (HOW and WHY analysis)
- View engine statistics and configuration

## Features

This is a **read-only** MCP server providing 8 tools for entity resolution analysis:

### Entity Search & Retrieval
- **search_entities**: Search by name, address, phone, email, etc.
- **get_entity**: Retrieve detailed entity information by ID

### Relationship Analysis
- **find_relationship_path**: Discover paths between entities
- **find_network**: Analyze networks of related entities
- **explain_relationship**: Understand why entities are related (WHY analysis)
- **explain_entity_resolution**: See how entities were resolved (HOW analysis)

### Configuration & Diagnostics
- **get_stats**: View engine statistics and metrics
- **get_config_info**: Check configuration and version info

## Installation

### Prerequisites

- Python 3.10 or higher
- Senzing SDK v4beta installed and environment initialized
- Senzing database configured and accessible

### Setup

1. Clone the repository to your server:
```bash
git clone https://github.com/yourusername/senzing-mcp-server.git
cd senzing-mcp-server
```

2. Install the package:
```bash
pip install -e .
```

3. Configure the launch script for your deployment:
```bash
# Edit launch_senzing_mcp.sh and set SENZING_ROOT to your Senzing installation path
# Example: SENZING_ROOT="/opt/senzing"
nano launch_senzing_mcp.sh
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Senzing configuration
```

Required environment variables:
- `SENZING_ENGINE_CONFIGURATION_JSON`: JSON string with database and resource paths

Optional environment variables:
- `SENZING_MODULE_NAME`: Module identifier (default: "senzing-mcp")
- `SENZING_INSTANCE_NAME`: Instance name (default: "senzing-mcp-server")
- `SENZING_LOG_LEVEL`: Verbosity level (default: 0)

## Usage

### Running the Server

Start the MCP server:
```bash
senzing-mcp
```

Or run directly:
```bash
python -m senzing_mcp.server
```

### Configuration for AI Assistants

This MCP server can be used with multiple AI assistants:

- **Claude Desktop**: See installation instructions below
- **ChatGPT Desktop**: See [CHATGPT_SETUP.md](CHATGPT_SETUP.md)
- **Amazon Q Developer**: See [AMAZON_Q_SETUP.md](AMAZON_Q_SETUP.md)
- **Remote Setup (Mac to Linux)**: See [MAC_SETUP_INSTRUCTIONS.md](MAC_SETUP_INSTRUCTIONS.md)

#### Claude Desktop Configuration

Add to your Claude Desktop MCP settings file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "senzing": {
      "command": "senzing-mcp",
      "env": {
        "SENZING_ENGINE_CONFIGURATION_JSON": "{\"PIPELINE\": {\"CONFIGPATH\": \"/etc/opt/senzing\", \"RESOURCEPATH\": \"/opt/senzing/g2/resources\", \"SUPPORTPATH\": \"/opt/senzing/data\"}, \"SQL\": {\"CONNECTION\": \"sqlite3://na:na@/var/opt/senzing/sqlite/G2C.db\"}}"
      }
    }
  }
}
```

### Example Queries in Claude

Once configured, you can ask Claude:

```
Search for entities with the name "John Smith" and phone "555-1234"
```

```
Add a customer record with ID "CUST-001" containing name "Jane Doe" and email "jane@example.com"
```

```
Find the relationship path between entity 100 and entity 200
```

```
Import records from /path/to/customers.jsonl into the CUSTOMERS data source
```

```
Explain why entities 100 and 200 are related
```

## Response Formatting Guide

For better interpretation of HOW and WHY analysis results, this repository includes a **Response Formatting Guide** (`RESPONSE_FORMATTING.md`) that helps AI assistants present entity resolution explanations in a clear, professional format.

### What It Does

The formatting guide provides instructions for:
- **HOW Analysis** (`explain_entity_resolution`): Step-by-step entity resolution explanations with merge steps and match drivers
- **WHY Analysis** (`explain_relationship`): Side-by-side entity comparisons showing confirmations and conflicts

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

## File Format for Bulk Import

The `add_records_from_file` tool expects JSONL format (one JSON object per line):

```jsonl
{"RECORD_ID": "001", "NAME_FULL": "John Smith", "ADDR_FULL": "123 Main St", "PHONE_NUMBER": "555-1234"}
{"RECORD_ID": "002", "NAME_FULL": "Jane Doe", "EMAIL_ADDRESS": "jane@example.com", "DATE_OF_BIRTH": "1990-01-15"}
{"RECORD_ID": "003", "NAME_FULL": "Bob Johnson", "PHONE_NUMBER": "555-5678"}
```

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
├── .env.example              # Environment template
└── README.md                 # This file
```

### Key Components

- **server.py**: MCP server implementation using the official `mcp` package
  - Defines 11 tools for entity resolution operations
  - Handles tool calls and routes to SDK wrapper
  - Uses stdio transport for Claude Desktop integration

- **sdk_wrapper.py**: Async wrapper for synchronous Senzing SDK
  - Initializes SDK from environment variables
  - Provides async interface using ThreadPoolExecutor
  - Handles error translation and bulk operations
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
- Ensure Senzing environment is initialized in your .bashrc file
- Verify the Senzing SDK Python modules are in your Python path
- Check that you can import senzing modules: `python -c "import senzing"`

**Performance Issues with Bulk Import**
- Adjust `max_workers` parameter (default: 5)
- Monitor system resources during large imports
- Consider breaking very large files into smaller batches

## License

This MCP server implementation is provided as-is. Senzing SDK usage is subject to Senzing licensing terms.

## Support

For issues with:
- **MCP Server**: Check server logs and environment configuration
- **Senzing SDK**: Consult Senzing documentation
- **Claude Integration**: Verify MCP configuration in Claude Desktop settings
