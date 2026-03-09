#!/bin/bash
# Start MCP Toolbox Server
# This script starts the Toolbox server with our configuration

echo "Starting MCP Toolbox Server..."
echo "Configuration: toolbox_test/tools_fixed.yaml"
echo ""

# Check if tools file exists
if [ ! -f "toolbox_test/tools_fixed.yaml" ]; then
    echo "Error: tools_fixed.yaml not found"
    exit 1
fi

# Start server
echo "Starting server on http://127.0.0.1:5000"
echo "Press Ctrl+C to stop"
echo ""

npx @toolbox-sdk/server --tools-file toolbox_test/tools_fixed.yaml
