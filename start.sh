#!/bin/bash

echo "🚀 Starting SokoLink Backend..."
echo "-------------------------------"

# Activate the virtual environment
source venv/bin/activate

# Start the Flask server
python wsgi.py
