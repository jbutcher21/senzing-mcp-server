#!/bin/bash
# SSH-based launch script for Senzing MCP Server
# This script is meant to be copied to your Mac and used by ChatGPT Desktop
# It SSHs to the remote server and launches the MCP server there

# Configuration
REMOTE_HOST="192.168.2.111"
REMOTE_USER="jbutcher"
SSH_KEY="$HOME/.ssh/id_rsa"
REMOTE_SCRIPT="/data/etl/senzing/er/v4beta/senzingMCP/launch_senzing_mcp.sh"

# SSH to the remote server and execute the launch script
# The -T flag disables pseudo-terminal allocation (required for stdio MCP)
# The -i flag specifies the SSH key
exec ssh -T -i "$SSH_KEY" "${REMOTE_USER}@${REMOTE_HOST}" "$REMOTE_SCRIPT"
