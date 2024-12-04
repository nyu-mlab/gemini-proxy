#!/bin/bash

# Configuration
APP_NAME="server"  # Replace with your Flask app's filename (without .py)
WORKERS=1                 # Number of Gunicorn worker processes
BIND_ADDRESS="127.0.0.1:5000"  # Address and port to bind

# Ensure script is executed in the correct directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Start the Gunicorn server
echo "Starting Flask server with Gunicorn..."
gunicorn -w $WORKERS -b $BIND_ADDRESS "$APP_NAME:app"

# Exit with Gunicorn's exit code
exit $?