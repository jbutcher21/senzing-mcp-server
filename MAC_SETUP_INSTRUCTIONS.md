# Remote Senzing MCP Server Setup (Mac to Linux via SSH)

## Overview

This guide configures ChatGPT Desktop on your Mac to connect to the Senzing MCP server running on a remote Linux server via SSH.

## Prerequisites

- ChatGPT Desktop App installed on your Mac
- SSH access to your remote server as your username
- SSH key at `~/.ssh/id_rsa` on your Mac (or your preferred SSH key path)

## Setup Steps

### 1. Test SSH Connection First

Before proceeding, verify you can SSH to the remote server:

```bash
ssh -i ~/.ssh/id_rsa your-username@remote-server-ip "echo 'SSH connection works'"
```

If this fails, you may need to:
- Add your SSH key: `ssh-add ~/.ssh/id_rsa`
- Or configure SSH config file (see "SSH Configuration" section below)

### 2. Copy Launch Script to Your Mac

On your **Mac**, create a directory and copy the launch script:

```bash
# Create directory
mkdir -p ~/senzing-mcp

# Copy the SSH launch script from the remote server
scp your-username@remote-server-ip:/path/to/senzing-mcp-server/launch_senzing_mcp_ssh.sh \
    ~/senzing-mcp/

# Make it executable
chmod +x ~/senzing-mcp/launch_senzing_mcp_ssh.sh
```

### 3. Configure ChatGPT Desktop

Create the ChatGPT MCP configuration directory and file:

```bash
# Create the configuration directory
mkdir -p ~/Library/Application\ Support/ChatGPT/

# Create the MCP configuration file
cat > ~/Library/Application\ Support/ChatGPT/mcp_config.json << 'EOF'
{
  "mcpServers": {
    "senzing": {
      "command": "/Users/your-username/senzing-mcp/launch_senzing_mcp_ssh.sh",
      "description": "Senzing Entity Resolution MCP Server (via SSH to remote server)",
      "env": {
        "SENZING_ENGINE_CONFIGURATION_JSON": "{\"PIPELINE\":{\"CONFIGPATH\":\"/etc/opt/senzing\",\"RESOURCEPATH\":\"/opt/senzing/g2/resources\",\"SUPPORTPATH\":\"/opt/senzing/data\"},\"SQL\":{\"CONNECTION\":\"sqlite3://na:na@/var/opt/senzing/sqlite/G2C.db\"}}",
        "LD_LIBRARY_PATH": "/opt/senzing/lib",
        "PYTHONPATH": "/opt/senzing/sdk/python"
      }
    }
  }
}
EOF
```

**Important**: Update the environment variables above to match your remote server's Senzing installation paths. The SSH launcher script will pass these to the remote server.

### 4. Restart ChatGPT Desktop

1. Quit ChatGPT Desktop completely
2. Relaunch ChatGPT Desktop
3. The Senzing MCP server should now be available

## Verification

### Test the Launch Script Manually

Before using with ChatGPT, test the launch script:

```bash
~/senzing-mcp/launch_senzing_mcp_ssh.sh
```

You should see log messages indicating the Senzing MCP server started. Press Ctrl+C to stop.

### Test in ChatGPT

Open ChatGPT and try these queries:

1. "What MCP servers are available?" - Should show "senzing"
2. "Search for entities named Robert Smith" - Should return entity results
3. "Get details for entity 1" - Should return comprehensive entity data

## SSH Configuration (Optional but Recommended)

To avoid specifying the SSH key path every time, add this to `~/.ssh/config`:

```
Host senzing-server
    HostName remote-server-ip
    User your-username
    IdentityFile ~/.ssh/id_rsa
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Then update the launch script to use: `ssh senzing-server` instead of the full command.

## Troubleshooting

### "Permission denied" SSH Error

```bash
# Add your SSH key to the agent
ssh-add ~/.ssh/id_rsa

