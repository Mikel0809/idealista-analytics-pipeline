#!/bin/bash

# Madrid Real Estate Analytics Pipeline - Setup Script
# This script prepares the environment for running the pipeline

set -e  # Exit on any error

echo "🏠 Madrid Real Estate Analytics Pipeline - Setup"
echo "==============================================="

# Check Python version
if command -v python3.12 &>/dev/null; then
    PYTHON_CMD=python3.12
elif command -v python3.11 &>/dev/null; then
    PYTHON_CMD=python3.11
elif command -v python3.10 &>/dev/null; then
    PYTHON_CMD=python3.10
elif command -v python3.9 &>/dev/null; then
    PYTHON_CMD=python3.9
else
    echo "❌ Error: Python 3.9+ is required but not found"
    exit 1
fi

echo "✅ Using $PYTHON_CMD ($(${PYTHON_CMD} --version))"

# Create virtual environment
echo -n "Creating virtual environment... "
$PYTHON_CMD -m venv .venv
echo "done"

# Activate virtual environment
echo -n "Activating virtual environment... "
source .venv/bin/activate
echo "done"

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data
mkdir -p airflow/logs
mkdir -p dbt/logs
echo "✅ Directories created"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file (please edit with your credentials)"
else
    echo "⚠️ .env file already exists, skipping"
fi

# Create dbt profile
DBT_DIR=~/.dbt
if [ ! -d "$DBT_DIR" ]; then
    echo "Creating dbt profile directory..."
    mkdir -p "$DBT_DIR"
fi

if [ ! -f "$DBT_DIR/profiles.yml" ]; then
    echo "Creating dbt profiles.yml from template..."
    cp dbt/profiles.yml.example "$DBT_DIR/profiles.yml"
    echo "✅ Created dbt profile (please edit with your credentials)"
else
    echo "⚠️ dbt profile already exists, skipping"
fi

# Make scripts executable
echo "Making scripts executable..."
chmod +x scripts/run_pipeline.sh
chmod +x setup.sh
echo "✅ Scripts are now executable"

# Initialize Airflow
echo "Initializing Airflow..."
export AIRFLOW_HOME=$(pwd)/airflow
airflow db migrate
echo "✅ Airflow initialized"

echo ""
echo "🎉 Setup complete! Next steps:"
echo "1. Edit .env with your BigQuery and API credentials"
echo "2. Edit ~/.dbt/profiles.yml with your BigQuery credentials"
echo "3. Run the pipeline with: ./scripts/run_pipeline.sh"
echo ""
echo "For more information, see the README.md file."
