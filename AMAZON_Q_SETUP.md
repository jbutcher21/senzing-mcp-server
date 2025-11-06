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

First, install the Senzing MCP server on your AWS instance:

```bash
# Clone the repository
git clone https://github.com/yourusername/senzing-mcp-server.git
cd senzing-mcp-server

# Install in development mode
pip install -e .

# Configure for your deployment
# Edit launch_senzing_mcp.sh and set SENZING_ROOT to your Senzing installation path
nano launch_senzing_mcp.sh
# Set: SENZING_ROOT="/path/to/your/senzing"
```

### Verify Installation

```bash
# Test that senzing-mcp command is available
which senzing-mcp

# Verify Senzing environment
source /path/to/your/senzing/setupEnv
python -c "import senzing; print('Senzing SDK accessible')"
```

## Quick Start for AWS Code Server

If you're using **AWS Code Server** (browser-based VS Code), follow these steps:

1. **Install the MCP server** on your Code Server instance (see Installation section above)

2. **Create MCP configuration:**
   ```bash
   mkdir -p ~/.amazon-q/mcp
   nano ~/.amazon-q/mcp/config.json
   ```

   Add this content (adjust path to where you cloned the repo):
   ```json
   {
     "mcpServers": {
       "senzing": {
         "command": "/home/ec2-user/senzing-mcp-server/launch_senzing_mcp.sh",
         "args": [],
         "env": {}
       }
     }
   }
   ```

3. **Reload Amazon Q Developer:**
   - Press `Ctrl+Shift+P` (Command Palette)
   - Type: `Developer: Reload Window`
   - Press Enter
   - **Your browser tab stays open** - this just reloads the VS Code window

4. **Verify it works:**
   - Open Amazon Q chat
   - Ask: "What MCP tools are available?"
   - You should see Senzing tools listed

## Detailed Configuration Steps

### Option 1: AWS Cloud9 or Code Server (Local)

When the Senzing MCP server is installed on the **same instance** as your IDE.

#### 1. Configure MCP Settings

Create the Amazon Q Developer MCP configuration file:

```bash
# Create configuration directory
mkdir -p ~/.amazon-q/mcp

# Create MCP configuration
# Replace /path/to with your actual senzing-mcp-server installation path
cat > ~/.amazon-q/mcp/config.json << 'EOF'
{
  "mcpServers": {
    "senzing": {
      "command": "/path/to/senzing-mcp-server/launch_senzing_mcp.sh",
      "args": [],
      "env": {}
    }
  }
}
EOF
```

**Example** for installation in home directory:
```json
{
  "mcpServers": {
    "senzing": {
      "command": "/home/ec2-user/senzing-mcp-server/launch_senzing_mcp.sh",
      "args": [],
      "env": {}
    }
  }
}
```

**Note**: The `launch_senzing_mcp.sh` script automatically sets up the required environment variables by sourcing Senzing's setupEnv.

#### 2. Reload Amazon Q Developer

After creating the configuration file, reload Amazon Q Developer to load the new MCP server:

**Method 1: Reload Window (Recommended)**
1. Open Command Palette: `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type: `Developer: Reload Window`
3. Press Enter

**Method 2: Reload Extension**
1. Open Extensions panel: `Ctrl+Shift+X` (or `Cmd+Shift+X` on Mac)
2. Find "Amazon Q" in the list
3. Click the gear icon → "Reload"

**Method 3: Restart Extension Host**
1. Open Command Palette: `Ctrl+Shift+P`
2. Type: `Developer: Restart Extension Host`
3. Press Enter

**Note**: For browser-based Code Server, these commands work the same way and won't close your browser tab or disconnect your session.

### Option 2: AWS CodeCatalyst Setup

If using AWS CodeCatalyst:

1. **Create a Dev Environment Configuration**

Add to your `.codecatalyst/workflows/mcp-config.yaml`:

```yaml
mcpServers:
  senzing:
    command: /path/to/senzing-mcp-server/launch_senzing_mcp.sh
    env: {}
```

2. **Configure in IDE Settings**

Open Settings → Extensions → Amazon Q Developer → MCP Servers and add:
- **Name**: senzing
- **Command**: `/path/to/senzing-mcp-server/launch_senzing_mcp.sh` (use your actual path)

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

The Senzing MCP server provides 8 read-only tools:

1. **search_entities** - Search for entities by attributes
   - Parameters: name, address, phone, email, date of birth
   - Returns: List of matching entities with match scores

2. **get_entity** - Get full entity details by ID
   - Parameters: entity_id
   - Returns: Complete entity record with features, records, and relationships

3. **find_relationship_path** - Find connection between entities
   - Parameters: start_entity_id, end_entity_id, max_degrees
   - Returns: Shortest path and relationship details

4. **find_network** - Discover related entity networks
   - Parameters: entity_ids, max_degrees, build_out_degrees, max_entities
   - Returns: Network graph of related entities

5. **explain_relationship** - Explain why entities are related
   - Parameters: entity_id_1, entity_id_2
   - Returns: Detailed match analysis and feature comparison

6. **explain_entity_resolution** - Explain how entity was resolved
   - Parameters: entity_id
   - Returns: Resolution steps and record consolidation details

7. **get_stats** - Get Senzing engine statistics
   - Returns: Performance metrics and repository statistics

8. **get_config_info** - Get configuration information
   - Returns: Active config ID and version details

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

2. **Verify Environment Setup**
   ```bash
   # Check that launch_senzing_mcp.sh has correct SENZING_ROOT
   grep SENZING_ROOT /path/to/senzing-mcp-server/launch_senzing_mcp.sh

   # Test that setupEnv exists at that location
   ls -la /your/senzing/root/setupEnv
   ```

3. **Check Senzing SDK Access**
   ```bash
   # The SDK should be importable after setupEnv is sourced
   source /your/senzing/root/setupEnv
   python3 -c "from senzing import SzEngine; print('Senzing SDK accessible')"
   ```

### Data Query Issues

1. **Verify Database Has Data**
   ```bash
   # Navigate to your MCP server directory
   cd /path/to/senzing-mcp-server

   # Run test search using example script
   source /your/senzing/root/setupEnv
   source ./senzing_env.sh
   python examples/search_entity.py "Smith"
   ```

2. **Check Database Connection**
   ```bash
   # Verify database file exists (for SQLite)
   # Path depends on your SENZING_ENGINE_CONFIGURATION_JSON
   ls -la /path/to/your/senzing/database/G2C.db
   ```

3. **Review Engine Configuration**
   ```bash
   # After sourcing senzing_env.sh, check config is valid
   echo $SENZING_ENGINE_CONFIGURATION_JSON | python3 -m json.tool
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

### Custom Environment Variables

If you need to override environment variables (instead of using launch script):

```json
{
  "mcpServers": {
    "senzing": {
      "command": "senzing-mcp",
      "env": {
        "SENZING_ENGINE_CONFIGURATION_JSON": "{\"PIPELINE\":{\"CONFIGPATH\":\"/etc/opt/senzing\",\"RESOURCEPATH\":\"/opt/senzing/g2/resources\",\"SUPPORTPATH\":\"/opt/senzing/data\"},\"SQL\":{\"CONNECTION\":\"sqlite3://na:na@/var/opt/senzing/sqlite/G2C.db\"}}",
        "LD_LIBRARY_PATH": "/opt/senzing/lib",
        "SENZING_LOG_LEVEL": "1"
      }
    }
  }
}
```

**Note**: Adjust paths to match your Senzing installation. This approach bypasses the launch script.

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