# Verify the key is added
ssh-add -l
```

### "Connection refused" or Timeout

- Verify the server is reachable: `ping remote-server-ip`
- Check firewall settings on remote server
- Ensure SSH is running on the remote server

### MCP Server Not Appearing in ChatGPT

1. Check the configuration file exists:
   ```bash
   cat ~/Library/Application\ Support/ChatGPT/mcp_config.json
   ```

2. Verify the launch script path is correct:
   ```bash
   ls -l ~/senzing-mcp/launch_senzing_mcp_ssh.sh
   ```

3. Test the launch script manually (see Verification section)

### ChatGPT Shows Connection Errors

1. Check ChatGPT logs (if available)
2. Test SSH connection manually
3. Verify the environment variables are correctly set in your MCP config:
   ```bash
   cat ~/Library/Application\ Support/ChatGPT/mcp_config.json | grep -A 5 '"env"'
   ```
4. Test that the SSH launcher passes environment variables correctly:
   ```bash
   SENZING_ENGINE_CONFIGURATION_JSON='{"PIPELINE":...}' \
   LD_LIBRARY_PATH=/opt/senzing/lib \
   PYTHONPATH=/opt/senzing/sdk/python \
     ~/senzing-mcp/launch_senzing_mcp_ssh.sh
   ```

### Slow Response Times

The SSH connection may add latency. This is normal for remote MCP servers. Each query requires:
1. SSH connection establishment
2. Remote script execution
3. Senzing query processing
4. Response transmission back

## Available Tools

The Senzing MCP server provides 7 read-only tools for entity search, retrieval, and relationship analysis. See the main [README](README.md#features) for complete tool descriptions.

## Example Queries for ChatGPT

- "Search for all entities with the name John Smith"
- "Get the complete details for entity ID 1"
- "Show me how entity 1 was resolved from its source records"
- "Find the relationship path between entity 1 and entity 8"
- "Explain why entity 1 and entity 8 are related"
- "Find the network of entities related to entity 20"
- "What are the Senzing statistics?"

## Response Formatting for HOW/WHY Analysis

For better formatted explanations of entity resolution, you can provide ChatGPT with formatting instructions:

**Option 1: Add to Custom Instructions**
1. Go to ChatGPT Settings → Personalization → Custom Instructions
2. Copy the contents of `RESPONSE_FORMATTING.md` from the senzing-mcp-server repository
3. Paste into "How would you like ChatGPT to respond?"
4. ChatGPT will automatically format all Senzing HOW/WHY results

**Option 2: Include in Conversation**
When asking about entity resolution:
```
Please format the results according to RESPONSE_FORMATTING.md
```
Then provide the contents from the repository.

**Result:**
Clear summaries with step-by-step breakdowns, highlighted confirmations (✅) and denials (❌), and side-by-side comparisons instead of raw JSON.

See the main README's "Response Formatting Guide" section for details and examples.

## Security Notes

- The SSH connection uses key-based authentication (more secure than passwords)
- The MCP server is **read-only** - no data modification is possible
- Each ChatGPT session creates a fresh SSH connection
- The server connection is closed when ChatGPT finishes the query

## Files Reference

**On your Mac:**
- Launch script: `~/senzing-mcp/launch_senzing_mcp_ssh.sh`
- ChatGPT config: `~/Library/Application Support/ChatGPT/mcp_config.json`

**On remote server:**
- Remote launch script: `/path/to/senzing-mcp-server/launch_senzing_mcp.sh`
- MCP server source: `/path/to/senzing-mcp-server/src/senzing_mcp/server.py`
- Environment setup: Senzing environment variables passed via SSH from MCP config

**Note**: Before running, ensure Python dependencies are installed on the remote server with `pip install -r requirements.txt` in the senzing-mcp-server directory. The launch script runs the MCP server directly from source. Environment variables are configured in the MCP config on your Mac and passed to the remote server via SSH.
