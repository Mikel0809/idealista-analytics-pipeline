"""
Airflow DAG for extracting data from Idealista API.
"""
import json
import os
from datetime import datetime, timedelta

import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from dotenv import load_dotenv
from google.cloud import bigquery

from scripts.api_client.api import IdealistaAPIClient
from scripts.utils.data_validation import (convert_properties_to_dataframe,
                                          validate_property_data)

# Load environment variables
load_dotenv()

# Default arguments for DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Get configuration from environment variables
CITIES = os.getenv('EXTRACTION_CITIES', 'madrid,barcelona').split(',')
PROPERTY_TYPES = os.getenv('EXTRACTION_PROPERTY_TYPES', 'sale,rent').split(',')
MAX_PAGES = int(os.getenv('EXTRACTION_MAX_PAGES', '10'))
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')
BIGQUERY_DATASET_RAW = os.getenv('BIGQUERY_DATASET_RAW', 'idealista_raw')
GCS_BUCKET = os.getenv('GCS_BUCKET', f'{GCP_PROJECT_ID}-idealista-data')
AIRFLOW_HOME = os.getenv('AIRFLOW_HOME', '/opt/airflow')
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
    'extract_idealista_data',
    default_args=default_args,
    description='Extract data from Idealista API and load to BigQuery',
    schedule_interval=schedule,
    start_date=datetime(2025, 8, 1),
    catchup=False,
    tags=['idealista', 'extraction'],
)

def extract_city_data(city, property_type, **kwargs):
    """
    Extract property data for a specific city and property type.
    
    Args:
        city: City to extract data for
        property_type: Type of property (sale, rent)
        **kwargs: Additional keyword arguments
        
    Returns:
        Path to the saved CSV file
    """
    execution_date = kwargs['execution_date']
    date_str = execution_date.strftime('%Y-%m-%d')
    
    # Initialize API client
    client = IdealistaAPIClient()
    
    # Map property_type to API operation and property type
    operation_map = {
        'sale': 'sale',
        'rent': 'rent'
    }
    
    property_type_map = {
        'sale': 'homes',
        'rent': 'homes'
    }
    
    operation = operation_map.get(property_type, 'sale')
    api_property_type = property_type_map.get(property_type, 'homes')
    
    # Extract data
    properties = client.search_properties(
        operation=operation,
        property_type=api_property_type,
        location=city,
        max_pages=MAX_PAGES
    )
    
    # Validate data
    valid_properties, invalid_properties = validate_property_data(properties)
    
    # Convert to DataFrame
    df = convert_properties_to_dataframe(valid_properties)
    
    # Add metadata columns
    df['extraction_date'] = execution_date.isoformat()
    df['city'] = city
    df['property_type'] = property_type
    
    # Save to CSV
    output_dir = f"{AIRFLOW_HOME}/data/{date_str}"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/{city}_{property_type}_{date_str}.csv"
    df.to_csv(output_file, index=False)
    
    # Save invalid data for analysis
    if invalid_properties:
        invalid_file = f"{output_dir}/{city}_{property_type}_{date_str}_invalid.json"
        with open(invalid_file, 'w') as f:
            json.dump(invalid_properties, f, indent=2, default=str)
    
    return output_file

