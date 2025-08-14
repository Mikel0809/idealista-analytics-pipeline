#!/usr/bin/env python3
"""
Idealista API Research Script
============================

Research script for Idealista API to design the real estate data pipeline.

Objective: Explore available data and structure extraction for Spain 
with core minimum fields defined.

Defined scope:
- Only residential properties (apartments, houses, penthouses, duplexes)
- Operations: sale + rent
- Geography: all Spain
- Core data: price, surface, location, type, operation, date, rooms, bathrooms
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IdealistaAPIResearcher:
    """
    Idealista API researcher to understand structure and capabilities.
    """
    
    def __init__(self):
        """Initialize the API researcher."""
        self.base_url = "https://api.idealista.com"
        self.oauth_url = "https://api.idealista.com/oauth/token"
        
        # Credentials (should be configured as environment variables)
        self.api_key = os.getenv('IDEALISTA_API_KEY')
        self.secret = os.getenv('IDEALISTA_SECRET')
        
        # Access token (obtained dynamically)
        self.access_token = None
        
        # Research configuration
        self.demo_mode = not (self.api_key and self.secret)
        
        if self.demo_mode:
            logger.warning("🔍 DEMO MODE: No credentials found. Using synthetic data.")
        else:
            logger.info("🔑 Credentials found. Real API mode.")
    
    def authenticate(self) -> bool:
        """
        Authenticate with Idealista API using OAuth2.
        
        Returns:
            bool: True if authentication was successful
        """
        if self.demo_mode:
            logger.info("🔍 DEMO: Simulating successful authentication")
            self.access_token = "demo_token_12345"
            return True
        
        try:
            # Datos para autenticación OAuth2
            auth_data = {
                'grant_type': 'client_credentials',
                'scope': 'read'
            }
            
            # Headers con credenciales básicas
            import base64
            credentials = f"{self.api_key}:{self.secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Realizar petición de autenticación
            response = requests.post(self.oauth_url, data=auth_data, headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                logger.info("✅ Autenticación exitosa")
                return True
            else:
                logger.error(f"❌ Error de autenticación: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error en autenticación: {str(e)}")
            return False
    
    def get_sample_properties_data(self, operation: str = "sale", location: str = "madrid") -> Dict:
        """
        Obtener datos de muestra de propiedades para investigar estructura.
        
        Args:
            operation: "sale" o "rent"
            location: ubicación para buscar
            
        Returns:
            Dict: Datos de respuesta de la API
        """
        if self.demo_mode:
            return self._generate_demo_data(operation, location)
        
        # URL del endpoint de búsqueda
        search_url = f"{self.base_url}/3.5/es/search"
        
        # Parámetros de búsqueda
        params = {
            'operation': operation,
            'propertyType': 'homes',  # Solo viviendas
            'locationId': self._get_location_id(location),
            'numPage': 1,
            'maxItems': 5,  # Solo 5 para investigación
            'order': 'publicationDate',
            'sort': 'desc'
        }
        
        # Headers con token de autorización
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(search_url, params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Error en búsqueda: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error en petición: {str(e)}")
            return {}
    
    def _get_location_id(self, location: str) -> str:
        """
        Obtener ID de ubicación para la API.
        
        Args:
            location: nombre de la ubicación
            
        Returns:
            str: ID de la ubicación
        """
        # Mapeo básico de ubicaciones principales
        location_map = {
            'madrid': '0-EU-ES-28-07-001-079',
            'barcelona': '0-EU-ES-08-08-001-019',
            'valencia': '0-EU-ES-46-46-001-087',
            'sevilla': '0-EU-ES-41-41-001-079'
        }
        
        return location_map.get(location.lower(), location_map['madrid'])
    
    def _generate_demo_data(self, operation: str, location: str) -> Dict:
        """
        Generar datos de demostración que simulan la estructura real de la API.
        
        Args:
            operation: tipo de operación
            location: ubicación
            
        Returns:
            Dict: Datos sintéticos con estructura real
        """
        logger.info(f"🔍 DEMO: Generando datos sintéticos para {operation} en {location}")
        
        demo_properties = []
        for i in range(3):
            property_data = {
                'propertyCode': f'DEMO_{i+1}_{operation.upper()}',
                'price': 250000 + (i * 50000) if operation == 'sale' else 1200 + (i * 300),
                'size': 80 + (i * 20),
                'rooms': 2 + (i % 3),
                'bathrooms': 1 + (i % 2),
                'propertyType': ['flat', 'house', 'penthouse'][i % 3],
                'operation': operation,
                'address': f'Calle Demo {i+1}, {location.title()}',
                'latitude': 40.4168 + (i * 0.01),
                'longitude': -3.7038 + (i * 0.01),
                'province': location.title(),
                'municipality': location.title(),
                'district': f'Distrito {i+1}',
                'publicationDate': f'2024-01-{15+i:02d}',
                'modificationDate': f'2024-01-{20+i:02d}',
                'floor': f'{i+1}º' if i < 2 else 'Bajo',
                'hasElevator': i % 2 == 0,
                'hasParkingSpace': i % 3 == 0,
                'description': f'Vivienda demo {i+1} en {location}. Excelente ubicación.',
                'images': [f'https://demo.idealista.com/image_{i+1}_{j}.jpg' for j in range(3)]
            }
            demo_properties.append(property_data)
        
        return {
            'total': 150 + (hash(location) % 100),
            'actualPage': 1,
            'itemsPerPage': 3,
            'totalPages': 50,
            'elementList': demo_properties,
            'summary': {
                'averagePrice': 275000 if operation == 'sale' else 1350,
                'averageSize': 90,
                'averagePricePerSquareMeter': 3056 if operation == 'sale' else 15
            }
        }
    
    def analyze_data_structure(self, data: Dict) -> Dict:
        """
        Analizar la estructura de datos devuelta por la API.
        
        Args:
            data: datos de respuesta de la API
            
        Returns:
            Dict: análisis de la estructura
        """
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_properties': data.get('total', 0),
            'sample_size': len(data.get('elementList', [])),
            'available_fields': [],
            'core_fields_mapping': {},
            'missing_fields': [],
            'data_quality': {}
        }
        
        if not data.get('elementList'):
            logger.warning("⚠️ No hay propiedades en la respuesta")
            return analysis
        
        # Analizar campos disponibles en la primera propiedad
        sample_property = data['elementList'][0]
        analysis['available_fields'] = list(sample_property.keys())
        
        # Mapear nuestros campos objetivo con los campos de la API
        field_mapping = {
            'precio': ['price', 'priceInfo', 'amount'],
            'superficie': ['size', 'surface', 'area'],
            'ubicacion_provincia': ['province', 'provinceName'],
            'ubicacion_municipio': ['municipality', 'municipalityName'],
            'ubicacion_coordenadas': ['latitude', 'longitude'],
            'tipo_vivienda': ['propertyType', 'typology'],
            'operacion': ['operation'],
            'fecha_publicacion': ['publicationDate', 'date'],
            'habitaciones': ['rooms', 'bedrooms'],
            'baños': ['bathrooms', 'baths']
        }
        
        # Verificar qué campos están disponibles
        for our_field, api_fields in field_mapping.items():
            found_field = None
            for api_field in api_fields:
                if api_field in sample_property:
                    found_field = api_field
                    break
            
            if found_field:
                analysis['core_fields_mapping'][our_field] = found_field
            else:
                analysis['missing_fields'].append(our_field)
        
        # Análisis de calidad de datos
        for property_item in data['elementList']:
            for our_field, api_field in analysis['core_fields_mapping'].items():
                value = property_item.get(api_field)
                
                if our_field not in analysis['data_quality']:
                    analysis['data_quality'][our_field] = {
                        'non_null_count': 0,
                        'null_count': 0,
                        'sample_values': []
                    }
                
                if value is not None and value != '':
                    analysis['data_quality'][our_field]['non_null_count'] += 1
                    if len(analysis['data_quality'][our_field]['sample_values']) < 3:
                        analysis['data_quality'][our_field]['sample_values'].append(value)
                else:
                    analysis['data_quality'][our_field]['null_count'] += 1
        
        return analysis
    
    def research_api_capabilities(self) -> Dict:
        """
        Investigar las capacidades completas de la API.
        
        Returns:
            Dict: resumen completo de capacidades
        """
        logger.info("🔍 Iniciando investigación completa de la API de Idealista")
        
        research_results = {
            'timestamp': datetime.now().isoformat(),
            'authentication_status': False,
            'operations_tested': {},
            'locations_tested': {},
            'overall_analysis': {}
        }
        
        # 1. Probar autenticación
        auth_success = self.authenticate()
        research_results['authentication_status'] = auth_success
        
        if not auth_success and not self.demo_mode:
            logger.error("❌ No se pudo autenticar. Terminando investigación.")
            return research_results
        
        # 2. Probar diferentes operaciones
        operations = ['sale', 'rent']
        locations = ['madrid', 'barcelona', 'valencia']
        
        for operation in operations:
            logger.info(f"🔍 Probando operación: {operation}")
            research_results['operations_tested'][operation] = {}
            
            for location in locations:
                logger.info(f"📍 Probando ubicación: {location}")
                
                # Obtener datos de muestra
                sample_data = self.get_sample_properties_data(operation, location)
                
                if sample_data:
                    # Analizar estructura
                    analysis = self.analyze_data_structure(sample_data)
                    research_results['operations_tested'][operation][location] = analysis
                    
                    logger.info(f"✅ {location} - {operation}: {analysis['sample_size']} propiedades analizadas")
                else:
                    logger.warning(f"⚠️ No se obtuvieron datos para {location} - {operation}")
        
        # 3. Análisis general
        research_results['overall_analysis'] = self._generate_overall_analysis(research_results)
        
        return research_results
    
    def _generate_overall_analysis(self, results: Dict) -> Dict:
        """
        Generar análisis general de todos los resultados.
        
        Args:
            results: resultados de la investigación
            
        Returns:
            Dict: análisis general
        """
        analysis = {
            'api_status': 'working' if results['authentication_status'] else 'authentication_failed',
            'operations_available': list(results['operations_tested'].keys()),
            'locations_tested': [],
            'core_fields_availability': {},
            'recommendations': []
        }
        
        # Recopilar ubicaciones probadas
        for operation_data in results['operations_tested'].values():
            analysis['locations_tested'].extend(operation_data.keys())
        analysis['locations_tested'] = list(set(analysis['locations_tested']))
        
        # Analizar disponibilidad de campos core
        all_mappings = {}
        for operation_data in results['operations_tested'].values():
            for location_data in operation_data.values():
                if 'core_fields_mapping' in location_data:
                    for field, mapping in location_data['core_fields_mapping'].items():
                        if field not in all_mappings:
                            all_mappings[field] = []
                        all_mappings[field].append(mapping)
        
        # Determinar campos más consistentes
        for field, mappings in all_mappings.items():
            most_common = max(set(mappings), key=mappings.count) if mappings else None
            consistency = mappings.count(most_common) / len(mappings) if mappings else 0
            
            analysis['core_fields_availability'][field] = {
                'api_field': most_common,
                'consistency': consistency,
                'available': consistency > 0.5
            }
        
        # Generar recomendaciones
        if analysis['api_status'] == 'working':
            analysis['recommendations'].append("✅ API funcional - proceder con desarrollo del extractor")
            
            available_fields = sum(1 for field_data in analysis['core_fields_availability'].values() 
                                 if field_data['available'])
            total_fields = len(analysis['core_fields_availability'])
            
            if available_fields >= total_fields * 0.8:
                analysis['recommendations'].append("✅ Mayoría de campos core disponibles")
            else:
                analysis['recommendations'].append("⚠️ Algunos campos core no disponibles - considerar alternativas")
        else:
            analysis['recommendations'].append("❌ Problemas de autenticación - verificar credenciales")
        
        return analysis
    
    def save_research_results(self, results: Dict, filename: str = None):
        """
        Guardar resultados de investigación en archivo JSON.
        
        Args:
            results: resultados a guardar
            filename: nombre del archivo (opcional)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"idealista_api_research_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Resultados guardados en: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Error guardando resultados: {str(e)}")
    
    def print_summary(self, results: Dict):
        """
        Imprimir resumen de resultados en consola.
        
        Args:
            results: resultados de la investigación
        """
        print("\n" + "="*80)
        print("🏠 RESUMEN DE INVESTIGACIÓN - API IDEALISTA")
        print("="*80)
        
        overall = results.get('overall_analysis', {})
        
        print(f"\n📊 ESTADO GENERAL:")
        print(f"   • API Status: {overall.get('api_status', 'unknown')}")
        print(f"   • Autenticación: {'✅' if results.get('authentication_status') else '❌'}")
        print(f"   • Operaciones probadas: {', '.join(overall.get('operations_available', []))}")
        print(f"   • Ubicaciones probadas: {', '.join(overall.get('locations_tested', []))}")
        
        print(f"\n🎯 CAMPOS CORE DISPONIBLES:")
        for field, data in overall.get('core_fields_availability', {}).items():
            status = "✅" if data.get('available') else "❌"
            api_field = data.get('api_field', 'N/A')
            consistency = data.get('consistency', 0) * 100
            print(f"   • {field}: {status} → {api_field} ({consistency:.0f}% consistencia)")
        
        print(f"\n💡 RECOMENDACIONES:")
        for rec in overall.get('recommendations', []):
            print(f"   • {rec}")
        
        print("\n" + "="*80)


def main():
    """Función principal para ejecutar la investigación."""
    print("🏠 Iniciando investigación de la API de Idealista")
    print("📋 Objetivo: Definir extracción de datos inmobiliarios para toda España")
    
    # Crear investigador
    researcher = IdealistaAPIResearcher()
    
    # Ejecutar investigación completa
    results = researcher.research_api_capabilities()
    
    # Mostrar resumen
    researcher.print_summary(results)
    
    # Guardar resultados
    researcher.save_research_results(results)
    
    print("\n🎯 Investigación completada. Revisa los resultados para el siguiente paso.")


if __name__ == "__main__":
    main()
