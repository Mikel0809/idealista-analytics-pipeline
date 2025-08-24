# Arquitectura: Análisis Predictivo del Mercado Inmobiliario Español

## Resumen Ejecutivo

Este documento define la arquitectura técnica para el pipeline de análisis inmobiliario, diseñado para extraer, procesar y analizar datos del mercado inmobiliario español. La arquitectura sigue principios modernos de ingeniería de datos, con énfasis en escalabilidad, mantenibilidad y calidad de datos.

## Diagrama de Arquitectura

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │     │                 │
│  Fuentes de     │     │   Extracción    │     │  Procesamiento  │     │    Análisis     │
│    Datos        │────▶│   (Airflow)     │────▶│     (dbt)       │────▶│  & Consumo      │
│                 │     │                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
       │                        │                      │                        │
       ▼                        ▼                      ▼                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  API Idealista  │     │  Python Scripts │     │  Modelos dbt    │     │  Visualización  │
│  Otros portales │     │  BigQuery Load  │     │  Transformación │     │  Exportación    │
│  Datos externos │     │  Validación     │     │  Testing        │     │  API (futuro)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Componentes Principales

### 1. Extracción de Datos

**Tecnologías**: Python, Apache Airflow, Google Cloud Storage (opcional)

**Componentes**:
- Cliente API de Idealista (u otras fuentes)
- DAGs de Airflow para orquestación
- Validación inicial de datos
- Carga en BigQuery (esquema base)

**Consideraciones**:
- Manejo de límites de API y paginación
- Estrategia de reintentos y manejo de errores
- Registro de metadatos de extracción
- Detección de cambios incrementales

### 2. Almacenamiento de Datos

**Tecnologías**: Google BigQuery

**Estructura de Esquemas**:
- **base**: Datos crudos tipados y renombrados
- **staging**: Limpieza y transformaciones básicas
- **intermediate**: Modelos de negocio y transformaciones complejas
- **mart**: Modelos finales organizados por dominio de negocio

**Consideraciones**:
- Particionamiento por fecha para optimizar costos y rendimiento
- Clustering por ubicación geográfica
- Políticas de retención de datos
- Controles de acceso y seguridad

### 3. Transformación de Datos

**Tecnologías**: dbt (data build tool)

**Estructura de Modelos**:
- **base**: Modelos 1:1 con tablas fuente, con tipado y renombrado
  - Ejemplo: `base_idealista_listings.sql`
- **staging**: Limpieza, filtrado y transformaciones básicas
  - Ejemplo: `stg_idealista_listings.sql`
- **intermediate**: Agregaciones y transformaciones de negocio
  - Ejemplo: `int_property_metrics.sql`, `int_location_metrics.sql`
- **mart**: Modelos finales organizados por dominio
  - `mart_investment/mart_investment_opportunities.sql`
  - `mart_market_trends/mart_emerging_areas.sql`
  - `mart_reporting/mart_market_overview.sql`

**Consideraciones**:
- Tests de datos en cada capa
- Documentación de modelos
- Macros para lógica reutilizable
- Materialización apropiada (tabla, vista, incremental)

### 4. Análisis y Consumo

**Tecnologías**: Python (pandas, scikit-learn), BigQuery ML (opcional), Looker/Data Studio (opcional)

**Componentes**:
- Modelos predictivos para tendencias de precios
- Algoritmos de detección de zonas emergentes
- Cálculo de KPIs y métricas
- Visualizaciones y dashboards (fase posterior)

**Consideraciones**:
- Frecuencia de actualización de modelos analíticos
- Validación de resultados con datos históricos
- Exportación de insights para consumo

## Estructura del Repositorio