# Create tasks for each city and property type combination
for city in CITIES:
    for property_type in PROPERTY_TYPES:
        task_id = f"extract_{city}_{property_type}"
        
        extract_task = PythonOperator(
            task_id=task_id,
            python_callable=extract_city_data,
            op_kwargs={'city': city, 'property_type': property_type},
            provide_context=True,
            dag=dag,
        )
        
        # Define GCS upload task
        gcs_upload_task = LocalFilesystemToGCSOperator(
            task_id=f"upload_to_gcs_{city}_{property_type}",
            src="{{ task_instance.xcom_pull(task_ids='" + task_id + "') }}",
            dst=f"raw/idealista/{{{{ ds }}}}/{city}_{property_type}.csv",
            bucket=GCS_BUCKET,
            dag=dag,
        )
        
        # Define BigQuery load task
        bq_load_task = GCSToBigQueryOperator(
            task_id=f"load_to_bq_{city}_{property_type}",
            bucket=GCS_BUCKET,
            source_objects=[f"raw/idealista/{{{{ ds }}}}/{city}_{property_type}.csv"],
            destination_project_dataset_table=f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET_RAW}.raw_idealista_{property_type}",
            schema_fields=[
                {'name': 'id', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'reference', 'type': 'STRING', 'mode': 'NULLABLE'},
                {'name': 'type', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'operation', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'status', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'url', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'title', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'description', 'type': 'STRING', 'mode': 'NULLABLE'},
                {'name': 'location_latitude', 'type': 'FLOAT', 'mode': 'REQUIRED'},
                {'name': 'location_longitude', 'type': 'FLOAT', 'mode': 'REQUIRED'},
                {'name': 'location_address', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'location_district', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'location_neighborhood', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'location_city', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'location_province', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'location_country', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'location_postal_code', 'type': 'STRING', 'mode': 'NULLABLE'},
                {'name': 'features_size', 'type': 'FLOAT', 'mode': 'REQUIRED'},
                {'name': 'features_rooms', 'type': 'INTEGER', 'mode': 'REQUIRED'},
                {'name': 'features_bathrooms', 'type': 'INTEGER', 'mode': 'REQUIRED'},
                {'name': 'features_has_elevator', 'type': 'BOOLEAN', 'mode': 'NULLABLE'},
                {'name': 'features_has_parking', 'type': 'BOOLEAN', 'mode': 'NULLABLE'},
                {'name': 'features_has_terrace', 'type': 'BOOLEAN', 'mode': 'NULLABLE'},
                {'name': 'features_has_garden', 'type': 'BOOLEAN', 'mode': 'NULLABLE'},
                {'name': 'features_has_pool', 'type': 'BOOLEAN', 'mode': 'NULLABLE'},
                {'name': 'features_floor', 'type': 'INTEGER', 'mode': 'NULLABLE'},
                {'name': 'features_is_exterior', 'type': 'BOOLEAN', 'mode': 'NULLABLE'},
                {'name': 'features_energy_certificate', 'type': 'STRING', 'mode': 'NULLABLE'},
                {'name': 'features_condition', 'type': 'STRING', 'mode': 'NULLABLE'},
                {'name': 'features_construction_year', 'type': 'INTEGER', 'mode': 'NULLABLE'},
                {'name': 'price_price', 'type': 'FLOAT', 'mode': 'REQUIRED'},
                {'name': 'price_price_per_sqm', 'type': 'FLOAT', 'mode': 'REQUIRED'},
                {'name': 'price_currency', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'price_original_price', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'price_change_date', 'type': 'TIMESTAMP', 'mode': 'NULLABLE'},
                {'name': 'price_change_percentage', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'images', 'type': 'STRING', 'mode': 'NULLABLE'},
                {'name': 'published_date', 'type': 'TIMESTAMP', 'mode': 'REQUIRED'},
                {'name': 'updated_date', 'type': 'TIMESTAMP', 'mode': 'REQUIRED'},
                {'name': 'contact_phone', 'type': 'STRING', 'mode': 'NULLABLE'},
                {'name': 'contact_name', 'type': 'STRING', 'mode': 'NULLABLE'},
                {'name': 'agency_id', 'type': 'STRING', 'mode': 'NULLABLE'},
                {'name': 'agency_name', 'type': 'STRING', 'mode': 'NULLABLE'},
                {'name': 'extraction_date', 'type': 'TIMESTAMP', 'mode': 'REQUIRED'},
                {'name': 'city', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'property_type', 'type': 'STRING', 'mode': 'REQUIRED'},
            ],
            write_disposition='WRITE_APPEND',
            skip_leading_rows=1,
            allow_quoted_newlines=True,
            dag=dag,
        )
        
        # Set task dependencies
        extract_task >> gcs_upload_task >> bq_load_task
