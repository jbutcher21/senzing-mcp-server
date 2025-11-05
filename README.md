# Senzing MCP Server

Model Context Protocol (MCP) server for the Senzing SDK, providing entity resolution capabilities to Claude and other MCP clients.

## Overview

This MCP server exposes Senzing SDK functionality through the Model Context Protocol, enabling AI assistants like Claude to:
- Search for entities by attributes
- Add and manage entity records
- Analyze relationships and networks
- Explain entity resolution decisions
- Perform bulk data imports with multithreading

## Features

### Entity Search & Retrieval
- **search_entities**: Search by name, address, phone, email, etc.
- **get_entity**: Retrieve detailed entity information by ID

### Record Management
- **add_record**: Add single entity records
- **add_records_from_file**: Bulk import from JSONL files with multithreading
- **delete_record**: Remove records from the repository

### Relationship Analysis
- **find_relationship_path**: Discover paths between entities
- **find_network**: Analyze networks of related entities
- **explain_relationship**: Understand why entities are related
- **explain_entity_resolution**: See how entities were resolved

### Configuration & Diagnostics
- **get_stats**: View engine statistics and metrics
- **get_config_info**: Check configuration and version info

## Installation

### Prerequisites

- Python 3.10 or higher
- Senzing SDK v4beta installed at `/data/etl/senzing/er/v4beta/sdk/python`
- Senzing database configured and accessible

### Setup

1. Clone or navigate to the project directory:
```bash
cd /data/etl/senzing/er/v4beta/senzingMCP
```

2. Install the package:
```bash
pip install -e .
```

3. Configure environment variables:
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

## File Format for Bulk Import

The `add_records_from_file` tool expects JSONL format (one JSON object per line):

```jsonl
{"RECORD_ID": "001", "NAME_FULL": "John Smith", "ADDR_FULL": "123 Main St", "PHONE_NUMBER": "555-1234"}
{"RECORD_ID": "002", "NAME_FULL": "Jane Doe", "EMAIL_ADDRESS": "jane@example.com", "DATE_OF_BIRTH": "1990-01-15"}
{"RECORD_ID": "003", "NAME_FULL": "Bob Johnson", "PHONE_NUMBER": "555-5678"}
```

## Architecture

```
senzingMCP/
├── src/
│   └── senzing_mcp/
│       ├── server.py         # MCP server with tool definitions
│       └── sdk_wrapper.py    # Async wrapper for Senzing SDK
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
- Verify Senzing SDK is installed at `/data/etl/senzing/er/v4beta/sdk/python`
- Check that the path is accessible and contains the senzing module

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
