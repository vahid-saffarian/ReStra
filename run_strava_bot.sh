#!/bin/bash

# Change to the script directory
cd "$(dirname "$0")"

# Activate virtual environment if you're using one
# source /path/to/your/venv/bin/activate

# Run the Python script
python3 main.py

# Log the execution time
echo "Script executed at $(date)" >> strava_bot.log 