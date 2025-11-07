#!/bin/bash
# Launch script for Senzing MCP Server
# This script sets up the environment and starts the MCP server
#
# USAGE:
# - LOCAL: Point your AI assistant's MCP config directly to this script
# - REMOTE: Called by launch_senzing_mcp_ssh.sh via SSH
#
# PREREQUISITES:
# Your .bashrc must initialize Senzing with:
# - SENZING_ENGINE_CONFIGURATION_JSON environment variable (required)
# - LD_LIBRARY_PATH including Senzing libraries
# - PYTHONPATH including Senzing Python SDK

#==============================================================================
# CONFIGURATION - Edit these for your deployment
#==============================================================================

# Path to the Python module
# Run directly from source without requiring pip install
PYTHON_MODULE="src/senzing_mcp/server.py"

#==============================================================================
# END CONFIGURATION
#==============================================================================

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Source .bashrc to get Senzing environment variables
# This ensures the interactive shell initialization runs
source "$HOME/.bashrc"

# Validate that required Senzing environment variables are set
if [ -z "$SENZING_ENGINE_CONFIGURATION_JSON" ]; then
    echo "Error: SENZING_ENGINE_CONFIGURATION_JSON is not set" >&2
    echo "Please add Senzing initialization to your .bashrc file" >&2
    exit 1
fi

# Check if the Python module exists
if [ ! -f "$PYTHON_MODULE" ]; then
    echo "Error: Python module not found at $PYTHON_MODULE" >&2
    exit 1
fi

# Add src directory to Python path and launch the MCP server as module
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"
cd "$SCRIPT_DIR/src"
exec python3 -m senzing_mcp.server
