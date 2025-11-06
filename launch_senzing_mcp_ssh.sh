#!/bin/bash
# SSH-based launch script for Senzing MCP Server
#
# PURPOSE: This script runs on your MCP CLIENT (Mac/Windows) and connects to
#          a remote Senzing server via SSH to start the MCP server there.
#
# SETUP:   1. Copy this script to your client machine
#          2. Edit the configuration section below
#          3. Make it executable: chmod +x launch_senzing_mcp_ssh.sh
#          4. Update your AI's MCP config to point to this script

#==============================================================================
# CONFIGURATION - Edit these for your deployment
#==============================================================================

# Remote server where Senzing is installed
REMOTE_HOST="192.168.2.111"

# User account on the remote server
REMOTE_USER="jbutcher"

# SSH key for authentication (use full path)
SSH_KEY="$HOME/.ssh/id_rsa"

# Path to the launch script on the REMOTE server
# (This should match where you cloned the senzing-mcp-server repo)
REMOTE_SCRIPT="/data/etl/senzing/er/v4beta/senzingMCP/launch_senzing_mcp.sh"

#==============================================================================
# END CONFIGURATION
#==============================================================================

# SSH to the remote server and execute the launch script
# The -T flag disables pseudo-terminal allocation (required for stdio MCP)
# The -i flag specifies the SSH key
exec ssh -T -i "$SSH_KEY" "${REMOTE_USER}@${REMOTE_HOST}" "$REMOTE_SCRIPT"
