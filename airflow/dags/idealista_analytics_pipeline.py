"""
Idealista Analytics Pipeline DAG - Simple Version

This DAG orchestrates the complete real estate analytics pipeline:
1. Extract data from Idealista API (Python script)
2. Run dbt models in sequence: base → staging → intermediate → mart

Schedule: Daily at 6:00 AM
"""

import os
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator

# En Airflow 3.1.0, days_ago ha sido reemplazado
def days_ago(n):
    return datetime.now() - timedelta(days=n)

def run_idealista_extraction():
    """Function to run the Idealista extraction script using relative paths"""
    import subprocess
    import sys
    import os
    
    # Use PROJECT_ROOT from environment variable or DAG variables
    project_root = PROJECT_ROOT
    
    # Build paths using os.path.join for cross-platform compatibility
    script_path = os.path.join(project_root, "scripts", "api_client", "idealista.py")
    python_path = os.path.join(VENV_PATH, "python")
    
    print(f"Running extraction script: {script_path}")
    print(f"Using Python interpreter: {python_path}")
    
    result = subprocess.run(
        [python_path, script_path],
        capture_output=True,
        text=True,
        cwd=project_root  # Run from project root
    )
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    # Check if successful
    if result.returncode != 0:
        raise Exception(f"Script failed with return code {result.returncode}")
    
    return "Extraction completed successfully"

def run_dbt_command(command, selector=None):
    """Function to run dbt commands via Python subprocess to avoid architecture issues"""
    import subprocess
    import os
    
    # Build the dbt command
    cmd = [DBT_PATH, command]
    if selector:
        cmd.extend(['-s', selector])
    
    print(f"Running dbt command: {' '.join(cmd)}")
    print(f"Working directory: {DBT_DIR}")
    
    # Run the command
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=DBT_DIR  # Run from dbt directory
    )
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    # Check if successful
    if result.returncode != 0:
        raise Exception(f"dbt {command} failed with return code {result.returncode}")
    
    return f"dbt {command} completed successfully"

# Configuration variables - use environment variables or defaults
# Get project root dynamically (3 levels up from this DAG file)
PROJECT_ROOT = os.getenv('IDEALISTA_PROJECT_ROOT', 
                         os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
VENV_PATH = os.path.join(PROJECT_ROOT, '.venv', 'bin')
PYTHON_PATH = os.path.join(VENV_PATH, 'python')
DBT_PATH = os.path.join(VENV_PATH, 'dbt')
DBT_DIR = os.path.join(PROJECT_ROOT, 'dbt')

# Default arguments
default_args = {
    'owner': 'analytics-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
}

# DAG definition
dag = DAG(
    'idealista_analytics_pipeline',
    default_args=default_args,
    description='Simple Idealista real estate analytics pipeline',
    schedule='0 6 * * *',  # Daily at 6:00 AM
    max_active_runs=1,
    tags=['idealista', 'real-estate', 'analytics', 'dbt'],
)

# Task 1: Extract data from Idealista API (using PythonOperator to avoid numpy issues)
extract_data = PythonOperator(
    task_id='extract_idealista_data',
    python_callable=run_idealista_extraction,
    dag=dag,
)

# Task 2: Run dbt base models (using PythonOperator to avoid architecture issues)
run_dbt_base = PythonOperator(
    task_id='run_dbt_base',
    python_callable=run_dbt_command,
    op_kwargs={'command': 'run', 'selector': 'base_raw_data_idealista__properties'},
    dag=dag,
)

# Task 3: Run dbt staging models (using PythonOperator to avoid architecture issues)
run_dbt_staging = PythonOperator(
    task_id='run_dbt_staging',
    python_callable=run_dbt_command,
    op_kwargs={'command': 'run', 'selector': 'stg_idealista__properties'},
    dag=dag,
)

# Task 4: Run dbt intermediate models (using PythonOperator to avoid architecture issues)
run_dbt_intermediate = PythonOperator(
    task_id='run_dbt_intermediate',
    python_callable=run_dbt_command,
    op_kwargs={'command': 'run', 'selector': 'int_idealista__properties_enriched'},
    dag=dag,
)

# Task 5: Run dbt mart models (using PythonOperator to avoid architecture issues)
run_dbt_mart = PythonOperator(
    task_id='run_dbt_mart',
    python_callable=run_dbt_command,
    op_kwargs={'command': 'run', 'selector': 'mart_idealista__properties'},
    dag=dag,
)

# Task 6: Run dbt tests (using PythonOperator to avoid architecture issues)
run_dbt_tests = PythonOperator(
    task_id='run_dbt_tests',
    python_callable=run_dbt_command,
    op_kwargs={'command': 'test'},
    dag=dag,
)

# Define task dependencies - simple linear flow
extract_data >> run_dbt_base >> run_dbt_staging >> run_dbt_intermediate >> run_dbt_mart >> run_dbt_tests
