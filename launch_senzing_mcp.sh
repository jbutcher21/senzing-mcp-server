#!/bin/bash
# Launch script for Senzing MCP Server
# This script sets up the environment and starts the MCP server

#==============================================================================
# CONFIGURATION - Edit these for your deployment
#==============================================================================

# Path to your Senzing installation (where setupEnv is located)
SENZING_ROOT="/data/etl/senzing/er/v4beta"

#==============================================================================
# END CONFIGURATION
#==============================================================================

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Validate that SENZING_ROOT is set and exists
if [ -z "$SENZING_ROOT" ]; then
    echo "Error: SENZING_ROOT is not set" >&2
    exit 1
fi

if [ ! -f "$SENZING_ROOT/setupEnv" ]; then
    echo "Error: setupEnv not found at $SENZING_ROOT/setupEnv" >&2
    exit 1
fi

# Source the main Senzing environment setup
source "$SENZING_ROOT/setupEnv"

# Source the local senzing environment configuration (for INI to JSON conversion)
cd "$SCRIPT_DIR"
source ./senzing_env.sh

# Launch the MCP server from the virtual environment
exec ./venv/bin/senzing-mcp
