#!/bin/bash

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment and installing requirements..."
source venv/bin/activate
pip install -r requirements.txt

echo "Setup complete. Run the app with ./run.sh"