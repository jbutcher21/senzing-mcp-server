#!/bin/bash
# Convert Senzing INI config file to JSON environment variable

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

# Set library path for Senzing native libraries
export LD_LIBRARY_PATH="/data/etl/senzing/er/v4beta/lib:${LD_LIBRARY_PATH}"
echo "Set LD_LIBRARY_PATH to include Senzing libraries" >&2
