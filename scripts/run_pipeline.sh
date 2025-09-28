#!/bin/bash

# Pipeline runner script for Idealista Analytics
# This avoids the SIGSEGV issues when running from Airflow web UI

set -e

echo "🏠 Starting Idealista Analytics Pipeline"
echo "📅 Date: $(date)"

# Set environment variables to avoid macOS issues
export no_proxy="*"
export PYTHONFAULTHANDLER=true

# Project configuration - automatically detect project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Set Airflow home
export AIRFLOW_HOME="$PROJECT_ROOT/airflow"

echo "📁 Working directory: $PROJECT_ROOT"
echo "🎯 Airflow home: $AIRFLOW_HOME"

# Run the complete pipeline
echo ""
echo "🚀 Executing complete pipeline..."
airflow dags test idealista_analytics_pipeline $(date +%Y-%m-%d)

echo ""
echo "✅ Pipeline execution completed!"
echo "📊 Check BigQuery for your data: ${BIGQUERY_PROJECT_ID}"
echo "🔍 Tables available:"
echo "  - raw_data.idealista_properties (raw data)"
echo "  - dbt_base.base_raw_data_idealista__properties (base model)"
echo "  - dbt_staging.stg_idealista__properties (staging model)"
echo "  - dbt_intermediate.int_idealista__properties_enriched (intermediate model)"
echo "  - dbt_mart.mart_idealista__properties (final mart)"
