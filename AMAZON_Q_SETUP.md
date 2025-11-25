# Setting Up Senzing MCP Server with Amazon Q Developer

## Prerequisites

- Amazon Q Developer with MCP support (available in IDE plugins as of June 2025)
- AWS Cloud9, AWS Code Server (VS Code Server), or other AWS cloud-based IDE
- Senzing MCP server cloned and installed (see Installation section below)
- Senzing SDK installed and accessible from your environment
- AWS credentials configured (if applicable)

## Overview

Amazon Q Developer supports MCP (Model Context Protocol) servers, allowing you to extend Q's capabilities with custom tools. This guide covers setup in AWS cloud-based IDEs including AWS Code Server (browser-based VS Code).

## Installation

### Install the MCP Server

First, set up the Senzing MCP server on your AWS instance:

```bash
# Clone the repository
git clone https://github.com/jbutcher21/senzing-mcp-server.git
cd senzing-mcp-server

# Make launch script executable
chmod +x launch_senzing_mcp.sh
```

**Note**: No pip install required - the launch script runs directly from source. All environment variables are configured in the MCP client's configuration (see below).

## Quick Start - Recommended Method (GUI)

The easiest way to configure Amazon Q Developer with the Senzing MCP server is through the GUI:

1. **Set up the MCP server** on your instance (see Installation section below)

2. **Open Amazon Q Chat** in your IDE (VS Code/Code Server)

3. **Click the tools icon** (⚙️) in the Amazon Q Chat panel

4. **Add MCP Server:**
   - Click "Add Server" or "+"
   - Choose **STDIO** transport
   - Fill in the details:
     - **Command:** Full path to `launch_senzing_mcp.sh` (e.g., `/home/ubuntu/senzing-mcp-server/launch_senzing_mcp.sh`)
     - **Environment Variables:** Add the following (required):
       - `SENZING_ENGINE_CONFIGURATION_JSON`: Your Senzing config JSON (see example below)
       - `LD_LIBRARY_PATH`: Path to Senzing libraries (e.g., `/opt/senzing/er/lib`)
       - `PYTHONPATH`: Path to Senzing Python SDK (e.g., `/opt/senzing/sdk/python`) if not system-wide
     - **Timeout:** `60000` (milliseconds)

5. **Set tool permissions** (Ask, Always allow, or Deny) for each Senzing tool

6. **Test:** Ask Amazon Q "What MCP tools are available?"

### Environment Variable Example

For `SENZING_ENGINE_CONFIGURATION_JSON`, use your actual Senzing configuration:
```json
{"PIPELINE":{"CONFIGPATH":"/etc/opt/senzing","RESOURCEPATH":"/opt/senzing/er/resources","SUPPORTPATH":"/opt/senzing/data"},"SQL":{"CONNECTION":"sqlite3://na:na@/home/ubuntu/sz_sqlite/G2C.db"}}
```

**Note:** This must be a single-line JSON string with escaped quotes if needed.

## Alternative: Manual Configuration (JSON File)

If you prefer manual configuration, Amazon Q Developer stores MCP configurations in:

**Global Configuration File:**
```bash
~/.aws/amazonq/agents/default.json
```

### Manual Configuration Steps

#### 1. Create the configuration file:

```bash
# Create directory if it doesn't exist
mkdir -p ~/.aws/amazonq/agents

# Edit the configuration
nano ~/.aws/amazonq/agents/default.json
```

#### 2. Add your MCP server configuration:

```json
{
  "mcpServers": {
    "senzing": {
      "command": "/home/ubuntu/senzing-mcp-server/launch_senzing_mcp.sh",
      "disabled": false,
      "timeout": 60000,
      "env": {
        "SENZING_ENGINE_CONFIGURATION_JSON": "{\"PIPELINE\":{\"CONFIGPATH\":\"/etc/opt/senzing\",\"RESOURCEPATH\":\"/opt/senzing/er/resources\",\"SUPPORTPATH\":\"/opt/senzing/data\"},\"SQL\":{\"CONNECTION\":\"sqlite3://na:na@/home/ubuntu/sz_sqlite/G2C.db\"}}",
        "LD_LIBRARY_PATH": "/opt/senzing/er/lib",
        "PYTHONPATH": "/opt/senzing/sdk/python"
      }
    }
  }
}
```

**Important Notes:**
- Use the **full absolute path** to your `launch_senzing_mcp.sh` script
- The `SENZING_ENGINE_CONFIGURATION_JSON` must be a **single-line escaped JSON string**
- Adjust paths to match your installation
- Set `disabled: false` to enable the server
- `timeout` is in milliseconds (60000 = 60 seconds)

#### 3. Reload Amazon Q Developer

After creating or modifying the configuration file, reload Amazon Q:

**For VS Code / Code Server:**
1. Open Command Palette: `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type: `Developer: Reload Window`
3. Press Enter

**Note**: For browser-based Code Server, this reloads the VS Code window but won't close your browser tab or disconnect your session.

### Option 2: AWS CodeCatalyst Setup

If using AWS CodeCatalyst:

1. **Create a Dev Environment Configuration**

Add to your `.codecatalyst/workflows/mcp-config.yaml`:

```yaml
mcpServers:
  senzing:
    command: /path/to/senzing-mcp-server/launch_senzing_mcp.sh
    env:
      SENZING_ENGINE_CONFIGURATION_JSON: '{"PIPELINE":{"CONFIGPATH":"/etc/opt/senzing","RESOURCEPATH":"/opt/senzing/er/resources","SUPPORTPATH":"/opt/senzing/data"},"SQL":{"CONNECTION":"sqlite3://na:na@/var/opt/senzing/sqlite/G2C.db"}}'
      LD_LIBRARY_PATH: /opt/senzing/er/lib
      PYTHONPATH: /opt/senzing/sdk/python
```

2. **Configure in IDE Settings**

Open Settings → Extensions → Amazon Q Developer → MCP Servers and add:
- **Name**: senzing
- **Command**: `/path/to/senzing-mcp-server/launch_senzing_mcp.sh` (use your actual path)
- **Environment Variables**: Set SENZING_ENGINE_CONFIGURATION_JSON, LD_LIBRARY_PATH, and PYTHONPATH as shown above

3. **Reload Amazon Q Developer**

Use one of the reload methods described in Option 1 above.

### Option 3: Remote SSH Configuration

If connecting from Code Server on one AWS instance to a remote Senzing server via SSH:

1. **Configure SSH Access**

Ensure you can SSH from your Code Server instance to the Senzing server:

```bash
# Test SSH connection
ssh -i ~/.ssh/id_rsa user@senzing-server.example.com "echo 'SSH works'"
```

2. **Copy and Configure SSH Launch Wrapper**

```bash
# Copy the SSH launcher from the repository
cp launch_senzing_mcp_ssh.sh ~/launch_senzing_mcp_ssh.sh
chmod +x ~/launch_senzing_mcp_ssh.sh

