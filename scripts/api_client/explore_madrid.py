"""
Explorador Rápido de Datos - Comunidad de Madrid
Muestra información general sin descargar todos los datos
"""
import requests
import json

# Configuración para Comunidad de Madrid
url = "https://idealista7.p.rapidapi.com/listbuildings"

# Función para explorar una operación
def explorar_operacion(operacion):
    print(f"\n{'=' * 50}")
    print(f"🔍 EXPLORACIÓN RÁPIDA - COMUNIDAD DE MADRID - {operacion.upper()}")
    print("=" * 50)
    
    querystring = {
        "order": "relevance",
        "operation": operacion,
        "locationId": "0-EU-ES-28",  # Comunidad de Madrid
        "locationName": "Madrid",
        "numPage": "1",              # Solo primera página para info general
        "maxItems": "40",            # La API parece no aceptar valores menores
        "location": "es",
        "locale": "es"
    }

    headers = {
        "x-rapidapi-key": "c6c0c2ce9dmsh09426791611cbf9p140451jsn73d5830bb4bb",
        "x-rapidapi-host": "idealista7.p.rapidapi.com"
    }

    # Hacer llamada de prueba
    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()

        # Extraer información clave
        total_pages = data.get('totalPages', 'No disponible')
        total_properties = data.get('total', 'No disponible')
        total_elements = data.get('totalElements', 'No disponible')

        print("📊 INFORMACIÓN GENERAL:")
        print(f"   📍 Ubicación: Comunidad de Madrid")
        print(f"   🏠 Operación: {operacion.capitalize()}")
        print(f"   📄 Páginas totales: {total_pages}")
        if isinstance(total_properties, int):
            print(f"   📊 Propiedades totales: {total_properties:,}")
        else:
            print(f"   📊 Propiedades totales: {total_properties}")
        print(f"   📊 Elementos totales: {total_elements}")

        # Calcular datos por página
        if isinstance(total_properties, int) and isinstance(total_pages, int):
            properties_per_page = total_properties / total_pages
            estimated_size_mb = total_properties * 0.1  # assuming 0.1 MB per property
            print("\n📈 CÁLCULOS:")
            print(f"   • Propiedades por página: {properties_per_page:.1f}")
            print(f"   💾 Tamaño estimado total: ~{estimated_size_mb:.1f} MB")

        # Mostrar estructura de respuesta
        print("\n📋 ESTRUCTURA DE DATOS:")
        print(f"   • Campos respuesta: {', '.join(list(data.keys()))}")

        # Resumen ejecutivo
        print("\n📋 RESUMEN EJECUTIVO:")
        print(f"   🎯 Alcance: Comunidad Autónoma completa")
        print(f"   📊 Escala: {total_properties:,} propiedades")
        print(f"   📄 Complejidad: {total_pages} páginas necesarias")
        print(f"   ⏱️ Estrategia: Procesar por páginas para datos completos")

        # Recomendaciones
        print("\n💡 RECOMENDACIONES:")
        if isinstance(total_pages, int) and total_pages > 100:
            print("   ⚠️ Alto volumen - considerar procesamiento por lotes")
            print("   💡 Implementar delays entre llamadas para evitar límites API")
        else:
            print("   ✅ Volumen manejable - se puede procesar completo")

        if isinstance(total_properties, int) and total_properties > 1000:
            print("   📈 Big data - perfecto para BigQuery")
            print("   🎯 Ideal para análisis de mercado inmobiliario")
            
        return total_properties if isinstance(total_properties, int) else 0

    else:
        print(f"❌ Error en la llamada: {response.status_code}")
        print(f"📄 Mensaje: {response.text[:200]}")
        return 0

# Ejecutar exploración para venta y alquiler
total_venta = explorar_operacion("sale")
total_alquiler = explorar_operacion("rent")

# Mostrar resumen comparativo
print("\n" + "=" * 50)
print("📊 RESUMEN COMPARATIVO")
print("=" * 50)
print(f"🏠 Total propiedades en VENTA: {total_venta:,}")
print(f"🏠 Total propiedades en ALQUILER: {total_alquiler:,}")
print(f"🏠 TOTAL PROPIEDADES: {total_venta + total_alquiler:,}")
print("\n" + "=" * 50)
print("✅ Exploración completada - sin descargar datos pesados")