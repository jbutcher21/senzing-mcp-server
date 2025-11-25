# Setting Up Senzing MCP Server with ChatGPT Desktop

## Prerequisites

- ChatGPT Desktop App installed (with MCP support)
- Senzing MCP server cloned (adjust paths below to match your installation location)

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

### 2. Create MCP Configuration

Create or edit the file `mcp_config.json` in the ChatGPT configuration directory:

**macOS:**
```bash
# Create the directory if it doesn't exist
mkdir -p ~/Library/Application\ Support/ChatGPT/

# Create the configuration file
nano ~/Library/Application\ Support/ChatGPT/mcp_config.json
```

Add the following configuration (adjust paths to match your installation):

```json
{
  "mcpServers": {
    "senzing": {
      "command": "/path/to/senzing-mcp-server/launch_senzing_mcp.sh",
      "env": {
        "SENZING_ENGINE_CONFIGURATION_JSON": "{\"PIPELINE\":{\"CONFIGPATH\":\"/etc/opt/senzing\",\"RESOURCEPATH\":\"/opt/senzing/g2/resources\",\"SUPPORTPATH\":\"/opt/senzing/data\"},\"SQL\":{\"CONNECTION\":\"sqlite3://na:na@/var/opt/senzing/sqlite/G2C.db\"}}",
        "LD_LIBRARY_PATH": "/opt/senzing/lib",
        "PYTHONPATH": "/opt/senzing/sdk/python"
      }
    }
  }
}
```

**Configuration Notes:**
- Replace `/path/to/senzing-mcp-server/` with the actual path where you cloned the repository
- Update `SENZING_ENGINE_CONFIGURATION_JSON` with your database connection details
- Update `LD_LIBRARY_PATH` to point to your Senzing library directory
- Update `PYTHONPATH` to point to your Senzing Python SDK location

**Note**: Before running, ensure you've installed Python dependencies with `pip install -r requirements.txt` in the senzing-mcp-server directory. The launch script runs directly from source. All environment variables are set in the MCP configuration above.

### 3. Restart ChatGPT Desktop

Close and restart the ChatGPT Desktop application to load the new MCP server.

## Verification

After restarting ChatGPT, you should see the Senzing MCP server available. To test:

1. Start a new conversation in ChatGPT
2. Ask: "What MCP servers are available?"
3. You should see "senzing" listed
4. Try a query: "Search for entities named Robert Smith"

## Available Tools

The Senzing MCP server provides 7 read-only tools for entity search, retrieval, and relationship analysis. See the main [README](README.md#features) for complete tool descriptions.

## Example Queries

- "Search for all entities with the name John Smith"
- "Get the full details for entity ID 1"
- "Show me how entity 1 was resolved"
- "Find the relationship path between entity 1 and entity 8"
- "Explain why entity 1 and entity 8 are related"
- "Find the network of entities related to entity 1"

## Response Formatting for HOW/WHY Analysis

For better formatted explanations of entity resolution, you can provide ChatGPT with formatting instructions:

**Option 1: Add to Custom Instructions**
1. Go to ChatGPT Settings → Personalization → Custom Instructions
2. Copy the contents of `RESPONSE_FORMATTING.md` from the repository
3. Paste into "How would you like ChatGPT to respond?"
4. ChatGPT will automatically format all Senzing HOW/WHY results

**Option 2: Include in Conversation**
When asking about entity resolution, add:
```
Please format the results according to RESPONSE_FORMATTING.md
```
Then paste the contents of the formatting guide or upload the file.

**Result:**
Instead of raw JSON, you'll get clear summaries with step-by-step breakdowns, highlighted confirmations (✅) and denials (❌), and side-by-side comparisons.

See the main README's "Response Formatting Guide" section for more details and examples.

## Troubleshooting

### MCP Server Not Appearing

1. Check that `mcp_config.json` is in the correct directory
2. Verify the launch script is executable: `ls -la launch_senzing_mcp.sh`
3. Check ChatGPT logs for errors

### Connection Errors

1. Test the launch script manually with environment variables:
   ```bash
   LD_LIBRARY_PATH=/opt/senzing/lib \
   PYTHONPATH=/opt/senzing/sdk/python \
   SENZING_ENGINE_CONFIGURATION_JSON='{"PIPELINE":...}' \
     /path/to/senzing-mcp-server/launch_senzing_mcp.sh
   ```
2. Verify environment variables are correctly set in your MCP config:
   ```bash
   cat ~/Library/Application\ Support/ChatGPT/mcp_config.json | grep -A 5 '"env"'
   ```

### No Data Returned

1. Verify the Senzing database has data
2. Check that your `SENZING_ENGINE_CONFIGURATION_JSON` in the MCP config points to the correct database
3. Review logs in ChatGPT application

## Notes

- This is a **read-only** MCP server - no data modification operations are available
- The server starts fresh for each ChatGPT session
- All queries go through the configured Senzing repository
- Environment variables are passed from the MCP configuration to the server