# Edit to update your server details
nano ~/launch_senzing_mcp_ssh.sh
```

Update the configuration section at the top:
```bash
REMOTE_HOST="your-senzing-server.example.com"
REMOTE_USER="your-username"
SSH_KEY="$HOME/.ssh/id_rsa"
REMOTE_SCRIPT="/path/to/senzing-mcp-server/launch_senzing_mcp.sh"
```

3. **Configure Amazon Q**

Create the MCP config pointing to your SSH launcher:

```bash
mkdir -p ~/.amazon-q/mcp
cat > ~/.amazon-q/mcp/config.json << 'EOF'
{
  "mcpServers": {
    "senzing": {
      "command": "/home/ec2-user/launch_senzing_mcp_ssh.sh",
      "args": []
    }
  }
}
EOF
```

4. **Reload Amazon Q Developer**

Use one of the reload methods described in Option 1 above.

## Verification

After setup and reloading Amazon Q Developer, verify the MCP server is connected:

1. **Check MCP Server Status**
   - Open Amazon Q Developer chat panel in your IDE
   - Ask: **"What MCP tools are available?"**
   - You should see 8-11 Senzing tools listed

2. **Test a Query**
   - Try: **"Search for entities named Robert Smith"**
   - Or: **"Get statistics from Senzing"**

3. **Verify Config File**
   ```bash
   # Check the config file exists and is correct
   cat ~/.amazon-q/mcp/config.json
   ```

**Expected Output**: Amazon Q should respond with Senzing entity data or statistics, confirming the MCP server is working.

## Available Tools

The Senzing MCP server provides 7 read-only tools for entity search, retrieval, and relationship analysis. See the main [README](README.md#features) for complete tool descriptions.

## Example Queries for Amazon Q

Once configured, you can ask Amazon Q Developer:

### Entity Search
```
"Search for all entities named John Smith in the Senzing repository"
"Find entities with phone number 555-1234"
"Search for entities with email ending in @example.com"
```

### Entity Analysis
```
"Get complete details for entity ID 1"
"Show me how entity 1 was created from multiple records"
"What features does entity 150 have?"
```

### Relationship Queries
```
"Find the relationship path between entity 1 and entity 8"
"Why are entities 1 and 8 related?"
"Show me the network of entities connected to entity 1 within 2 degrees"
```

### Statistics and Configuration
```
"What are the current Senzing statistics?"
"Show me the active configuration ID"
"How many entities are in the repository?"
```

## Response Formatting for HOW/WHY Analysis

Amazon Q Developer can provide better formatted explanations of entity resolution if you reference the formatting guide:

**Include in your workspace:**
1. Ensure `RESPONSE_FORMATTING.md` is in your project directory
2. When asking about entity resolution, use `@workspace`:

```
@workspace Please explain how entity 100 was resolved, using the formatting from RESPONSE_FORMATTING.md
```

```
@workspace Why are entities 100 and 200 related? Format according to RESPONSE_FORMATTING.md
```

Amazon Q will then format the HOW/WHY results with clear summaries, step-by-step breakdowns, and highlighted confirmations/denials instead of showing raw JSON.

See the main README's "Response Formatting Guide" section for more details and examples.

## Troubleshooting

### MCP Server Not Appearing

1. **Check Configuration File Location**
   ```bash
   # Verify config exists and has correct path
   cat ~/.amazon-q/mcp/config.json
   ```

2. **Verify Launch Script is Executable**
   ```bash
   # Replace /path/to with your actual installation path
   ls -la /path/to/senzing-mcp-server/launch_senzing_mcp.sh
   chmod +x /path/to/senzing-mcp-server/launch_senzing_mcp.sh
   ```

3. **Reload Amazon Q Developer**
   - Use Command Palette → `Developer: Reload Window`
   - Or restart the extension as described in Configuration Steps above

4. **Check Amazon Q Developer Logs**
   - Open IDE Output panel (View → Output)
   - Select "Amazon Q Developer" from the dropdown
   - Look for MCP server connection errors or initialization messages

### Connection Errors

1. **Test Launch Script Manually**
   ```bash
   # Replace with your actual path
   /path/to/senzing-mcp-server/launch_senzing_mcp.sh
   # Should output MCP protocol JSON messages
   # Press Ctrl+C to exit
   ```

2. **Verify Environment Variables in MCP Config**
   ```bash
   # Check that your MCP config includes environment variables
   cat ~/.aws/amazonq/agents/default.json | grep -A 5 '"env"'

   # Verify the config has SENZING_ENGINE_CONFIGURATION_JSON and LD_LIBRARY_PATH
   ```

3. **Check Senzing SDK Access**
   ```bash
   # Test that the SDK can be imported with environment variables set
   LD_LIBRARY_PATH=/opt/senzing/er/lib PYTHONPATH=/opt/senzing/sdk/python \
     python3 -c "from senzing import SzEngine; print('Senzing SDK accessible')"
   ```

### Data Query Issues

1. **Verify Database Has Data**
   ```bash
   # Navigate to your MCP server directory
   cd /path/to/senzing-mcp-server

   # Run test search using example script with environment variables set
   LD_LIBRARY_PATH=/opt/senzing/er/lib \
   PYTHONPATH=/opt/senzing/sdk/python \
   SENZING_ENGINE_CONFIGURATION_JSON='{"PIPELINE":...}' \
     python examples/search_entity.py "Smith"
   ```

2. **Check Database Connection**
   ```bash
   # Verify database file exists (for SQLite)
   # Path should match what's in your MCP config's SENZING_ENGINE_CONFIGURATION_JSON
   ls -la /path/to/your/senzing/database/G2C.db
   ```

3. **Review Engine Configuration**
   ```bash
   # Extract and validate JSON from your MCP config
   cat ~/.aws/amazonq/agents/default.json | \
     grep SENZING_ENGINE_CONFIGURATION_JSON | \
     python3 -m json.tool
   ```

### Permission Issues

If you see permission errors:

```bash
# Make scripts executable
chmod +x /path/to/senzing-mcp-server/*.sh

# Check directory permissions
ls -la /path/to/senzing-mcp-server/
```

## Advanced Configuration

### Using with AWS Systems Manager

For AWS Systems Manager Session Manager:

```bash
# Start session to EC2 instance with Senzing
aws ssm start-session --target i-1234567890abcdef0

# Then configure MCP server as described above
```

### Docker Container Setup

If running Senzing in a Docker container:

```json
{
  "mcpServers": {
    "senzing": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "senzing-container",
        "/path/to/senzing-mcp-server/launch_senzing_mcp.sh"
      ]
    }
  }
}
```

Replace `senzing-container` with your container name and `/path/to` with the actual path inside the container.

## Performance Considerations

- **First Query Delay**: Initial SDK initialization may take 2-3 seconds
- **Large Result Sets**: Search queries returning >100 entities may be slower
- **Network Latency**: Remote SSH connections add ~50-200ms per query
- **Concurrent Queries**: MCP server handles one request at a time

## Security Notes

- This is a **read-only** MCP server - no data modification capabilities
- All queries use configured Senzing repository permissions
- No authentication is performed by the MCP server itself
- Use SSH key-based authentication for remote connections
- Consider network security groups for AWS cloud deployments

## Additional Resources

- [Amazon Q Developer Documentation](https://docs.aws.amazon.com/amazonq/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Senzing SDK Documentation](https://docs.senzing.com/)
- [AWS Cloud9 User Guide](https://docs.aws.amazon.com/cloud9/)

## Support

For issues related to:

- **MCP Configuration**: Check Amazon Q Developer extension logs
- **Senzing Queries**: Review Senzing engine logs and configuration
- **AWS Environment**: Verify IAM permissions and network connectivity
- **Server Setup**: Test launch script manually and check environment variables
