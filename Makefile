# Madrid Real Estate Analytics Pipeline
# Makefile for common operations

.PHONY: setup run test clean airflow dbt extract

# Default target
help:
	@echo "Madrid Real Estate Analytics Pipeline"
	@echo "==================================="
	@echo ""
	@echo "Available commands:"
	@echo "  make setup      - Set up the environment (create venv, install dependencies)"
	@echo "  make run        - Run the complete pipeline"
	@echo "  make extract    - Run only the extraction step"
	@echo "  make dbt        - Run only the dbt transformations"
	@echo "  make test       - Run dbt tests"
	@echo "  make airflow    - Start Airflow webserver"
	@echo "  make clean      - Clean temporary files and logs"
	@echo ""
	@echo "For more information, see README.md"

# Setup environment
setup:
	@echo "Setting up environment..."
	@chmod +x setup.sh
	@./setup.sh

# Run the complete pipeline
run:
	@echo "Running complete pipeline..."
	@chmod +x scripts/run_pipeline.sh
	@./scripts/run_pipeline.sh

# Run only extraction
extract:
	@echo "Running extraction only..."
	@source .venv/bin/activate && \
		python scripts/api_client/idealista.py

# Run dbt models
dbt:
	@echo "Running dbt models..."
	@source .venv/bin/activate && \
		cd dbt && \
		dbt run

# Run dbt tests
test:
	@echo "Running dbt tests..."
	@source .venv/bin/activate && \
		cd dbt && \
		dbt test

# Start Airflow webserver
airflow:
	@echo "Starting Airflow webserver..."
	@source .venv/bin/activate && \
		export AIRFLOW_HOME=$(PWD)/airflow && \
		export no_proxy="*" && \
		export PYTHONFAULTHANDLER=true && \
		airflow standalone

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name ".DS_Store" -delete
	@find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} +
	@rm -f data/*.csv
	@rm -f dbt/logs/*.log
	@echo "✅ Cleaned temporary files"
