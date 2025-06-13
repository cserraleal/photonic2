#!/bin/bash

set -e
echo "Activating virtual environment..."
source venv/bin/activate
echo "Running Streamlit app..."
streamlit run app.py