#!/bin/bash

# Define the path to the virtual environment
VENV_PATH="/home/cps/cps-sensors/cps-env"

# Define the path to the Python script
SCRIPT_PATH="/home/cps/cps-sensors/sensor-serial-new.py"

# Periodically run the script every minute
while true; do
    # Activate the virtual environment
    source "$VENV_PATH/bin/activate"
    
    # Run the Python script
    python "$SCRIPT_PATH"
    
    # Deactivate the virtual environment
    deactivate
    
    # Wait for 60 seconds
    sleep 600
done
