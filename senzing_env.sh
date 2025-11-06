#!/bin/bash
# OPTIONAL: Convert Senzing INI config file to JSON environment variable
#
# This script is NO LONGER REQUIRED if you set SENZING_ENGINE_CONFIGURATION_JSON
# in your .bashrc. It's kept as a utility for users who need to convert INI files.
#
# USAGE:
#   export SENZING_CONFIG_FILE=/path/to/config.ini
#   source ./senzing_env.sh

# Check if SENZING_CONFIG_FILE is set
if [ -z "$SENZING_CONFIG_FILE" ]; then
    echo "Error: SENZING_CONFIG_FILE environment variable is not set" >&2
    exit 1
fi

# Check if the config file exists
if [ ! -f "$SENZING_CONFIG_FILE" ]; then
    echo "Error: Config file not found: $SENZING_CONFIG_FILE" >&2
    exit 1
fi

# Convert INI to JSON using Python
export SENZING_ENGINE_CONFIGURATION_JSON=$(python3 << 'EOF'
import json
import sys
import os
from configparser import ConfigParser

config_file = os.environ.get('SENZING_CONFIG_FILE')
config = ConfigParser()
config.read(config_file)

# Convert to dictionary
result = {}
for section in config.sections():
    result[section] = {}
    for key, value in config.items(section):
        result[section][key.upper()] = value.strip()

# Output as compact JSON
print(json.dumps(result, separators=(',', ':')))
EOF
)

# Check if conversion was successful
if [ $? -eq 0 ]; then
    echo "Successfully set SENZING_ENGINE_CONFIGURATION_JSON" >&2
    echo "Value: $SENZING_ENGINE_CONFIGURATION_JSON" >&2
else
    echo "Error: Failed to convert INI to JSON" >&2
    exit 1
fi
