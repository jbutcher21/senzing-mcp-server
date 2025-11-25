# MCP Server Test Client

This directory contains a test client for interacting with the Senzing MCP server directly using the MCP Python SDK. It's useful for testing your setup and understanding how the MCP server works.

## Prerequisites

1. **MCP server installed**:
   ```bash
   cd /path/to/senzing-mcp-server
   pip install -e .
   ```

2. **Senzing environment configured**:
   ```bash
   # Required environment variables:
   export SENZING_ENGINE_CONFIGURATION_JSON='{...}'
   export LD_LIBRARY_PATH=/opt/senzing/lib
   export PYTHONPATH=/opt/senzing/sdk/python
   ```

## Usage

The `senzing_test.py` script provides a unified CLI for testing all 7 MCP tools:

```bash
# List available MCP tools
python senzing_test.py list-tools

# Search for entities by name
python senzing_test.py search "John Smith"

# Get entity details by ID
python senzing_test.py get 1

# Get entity by source record
python senzing_test.py get-record CUSTOMERS 1001

# Find relationship path between entities
python senzing_test.py find-path 1 2
python senzing_test.py find-path 1 2 3  # with max_degrees

# Expand entity network
python senzing_test.py expand 1
python senzing_test.py expand 1 2     # with max_degrees
python senzing_test.py expand 1 2 20  # with max_degrees and max_entities

# Explain why entities are related
python senzing_test.py why 1 2

# Explain how entity was resolved
python senzing_test.py how 1
```

### Built-in Help

Run without arguments to see full usage documentation:

```bash
python senzing_test.py
```

## How It Works

The test client uses the MCP Python SDK to:

1. **Start the MCP server** using `StdioServerParameters`
2. **Connect** via stdin/stdout transport
3. **Initialize** a client session
4. **Call tools** exposed by the MCP server
5. **Parse and display** the JSON results

## Using in Your Own Code

You can use this as a template for your own MCP client applications:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure server
server_params = StdioServerParameters(
    command="senzing-mcp",
    env={
        "SENZING_ENGINE_CONFIGURATION_JSON": config_json,
        "LD_LIBRARY_PATH": ld_library_path
    }
)

# Connect and use
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()

        # Call any MCP tool
        result = await session.call_tool("search_entities", {
            "attributes": {"NAME_FULL": "John Smith"}
        })

        # Process result
        data = json.loads(result.content[0].text)
```

## Available MCP Tools

The server provides these 7 read-only tools:

1. **search_entities** - Search by name, address, phone, email, etc.
2. **get_entity** - Get entity by ID
3. **get_source_record** - Get entity by source record ID (e.g., CUSTOMERS:1001)
4. **find_path** - Find relationship path between entities
5. **expand_network** - Expand networks of related entities
6. **explain_why_related** - Explain why two entities are related (WHY analysis)
7. **explain_how_resolved** - Explain how entity was resolved (HOW analysis)

## Troubleshooting

**Environment errors:**
```bash
# Ensure environment variables are set
echo $SENZING_ENGINE_CONFIGURATION_JSON
echo $LD_LIBRARY_PATH
```

**Server not found:**
```bash
# Use absolute path if senzing-mcp not in PATH
export SENZING_MCP_COMMAND=/path/to/senzing-mcp-server/venv/bin/senzing-mcp
python senzing_test.py list-tools
```

**Import errors:**
```bash
# Ensure MCP package is installed
pip install mcp
```

## Notes

- This is a **test/example client** - in production, you'd typically use the MCP server through AI assistants (Claude, ChatGPT, Amazon Q)
- The script starts a new MCP server instance for each command
- The server automatically handles SDK initialization
- All commands require proper environment configuration
