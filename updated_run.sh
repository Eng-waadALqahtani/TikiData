#!/bin/bash

echo "========================================"
echo "Sports Coach Assistant System"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed or not in PATH!"
    echo "Please install Python from https://www.python.org/downloads/"
    exit 1
fi

# Set the OpenAI API key
export OPENAI_API_KEY=""

# Install required packages
echo "Installing required packages..."
pip3 install flask openai requests || {
    echo "Failed to install required packages with pip3. Trying with pip..."
    pip install flask openai requests
}

# Check if data files exist
if [ ! -f match_data.json ]; then
    echo "Creating sample match_data.json file for football..."
    echo '{"matches": []}' > match_data.json
    echo "Please update the match_data.json file with your football match data."
fi

if [ ! -f NYK-JAN.json ]; then
    echo "Error: NYK-JAN.json file not found!"
    echo "Please ensure the NYK-JAN.json file is in the same directory as this script."
    exit 1
fi

# Create necessary directories
mkdir -p static
mkdir -p templates

# Copy frontend files to templates directory
echo "Setting up frontend files..."
cp football_frontend.html templates/football.html
cp basketball_frontend.html templates/basketball.html
cp landing_page.html templates/index.html
cp request-demo.html templates/request-demo.html

# Copy the updated unified app
cp updated_unified_app.py unified_app.py

# Run the application
echo "Starting Sports Coach Assistant System..."
python3 unified_app.py || python unified_app.py

read -p "Press Enter to exit..."
