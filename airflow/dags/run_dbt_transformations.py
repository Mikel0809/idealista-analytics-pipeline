"""
Airflow DAG for running dbt transformations.
"""
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default arguments for DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Get configuration from environment variables
DBT_PROJECT_DIR = os.getenv('DBT_PROJECT_DIR', '/opt/airflow/dbt')
EXTRACTION_FREQUENCY = os.getenv('EXTRACTION_FREQUENCY', 'daily')

# Define schedule based on frequency
if EXTRACTION_FREQUENCY == 'daily':
    schedule = '@daily'
elif EXTRACTION_FREQUENCY == 'weekly':
    schedule = '@weekly'
else:
    schedule = '@daily'  # Default to daily

# Define the DAG
dag = DAG(
    'run_dbt_transformations',
    default_args=default_args,
    description='Run dbt transformations on Idealista data',
    schedule_interval=schedule,
    start_date=datetime(2025, 8, 1),
    catchup=False,
    tags=['idealista', 'dbt', 'transformation'],
)

# Define tasks for each dbt model layer
dbt_run_base = BashOperator(
    task_id='dbt_run_base',
    bash_command=f'cd {DBT_PROJECT_DIR} && dbt run --models base',
    dag=dag,
)

dbt_test_base = BashOperator(
    task_id='dbt_test_base',
    bash_command=f'cd {DBT_PROJECT_DIR} && dbt test --models base',
    dag=dag,
)

dbt_run_staging = BashOperator(
    task_id='dbt_run_staging',
    bash_command=f'cd {DBT_PROJECT_DIR} && dbt run --models staging',
    dag=dag,
)

dbt_test_staging = BashOperator(
    task_id='dbt_test_staging',
    bash_command=f'cd {DBT_PROJECT_DIR} && dbt test --models staging',
    dag=dag,
)

dbt_run_intermediate = BashOperator(
    task_id='dbt_run_intermediate',
    bash_command=f'cd {DBT_PROJECT_DIR} && dbt run --models intermediate',
    dag=dag,
)

dbt_test_intermediate = BashOperator(
    task_id='dbt_test_intermediate',
    bash_command=f'cd {DBT_PROJECT_DIR} && dbt test --models intermediate',
    dag=dag,
)

dbt_run_mart = BashOperator(
    task_id='dbt_run_mart',
    bash_command=f'cd {DBT_PROJECT_DIR} && dbt run --models mart',
    dag=dag,
)

dbt_test_mart = BashOperator(
    task_id='dbt_test_mart',
    bash_command=f'cd {DBT_PROJECT_DIR} && dbt test --models mart',
    dag=dag,
)

dbt_generate_docs = BashOperator(
    task_id='dbt_generate_docs',
    bash_command=f'cd {DBT_PROJECT_DIR} && dbt docs generate',
    dag=dag,
)

# Set task dependencies
dbt_run_base >> dbt_test_base >> dbt_run_staging >> dbt_test_staging >> \
dbt_run_intermediate >> dbt_test_intermediate >> dbt_run_mart >> dbt_test_mart >> \
dbt_generate_docs
