import requests
import pandas as pd
import json
import time
import os
from dotenv import load_dotenv
from google.cloud import bigquery

# Cargar variables de entorno desde .env
load_dotenv()

def get_idealista_data(location_id, location_name_for_api):
    """
    Fetches property data from the Idealista API for a given location ID and filters,
    handling pagination.
    """
    url = "https://idealista7.p.rapidapi.com/listhomes"
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "idealista7.p.rapidapi.com"
    }

    all_properties = []
    num_page = 1
    total_pages = 1  # Initialize with 1 to enter the loop

    print(f"\n--- Starting data retrieval for locationId: {location_id} (API Location Name: {location_name_for_api}) ---")

    while num_page <= total_pages:
        querystring = {
            "order": "relevance",
            "operation": "sale",
            "locationId": location_id,
            "locationName": 'Madrid',
            "numPage": str(num_page),
            "maxItems": "40",
            "location": "es",
            "locale": "es",
            "sinceDate":"M"
            #"maxPrice": str(max_price),
            #"minSize": str(min_size),
            #"garden": str(garden).lower(),
            #"swimmingPool": str(swimming_pool).lower(),
            #"terrace": str(terrace).lower() # Corrected from 'terrance'
        }

        print(f"Fetching page {num_page} for {location_id}...")
        try:
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status()  # Raise an exception for HTTP errors
            result = response.json()

            if num_page == 1:
                total_pages = result.get('totalPages', 1)
                print(f"Total pages for {location_id}: {total_pages}")

            # Extract properties from the current page
            properties = result.get('elementList', [])
            all_properties.extend(properties)

            print(f"Fetched {len(properties)} properties from page {num_page}")

            num_page += 1

            # Add a small delay to be respectful to the API
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {location_id} on page {num_page}: {e}")
            break

    print(f"Finished processing {location_id} ({location_name_for_api}). Time taken: {time.time() - start_time:.2f} seconds.")
    return all_properties

def load_to_bigquery(df, table_id):
    """
    Load DataFrame to BigQuery table
    """
    try:
        # Initialize BigQuery client
        client = bigquery.Client(project=os.getenv("BIGQUERY_PROJECT_ID"))
        
        # Configure the load job
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",  # Replace table contents
            autodetect=True,  # Auto-detect schema
            source_format=bigquery.SourceFormat.CSV
        )
        
        # Load data
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()  # Wait for the job to complete
        
        print(f"✅ Datos cargados exitosamente a {table_id}")
        print(f"📊 Total de filas cargadas: {len(df)}")
        
    except Exception as e:
        print(f"❌ Error al cargar datos en BigQuery: {e}")
        print("Asegúrate de que las variables BIGQUERY_PROJECT_ID y BIGQUERY_DATASET están configuradas en el archivo .env")

def save_to_csv(df, filename):
    """
    Save DataFrame to CSV file
    """
    try:
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        filepath = f"data/{filename}"
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"✅ Datos guardados en CSV: {filepath}")
        print(f"📊 Total de filas guardadas: {len(df)}")
        
    except Exception as e:
        print(f"❌ Error al guardar CSV: {e}")

def main():
    """
    Main function to extract data from Idealista API
    """
    global start_time
    start_time = time.time()
    
    print("🚀 Iniciando extracción de datos de Idealista...")
    print(f"⏰ Hora de inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configuration for Madrid South
    locations = [
        {
            'location_id': '0-EU-ES-28-04',
            'api_location_name': 'Zona sur, Madrid'
        }
    ]
    
    all_data = []
    
    # Extract data for each location
    for location in locations:
        loc_id = location['location_id']
        api_location_name_param = location['api_location_name']
        
        properties_for_location = get_idealista_data(loc_id, api_location_name_param)
        all_data.extend(properties_for_location)
    
    if all_data:
        # Convert to DataFrame
        df = pd.DataFrame(all_data)
        
        print(f"\n📊 Resumen de extracción:")
        print(f"   • Total propiedades extraídas: {len(df)}")
        print(f"   • Columnas disponibles: {len(df.columns)}")
        print(f"   • Tiempo total: {time.time() - start_time:.2f} segundos")
        
        # Save to CSV
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        csv_filename = f"idealista_properties_{timestamp}.csv"
        save_to_csv(df, csv_filename)
        
        # Load to BigQuery
        project_id = os.getenv("BIGQUERY_PROJECT_ID")
        dataset_id = os.getenv("BIGQUERY_DATASET", "raw_data")
        table_name = "idealista_properties"
        
        if project_id:
            table_id = f"{project_id}.{dataset_id}.{table_name}"
            load_to_bigquery(df, table_id)
        else:
            print("⚠️  BIGQUERY_PROJECT_ID no configurado. Saltando carga a BigQuery.")
        
        print(f"\n✅ Proceso completado exitosamente!")
        
    else:
        print("❌ No se pudieron extraer datos. Verifica la configuración de la API.")

if __name__ == "__main__":
    main()
