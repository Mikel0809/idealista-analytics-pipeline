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
        "x-rapidapi-key": "ba5c6b3093mshd662486fc824113p1b0ea4jsn0c22e26812e2",
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

            element_list = result.get('elementList', [])
            all_properties.extend(element_list)
            num_page += 1
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {location_id} on page {num_page}: {e}")
            break # Exit the loop if there's an error
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for {location_id} on page {num_page}: {e}")
            break # Exit the loop if there's an error

    return all_properties

def extract_property_details(property_list):
    """
    Extracts specified details from a list of property dictionaries into a list of flat dictionaries.
    """
    extracted_data = []
    for prop in property_list:
        details = {
            'propertyCode': prop.get('propertyCode'),
            'price': prop.get('price'),
            'propertyType': prop.get('propertyType'),
            'operation': prop.get('operation'),
            'size': prop.get('size'),
            'rooms': prop.get('rooms'),
            'bathrooms': prop.get('bathrooms'),
            'address': prop.get('address'),
            'province': prop.get('province'),
            'municipality': prop.get('municipality'),
            'locationId': prop.get('locationId'),
            'latitude': prop.get('latitude'),
            'longitude': prop.get('longitude'),
            'url': prop.get('url'),
            'description': prop.get('description'),
            'status': prop.get('status'),
            'phoneNumberForMobileDialing': prop.get('contactInfo', {}).get('phone1', {}).get('phoneNumberForMobileDialing'),
            'contactName': prop.get('contactInfo', {}).get('contactName'),
            'userType': prop.get('contactInfo', {}).get('userType'),
            'hasParkingSpace': prop.get('parkingSpace', {}).get('hasParkingSpace'),
            'priceByArea': prop.get('priceByArea'),
            'hasSwimmingPool': prop.get('features', {}).get('hasSwimmingPool'),
            'hasTerrace': prop.get('features', {}).get('hasTerrace'),
            'hasAirConditioning': prop.get('features', {}).get('hasAirConditioning'),
            'hasBoxRoom': prop.get('features', {}).get('hasBoxRoom'),
            'hasGarden': prop.get('features', {}).get('hasGarden')
        }
        extracted_data.append(details)
    return extracted_data

def export_to_csv(dataframe, filename="idealista_properties.csv"):
    """
    Exports a Pandas DataFrame to a CSV file.
    """
    dataframe.to_csv(filename, index=False, encoding='utf-8')
    print(f"\nData successfully exported to {filename}")


def load_to_bigquery(dataframe, table_name, dataset=None, project_id=None):
    """
    Carga un DataFrame de pandas a BigQuery.
    
    Args:
        dataframe (pd.DataFrame): Datos a cargar
        table_name (str): Nombre de la tabla
        dataset (str, optional): Nombre del dataset. Si es None, se usa el valor de BIGQUERY_DATASET del .env
        project_id (str, optional): ID del proyecto. Si es None, se usa el valor de BIGQUERY_PROJECT_ID del .env
    """
    # Obtener configuración desde variables de entorno
    project_id = project_id or os.getenv("BIGQUERY_PROJECT_ID")
    dataset = dataset or os.getenv("BIGQUERY_DATASET")
    location = os.getenv("BIGQUERY_LOCATION", "EU")
    
    if not project_id:
        raise ValueError("No se ha especificado BIGQUERY_PROJECT_ID en el archivo .env")
    if not dataset:
        raise ValueError("No se ha especificado BIGQUERY_DATASET en el archivo .env")
    
    # Configurar cliente
    client = bigquery.Client(project=project_id, location=location)
    
    # ID completo de la tabla
    full_table_id = f"{project_id}.{dataset}.{table_name}"
    
    # Configurar job de carga
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Sobrescribir tabla
        autodetect=True  # Detectar esquema automáticamente
    )
    
    # Cargar datos
    job = client.load_table_from_dataframe(
        dataframe, full_table_id, job_config=job_config
    )
    
    # Esperar a que termine
    job.result()
    
    print(f"✅ Datos cargados exitosamente a {full_table_id}")
    print(f"📊 Filas cargadas: {len(dataframe)}")
    
    return job


# --- Main Execution ---
if __name__ == "__main__":
    # 1. List of locationIds and corresponding locationNames
    location_data = [
    {"id": "0-EU-ES-28-04", "name": "Zona sur, Madrid"}
      ]

    # Filters (based on your querystring example)
    # MAX_PRICE = false
    # MIN_SIZE = 90
    # HAS_GARDEN = True
    # HAS_SWIMMING_POOL = True
    # HAS_TERRACE = True

    all_extracted_properties = []

    for loc in location_data:
        loc_id = loc["id"]
        # This is the name you want for your 'origin_location_name' column in the DataFrame
        location_origin_name = loc["name"]

        # The 'locationName' for the API querystring will remain "Madrid" as per your request.
        # If the API works better when this matches the specific location name, you could change it to loc["name"].
        api_location_name_param = loc["name"]

        start_time_loc_id = time.time()
        properties_for_location = get_idealista_data(loc_id, api_location_name_param)
        extracted_details = extract_property_details(properties_for_location)

        # ADD THE 'origin_location_name' COLUMN TO EACH DICTIONARY
        for prop_detail in extracted_details:
            prop_detail['origin_location_name'] = location_origin_name

        all_extracted_properties.extend(extracted_details)
        end_time_loc_id = time.time()
        time_taken = end_time_loc_id - start_time_loc_id
        print(f"Finished processing {loc_id} ({location_origin_name}). Time taken: {time_taken:.2f} seconds.")

    # Create a single DataFrame
    final_df = pd.DataFrame(all_extracted_properties)

    # Optional: Filter by userType = 'private'
    # final_df_private = final_df[final_df['userType'] == 'private'].copy() # .copy() to avoid SettingWithCopyWarning

    # print("\n--- Final DataFrame (Private UserType) Head ---")
    # print(final_df_private.head())
    # print(f"\nTotal number of properties collected (Private UserType): {len(final_df_private)}")


    # 8. Export to CSV to your local machine
    csv_filename = "idealista_filtered_properties_private.csv" # You can change the filename
    # final_df_private.to_csv(csv_filename, index=False, encoding='utf-8')
    # print(f"\nData successfully saved to {csv_filename}")
    
    # 9. Cargar a BigQuery
    try:
        # Cargar todos los datos (sin filtrar)
        load_to_bigquery(
            dataframe=final_df,
            table_name="idealista_properties"
        )
        
        # Cargar solo propiedades de particulares
        # load_to_bigquery(
        #    dataframe=final_df_private,
        #    table_name="idealista_properties_private"
        # )
        
        print("\n🚀 Proceso completo: Datos extraídos, guardados en CSV y cargados en BigQuery")
    except Exception as e:
        print(f"\n❌ Error al cargar datos en BigQuery: {e}")
        print("Asegúrate de que las variables BIGQUERY_PROJECT_ID y BIGQUERY_DATASET están configuradas en el archivo .env")