```
idealista-analytics-pipeline/
├── airflow/
│   ├── dags/
│   │   ├── extract_idealista_data.py
│   │   └── run_dbt_transformations.py
│   └── plugins/
│       └── operators/
│           └── idealista_api_operator.py
├── dbt/
│   ├── models/
│   │   ├── base/
│   │   │   └── base_idealista_listings.sql
│   │   ├── staging/
│   │   │   └── stg_idealista_listings.sql
│   │   ├── intermediate/
│   │   │   ├── int_property_metrics.sql
│   │   │   └── int_location_metrics.sql
│   │   └── mart/
│   │       ├── investment/
│   │       │   └── mart_investment_opportunities.sql
│   │       ├── market_trends/
│   │       │   └── mart_emerging_areas.sql
│   │       └── reporting/
│   │           └── mart_market_overview.sql
│   ├── tests/
│   │   └── assert_positive_prices.sql
│   ├── macros/
│   │   └── generate_schema_name.sql
│   ├── dbt_project.yml
│   └── profiles.yml.example
├── scripts/
│   ├── api_client/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   └── models.py
│   └── utils/
│       ├── __init__.py
│       └── data_validation.py
├── docs/
│   ├── architecture/
│   │   ├── architecture_document.md
│   │   └── component_diagram.md
│   └── project-brief.md
├── notebooks/
│   └── exploratory_analysis.ipynb
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Flujo de Datos Detallado

1. **Extracción**:
   - DAG de Airflow se ejecuta diariamente
   - Extrae datos de API de Idealista para ciudades objetivo
   - Valida estructura básica y completitud
   - Carga en BigQuery en esquema `base`

2. **Transformación Base a Staging**:
   - Modelos dbt convierten datos crudos a formato estandarizado
   - Aplica limpieza, tipado y normalización
   - Detecta y maneja valores atípicos
   - Genera tablas en esquema `staging`

3. **Transformación Staging a Intermediate**:
   - Modelos dbt aplican lógica de negocio
   - Calcula métricas por propiedad y ubicación
   - Genera agregaciones temporales (semanal, mensual)
   - Crea tablas en esquema `intermediate`

4. **Transformación Intermediate a Mart**:
   - Modelos dbt crean vistas específicas por dominio
   - Implementa cálculos de KPIs avanzados
   - Genera modelos para análisis de inversión, tendencias y reporting
   - Materializa en esquema `mart`

5. **Análisis y Consumo**:
   - Scripts Python/notebooks consumen modelos finales
   - Aplica algoritmos predictivos y detección de patrones
   - Genera insights y recomendaciones
   - Exporta resultados para visualización (fase posterior)

## Modelo de Datos Conceptual

### Entidades Principales

1. **Propiedades**:
   - Identificador único
   - Características físicas (tamaño, habitaciones, etc.)
   - Ubicación (coordenadas, dirección)
   - Precios (actual, histórico)
   - Estado (disponible, vendido, etc.)

2. **Ubicaciones**:
   - Jerarquía (ciudad, distrito, barrio)
   - Datos demográficos
   - Servicios y amenidades
   - Indicadores económicos

3. **Transacciones** (si disponible):
   - Tipo (venta, alquiler)
   - Fechas (publicación, venta/alquiler)
   - Precios inicial y final
   - Duración en mercado

### Modelos Analíticos

1. **Índice de Zonas Emergentes**:
   - Tendencias de precios por zona
   - Velocidad de transacciones
   - Factores contextuales

2. **Análisis de Rentabilidad**:
   - ROI estimado por zona y tipo de propiedad
   - Proyecciones a 5 años
   - Comparativas entre zonas

3. **Índice de Saturación de Mercado**:
   - Ratio oferta/demanda
   - Tiempo estimado de absorción
   - Indicadores de presión de mercado

## Consideraciones Técnicas

### Escalabilidad

- Diseño para soportar múltiples ciudades/regiones
- Particionamiento de datos para manejar crecimiento
- Procesamiento incremental donde sea posible

### Calidad de Datos

- Tests automatizados en cada capa de transformación
- Monitoreo de completitud y consistencia
- Alertas para anomalías y desviaciones

### Seguridad

- Gestión segura de credenciales de API
- Control de acceso a datos sensibles
- Cumplimiento con GDPR para datos personales

### DevOps

- Control de versiones para código y modelos
- Documentación automatizada
- Entornos separados (desarrollo, producción)

## Próximos Pasos de Implementación

1. **Fase 1: Configuración Inicial**
   - Crear estructura de repositorio
   - Configurar entorno de desarrollo
   - Implementar cliente API básico

2. **Fase 2: Pipeline de Extracción**
   - Desarrollar DAGs de Airflow
   - Configurar BigQuery
   - Implementar validación básica

3. **Fase 3: Modelos dbt**
   - Configurar proyecto dbt
   - Implementar modelos base y staging
   - Desarrollar tests de datos

4. **Fase 4: Modelos Analíticos**
   - Implementar modelos intermediate y mart
   - Desarrollar cálculos de KPIs
   - Crear notebooks para análisis exploratorio

5. **Fase 5: Automatización y Monitoreo**
   - Configurar pipeline completo
   - Implementar monitoreo y alertas
   - Documentar arquitectura y procesos

## Dependencias y Requisitos

### Software

```
# API y procesamiento de datos
requests==2.31.0
pandas==2.1.0
numpy==1.25.2

# Airflow
apache-airflow==2.7.1
apache-airflow-providers-google==10.1.0

# BigQuery
google-cloud-bigquery==3.11.4
pyarrow==13.0.0

# dbt
dbt-core==1.5.1
dbt-bigquery==1.5.1

# Utilidades
python-dotenv==1.0.0
pydantic==2.3.0
```

### Infraestructura

- Cuenta de Google Cloud Platform
- Proyecto BigQuery configurado
- Entorno para ejecución de Airflow
- Credenciales para API de Idealista (u otras fuentes)

## Conclusión

Esta arquitectura proporciona un framework robusto y escalable para el análisis del mercado inmobiliario español. El diseño modular permite una implementación incremental, comenzando con funcionalidades básicas y expandiendo gradualmente hacia análisis más sofisticados y cobertura geográfica más amplia.

La combinación de Airflow para orquestación, BigQuery para almacenamiento, y dbt para transformación ofrece un stack tecnológico moderno y probado para pipelines de datos analíticos, mientras que la estructura clara del repositorio y la documentación facilitan la colaboración y mantenimiento del proyecto.
