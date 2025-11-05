# Setting Up Senzing MCP Server with Amazon Q Developer

## Prerequisites

- Amazon Q Developer with MCP support
- AWS Cloud9 or other AWS cloud-based IDE
- Senzing MCP server installed and accessible from your environment
- AWS credentials configured

## Overview

Amazon Q Developer supports MCP (Model Context Protocol) servers, allowing you to extend Q's capabilities with custom tools. This guide covers setup in AWS cloud-based IDEs.

## Installation Steps

### Option 1: AWS Cloud9 Setup

#### 1. Prepare Your Environment

Ensure the Senzing MCP server is installed and the environment is configured:

```bash
# Navigate to the MCP server directory
cd /data/etl/senzing/er/v4beta/senzingMCP

# Verify installation
./venv/bin/senzing-mcp --version

# Test the environment setup
source /data/etl/senzing/er/v4beta/setupEnv
source ./senzing_env.sh
```

#### 2. Configure MCP Settings

Create or edit the Amazon Q Developer MCP configuration file:

```bash
# Create configuration directory
mkdir -p ~/.amazon-q/mcp

# Create MCP configuration
cat > ~/.amazon-q/mcp/config.json << 'EOF'
{
  "mcpServers": {
    "senzing": {
      "command": "/data/etl/senzing/er/v4beta/senzingMCP/launch_senzing_mcp.sh",
      "args": [],
      "env": {}
    }
  }
}
EOF
```

**Note**: The `launch_senzing_mcp.sh` script automatically sets up the required environment variables.

#### 3. Restart Amazon Q Developer

Restart your IDE or reload the Amazon Q Developer extension to load the new MCP server configuration.

### Option 2: AWS CodeCatalyst Setup

If using AWS CodeCatalyst:

1. **Create a Dev Environment Configuration**

Add to your `.codecatalyst/workflows/mcp-config.yaml`:

```yaml
mcpServers:
  senzing:
    command: /data/etl/senzing/er/v4beta/senzingMCP/launch_senzing_mcp.sh
    env: {}
```

2. **Configure in IDE Settings**

Open Settings → Extensions → Amazon Q Developer → MCP Servers and add:
- **Name**: senzing
- **Command**: `/data/etl/senzing/er/v4beta/senzingMCP/launch_senzing_mcp.sh`

### Option 3: Remote SSH Configuration

If connecting from a local IDE to a remote Senzing server via SSH:

1. **Create SSH Launch Wrapper**

Use the provided SSH launch script:

```bash
# This script is already in the repository
chmod +x launch_senzing_mcp_ssh.sh

# Edit to update your server details
nano launch_senzing_mcp_ssh.sh
```

Update these variables:
```bash
REMOTE_HOST="your-senzing-server.example.com"
REMOTE_USER="your-username"
SSH_KEY="$HOME/.ssh/id_rsa"
```

2. **Configure Amazon Q**

```json
{
  "mcpServers": {
    "senzing": {
      "command": "/path/to/launch_senzing_mcp_ssh.sh",
      "args": []
    }
  }
}
```

## Verification

After setup, verify the MCP server is connected:

1. Open Amazon Q Developer in your IDE
2. Ask: **"What MCP tools are available?"**
3. You should see 8 Senzing tools listed
4. Try a test query: **"Search for entities named Robert Smith"**

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
   # Verify config exists
   cat ~/.amazon-q/mcp/config.json
   ```

2. **Verify Launch Script is Executable**
   ```bash
   ls -la /data/etl/senzing/er/v4beta/senzingMCP/launch_senzing_mcp.sh
   chmod +x /data/etl/senzing/er/v4beta/senzingMCP/launch_senzing_mcp.sh
   ```

3. **Check Amazon Q Developer Logs**
   - Open IDE Output panel
   - Select "Amazon Q Developer" from the dropdown
   - Look for MCP server connection errors

### Connection Errors

1. **Test Launch Script Manually**
   ```bash
   /data/etl/senzing/er/v4beta/senzingMCP/launch_senzing_mcp.sh
   # Should output MCP protocol messages
   # Press Ctrl+C to exit
   ```

2. **Verify Environment Setup**
   ```bash
   source /data/etl/senzing/er/v4beta/setupEnv
   source /data/etl/senzing/er/v4beta/senzingMCP/senzing_env.sh
   echo $SENZING_ENGINE_CONFIGURATION_JSON
   # Should output JSON configuration
   ```

3. **Check Senzing SDK Access**
   ```bash
   python3 << 'EOF'
   import sys
   sys.path.insert(0, '/data/etl/senzing/er/v4beta/sdk/python')
   from senzing import SzEngine
   print("Senzing SDK accessible")
   EOF
   ```

### Data Query Issues

1. **Verify Database Has Data**
   ```bash
   # Navigate to server directory
   cd /data/etl/senzing/er/v4beta/senzingMCP

   # Run test search
   source /data/etl/senzing/er/v4beta/setupEnv
   source ./senzing_env.sh
   ./venv/bin/python search_entity.py "Smith"
   ```

2. **Check Database Connection**
   ```bash
   # Verify database file exists (for SQLite)
   ls -la /data/etl/senzing/er/v4beta/var/sqlite/G2C.db
   ```

3. **Review Engine Configuration**
   ```bash
   echo $SENZING_ENGINE_CONFIGURATION_JSON | python3 -m json.tool
   ```

### Permission Issues

If you see permission errors:

```bash
# Make scripts executable
chmod +x /data/etl/senzing/er/v4beta/senzingMCP/*.sh

# Check directory permissions
ls -la /data/etl/senzing/er/v4beta/senzingMCP/
```

## Advanced Configuration

### Custom Environment Variables

If you need custom Senzing configuration:

```json
{
  "mcpServers": {
    "senzing": {
      "command": "/data/etl/senzing/er/v4beta/senzingMCP/venv/bin/senzing-mcp",
      "env": {
        "SENZING_ENGINE_CONFIGURATION_JSON": "{\"PIPELINE\":{...},\"SQL\":{...}}",
        "LD_LIBRARY_PATH": "/data/etl/senzing/er/v4beta/lib",
        "SENZING_LOG_LEVEL": "1"
      }
    }
  }
}
```

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
        "/data/etl/senzing/er/v4beta/senzingMCP/launch_senzing_mcp.sh"
      ]
    }
  }
}
```

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
