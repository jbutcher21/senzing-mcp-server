#!/bin/bash
# Launch script for Senzing MCP Server
# This script sets up the environment and starts the MCP server

# Source the main Senzing environment setup
source /data/etl/senzing/er/v4beta/setupEnv

# Source the local senzing environment configuration
cd /data/etl/senzing/er/v4beta/senzingMCP
source ./senzing_env.sh

# Launch the MCP server
exec ./venv/bin/senzing-mcp
