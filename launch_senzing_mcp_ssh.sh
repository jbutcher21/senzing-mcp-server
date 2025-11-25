#!/bin/bash
# SSH-based launch script for Senzing MCP Server
#
# PURPOSE: This script runs on your MCP CLIENT (Mac/Windows) and connects to
#          a remote Senzing server via SSH to start the MCP server there.
#
# PREREQUISITES:
#          - Remote server must have senzing-mcp-server cloned
#          - Environment variables must be set in MCP config on client
#
# SETUP:   1. Copy this script to your client machine
#          2. Edit the configuration section below
#          3. Make it executable: chmod +x launch_senzing_mcp_ssh.sh
#          4. Update your AI's MCP config to:
#             - Point command to this script
#             - Set environment variables in the "env" section

#==============================================================================
# CONFIGURATION - Edit these for your deployment
#==============================================================================

# Remote server where Senzing is installed
REMOTE_HOST="your-server-ip"

# User account on the remote server
REMOTE_USER="your-username"

# SSH key for authentication (use full path)
SSH_KEY="$HOME/.ssh/id_rsa"

# Path to the launch script on the REMOTE server
# (This should match where you cloned the senzing-mcp-server repo)
REMOTE_SCRIPT="/path/to/senzing-mcp-server/launch_senzing_mcp.sh"

#==============================================================================
# END CONFIGURATION
#==============================================================================

# Build environment variable exports for remote execution
# These will be passed from the MCP config's "env" section
ENV_EXPORTS=""
if [ -n "$SENZING_ENGINE_CONFIGURATION_JSON" ]; then
    ENV_EXPORTS="$ENV_EXPORTS export SENZING_ENGINE_CONFIGURATION_JSON='$SENZING_ENGINE_CONFIGURATION_JSON';"
fi
if [ -n "$LD_LIBRARY_PATH" ]; then
    ENV_EXPORTS="$ENV_EXPORTS export LD_LIBRARY_PATH='$LD_LIBRARY_PATH';"
fi
if [ -n "$PYTHONPATH" ]; then
    ENV_EXPORTS="$ENV_EXPORTS export PYTHONPATH='$PYTHONPATH';"
fi
if [ -n "$SENZING_LOG_LEVEL" ]; then
    ENV_EXPORTS="$ENV_EXPORTS export SENZING_LOG_LEVEL='$SENZING_LOG_LEVEL';"
fi

# SSH to the remote server, set environment variables, and execute the launch script
# The -T flag disables pseudo-terminal allocation (required for stdio MCP)
# The -i flag specifies the SSH key
exec ssh -T -i "$SSH_KEY" "${REMOTE_USER}@${REMOTE_HOST}" "$ENV_EXPORTS $REMOTE_SCRIPT"
