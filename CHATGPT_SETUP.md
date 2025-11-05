# Setting Up Senzing MCP Server with ChatGPT Desktop

## Prerequisites

- ChatGPT Desktop App installed (with MCP support)
- Senzing MCP server installed in `/data/etl/senzing/er/v4beta/senzingMCP/`

## Installation Steps

### 1. Locate ChatGPT Configuration Directory

The ChatGPT Desktop app stores MCP configuration in:

**macOS:**
```
~/Library/Application Support/ChatGPT/
```

**Windows:**
```
%APPDATA%\ChatGPT\
```

**Linux:**
```
~/.config/ChatGPT/
```

### 2. Create or Update MCP Configuration

1. Navigate to the ChatGPT configuration directory
2. Create or edit the file `mcp_config.json`
3. Copy the contents from `chatgpt_mcp_config.json` in this directory

**Quick command for macOS:**
```bash
# Create the directory if it doesn't exist
mkdir -p ~/Library/Application\ Support/ChatGPT/

# Copy the configuration
cp /data/etl/senzing/er/v4beta/senzingMCP/chatgpt_mcp_config.json \
   ~/Library/Application\ Support/ChatGPT/mcp_config.json
```

### 3. Restart ChatGPT Desktop

Close and restart the ChatGPT Desktop application to load the new MCP server.

## Verification

After restarting ChatGPT, you should see the Senzing MCP server available. To test:

1. Start a new conversation in ChatGPT
2. Ask: "What MCP servers are available?"
3. You should see "senzing" listed
4. Try a query: "Search for entities named Robert Smith"

## Available Tools

The Senzing MCP server provides 8 read-only tools:

1. **search_entities** - Search for entities by attributes (name, address, phone, email, DOB)
2. **get_entity** - Get comprehensive details for a specific entity by ID
3. **find_relationship_path** - Find the connection path between two entities
4. **find_network** - Discover a network of related entities
5. **explain_relationship** - Explain why two entities are related
6. **explain_entity_resolution** - Explain how an entity was resolved from records
7. **get_stats** - Get Senzing engine statistics
8. **get_config_info** - Get configuration information

## Example Queries

- "Search for all entities with the name John Smith"
- "Get the full details for entity ID 1"
- "Show me how entity 1 was resolved"
- "Find the relationship path between entity 1 and entity 8"
- "Explain why entity 1 and entity 8 are related"
- "Find the network of entities related to entity 1"

## Troubleshooting

### MCP Server Not Appearing

1. Check that `mcp_config.json` is in the correct directory
2. Verify the launch script is executable: `ls -la launch_senzing_mcp.sh`
3. Check ChatGPT logs for errors

### Connection Errors

1. Test the launch script manually:
   ```bash
   /data/etl/senzing/er/v4beta/senzingMCP/launch_senzing_mcp.sh
   ```
2. Verify environment variables are set:
   ```bash
   source /data/etl/senzing/er/v4beta/setupEnv
   echo $SENZING_ENGINE_CONFIGURATION_JSON
   ```

### No Data Returned

1. Verify the Senzing database has data
2. Check that setupEnv script properly configured the database path
3. Review logs in ChatGPT application

## Notes

- This is a **read-only** MCP server - no data modification operations are available
- The server starts fresh for each ChatGPT session
- All queries go through the configured Senzing repository
- Environment setup is handled automatically by the launch script
