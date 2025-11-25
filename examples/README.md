# MCP Server Example Scripts

These scripts demonstrate how to interact with the Senzing MCP server directly using the MCP Python client. They're useful for testing your setup and understanding how the MCP server works.

## Prerequisites

Before running these examples, ensure:

1. The MCP server is installed:
   ```bash
   cd /path/to/senzing-mcp-server
   pip install -e .
   ```

2. Senzing environment is configured in your .bashrc:
   ```bash
   # Ensure your .bashrc has:
   # - SENZING_ENGINE_CONFIGURATION_JSON
   # - LD_LIBRARY_PATH including Senzing libraries
   # - PYTHONPATH including Senzing Python SDK
   ```

## Available Examples

### `quick_test.py`

Quick test to verify the MCP server is working and list available tools.

**Usage:**
```bash
./venv/bin/python examples/quick_test.py
```

**What it does:**
- Connects to the MCP server
- Lists all available tools
- Shows tool names and descriptions

### `search_entity.py`

Search for entities by name and display results with features.

**Usage:**
```bash
# Search for a specific name
./venv/bin/python examples/search_entity.py "Robert Smith"

# Default search (Robert Johnson)
./venv/bin/python examples/search_entity.py
```

**What it displays:**
- Entity ID and name
- Match key and score
- Number of records and data sources
- All entity features (ADDRESS, DOB, EMAIL, PHONE, NAME, etc.)

**Example output:**
```
🔍 Searching for entities named 'Robert Smith'...

✅ Found 3 matching entities:

1. Entity ID: 1
   Name: Robert Smith
   Match Key: +NAME
   Match Score: N/A
   Records: 4 from CUSTOMERS
   Features:
      ADDRESS: 1515 Adela Lane Las Vegas NV 89111 (HOME)
      DOB: 11/12/1978
      EMAIL: bsmith@work.com
      PHONE: 702-919-1300 (HOME)
```

### `get_entity.py`

Get comprehensive details for a specific entity by ID.

**Usage:**
```bash
# Get entity by ID
./venv/bin/python examples/get_entity.py 1

# Default entity (ID 1)
./venv/bin/python examples/get_entity.py
```

**What it displays:**
- Complete entity details in formatted JSON
- All records that resolved to this entity
- Features and relationships
- Match information

## How They Work

These scripts use the MCP Python client to:

1. **Start the MCP server** using `StdioServerParameters`
2. **Connect** via stdin/stdout
3. **Initialize** a client session
4. **Call tools** exposed by the MCP server
5. **Parse and display** the JSON results

## Using in Your Own Code

You can use these as templates for your own MCP client applications:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure server
server_params = StdioServerParameters(
    command="/path/to/senzing-mcp-server/venv/bin/senzing-mcp",
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

The server provides these tools you can call:

1. **search_entities** - Search by attributes
2. **get_entity** - Get entity by ID
3. **find_relationship_path** - Find path between entities
4. **find_network** - Discover entity networks
5. **explain_relationship** - Explain why entities are related
6. **explain_entity_resolution** - Explain how entity was resolved
7. **get_stats** - Get engine statistics
8. **get_config_info** - Get configuration info

## Troubleshooting

**Import errors:**
```bash
# Ensure MCP package is installed
pip install mcp
```

**Server not found:**
```bash
# Use absolute path to server
/path/to/senzing-mcp-server/venv/bin/senzing-mcp
```

**Environment errors:**
```bash
# Ensure your .bashrc has Senzing environment variables set
echo $SENZING_ENGINE_CONFIGURATION_JSON
```

## Notes

- These are **test/example scripts** - in production, you'd typically use the MCP server through AI assistants (Claude, ChatGPT, Amazon Q)
- Each script starts a new MCP server instance
- The server automatically handles SDK initialization
- All scripts require the environment to be properly configured
