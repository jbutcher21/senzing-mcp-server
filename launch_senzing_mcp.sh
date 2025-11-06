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

# Path to this project's virtual environment
# (Edit if your venv is in a different location)
VENV_PATH="./venv/bin/senzing-mcp"

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

# Check if venv exists
if [ ! -f "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH" >&2
    echo "Please run: pip install -e ." >&2
    exit 1
fi

# Launch the MCP server from the virtual environment
exec "$VENV_PATH"
