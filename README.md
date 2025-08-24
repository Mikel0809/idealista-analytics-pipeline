# Análisis Predictivo del Mercado Inmobiliario Español

Pipeline de datos end-to-end para analizar el mercado inmobiliario español, identificar zonas emergentes y generar insights accionables sobre tendencias y oportunidades de inversión.

## Visión General

Este proyecto implementa un pipeline analítico moderno que extrae datos de portales inmobiliarios, los procesa mediante una arquitectura de datos en capas, y genera KPIs avanzados para el análisis del mercado inmobiliario español.

### Objetivos Principales

- Identificar zonas emergentes antes de que los precios suban significativamente
- Analizar rentabilidad de inversiones inmobiliarias por zona
- Evaluar la saturación del mercado y presión compradora/vendedora
- Predecir tendencias de precios a medio plazo

## Arquitectura

El proyecto sigue una arquitectura moderna de ingeniería de datos:

- **Extracción**: Python + Airflow para obtener datos de APIs inmobiliarias
- **Almacenamiento**: Google BigQuery con estructura de esquemas en capas
- **Transformación**: dbt para modelado de datos y transformaciones SQL
- **Análisis**: Python para modelos predictivos y cálculo de KPIs

Para más detalles, consulta la [documentación de arquitectura](docs/architecture/architecture_document.md) y el [diagrama de componentes](docs/architecture/component_diagram.md).

## Estructura del Proyecto

```
idealista-analytics-pipeline/
├── airflow/               # DAGs y configuración de Airflow
├── dbt/                   # Proyecto dbt con modelos en capas
├── scripts/               # Scripts de utilidad y cliente API
├── docs/                  # Documentación del proyecto
├── notebooks/             # Notebooks para análisis exploratorio
└── [archivos de config]   # Configuración del proyecto
```

## Requisitos

- Python 3.9+
- Apache Airflow 2.7+
- Google Cloud Platform (BigQuery)
- dbt 1.5+
- Acceso a API de Idealista (u otra fuente de datos inmobiliarios)

## Configuración

1. Clonar el repositorio:
   ```
   git clone https://github.com/tu-usuario/idealista-analytics-pipeline.git
   cd idealista-analytics-pipeline
   ```

2. Crear y activar entorno virtual:
   ```
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Para desarrollo
   ```

4. Configurar variables de entorno:
   ```
   cp .env.example .env
   # Editar .env con tus credenciales
   ```

5. Configurar dbt:
   ```
   cp dbt/profiles.yml.example ~/.dbt/profiles.yml
   # Editar profiles.yml con tu configuración de BigQuery
   ```

## Uso

### Extracción de Datos

Los DAGs de Airflow gestionan la extracción de datos:

```
cd airflow
airflow standalone
```

Visita http://localhost:8080 para acceder a la UI de Airflow.

### Transformación con dbt

Para ejecutar las transformaciones dbt:

```
cd dbt
dbt run
```

Para ejecutar tests de datos:

```
dbt test
```

### Análisis

Los notebooks de análisis se encuentran en la carpeta `notebooks/`.

## KPIs Principales

- **Índice de Zonas Emergentes**: Identifica barrios con potencial de revalorización
- **Análisis de Rentabilidad**: ROI estimado y proyecciones a 5 años
- **Índice de Saturación**: Equilibrio oferta/demanda y presión de mercado

## Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add some amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Licencia

Este proyecto es para uso personal y educativo.

## Contacto

Tu Nombre - tu.email@example.com
