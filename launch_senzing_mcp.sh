#!/bin/bash
# Launch script for Senzing MCP Server
# This script sets up the Python path and starts the MCP server
#
# USAGE:
# - Point your AI assistant's MCP config to this script
# - Set environment variables in the MCP config's "env" section:
#   - SENZING_ENGINE_CONFIGURATION_JSON (required)
#   - LD_LIBRARY_PATH (required - path to Senzing libraries)
#   - PYTHONPATH (optional - for Senzing Python SDK if not system-wide)
#
# EXAMPLE MCP CONFIG:
# {
#   "mcpServers": {
#     "senzing": {
#       "command": "/path/to/launch_senzing_mcp.sh",
#       "env": {
#         "SENZING_ENGINE_CONFIGURATION_JSON": "{\"PIPELINE\":...}",
#         "LD_LIBRARY_PATH": "/opt/senzing/lib",
#         "PYTHONPATH": "/opt/senzing/sdk/python"
#       }
#     }
#   }
# }

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

# Check if the Python module exists
if [ ! -f "$PYTHON_MODULE" ]; then
    echo "Error: Python module not found at $PYTHON_MODULE" >&2
    exit 1
fi

# Add src directory to Python path and launch the MCP server as module
# Environment variables (SENZING_ENGINE_CONFIGURATION_JSON, LD_LIBRARY_PATH, etc.)
# should be set in the MCP config's "env" section and will be inherited here
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"
cd "$SCRIPT_DIR/src"
exec python3 -m senzing_mcp.server
