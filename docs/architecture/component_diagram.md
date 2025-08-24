# Diagrama de Componentes: Pipeline de Análisis Inmobiliario

## Visión General del Sistema

Este diagrama muestra la arquitectura de componentes del pipeline de análisis inmobiliario, detallando las interacciones entre los diferentes módulos y el flujo de datos a través del sistema.

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                     │
│                               FUENTES DE DATOS                                      │
│                                                                                     │
│  ┌───────────────┐        ┌───────────────┐        ┌───────────────┐                │
│  │  API Idealista│        │  Otros Portales│        │  Datos Externos│                │
│  │  Inmobiliarios│        │  Inmobiliarios │        │  (Opcional)   │                │
│  └───────┬───────┘        └───────┬───────┘        └───────┬───────┘                │
│          │                        │                        │                        │
└──────────┼────────────────────────┼────────────────────────┼────────────────────────┘
           │                        │                        │
           ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                     │
│                           CAPA DE EXTRACCIÓN (AIRFLOW)                              │
│                                                                                     │
│  ┌───────────────┐        ┌───────────────┐        ┌───────────────┐                │
│  │  DAG Extracción│        │  Cliente API   │        │  Validación    │                │
│  │  Diaria       │───────▶│  Python        │───────▶│  Inicial       │                │
│  └───────────────┘        └───────────────┘        └───────┬───────┘                │
│                                                            │                        │
└────────────────────────────────────────────────────────────┼────────────────────────┘
                                                             │
                                                             ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                     │
│                           ALMACENAMIENTO (BIGQUERY)                                 │
│                                                                                     │
│  ┌───────────────┐        ┌───────────────┐        ┌───────────────┐                │
│  │  Esquema      │        │  Esquema      │        │  Esquema      │                │
│  │  base         │───────▶│  staging      │───────▶│  intermediate │───────┐        │
│  └───────────────┘        └───────────────┘        └───────────────┘       │        │
│                                                                            │        │
│                                                                            ▼        │
│                                                                    ┌───────────────┐│
│                                                                    │  Esquema      ││
│                                                                    │  mart         ││
│                                                                    └───────┬───────┘│
│                                                                            │        │
└────────────────────────────────────────────────────────────────────────────┼────────┘
                                                                             │
                                                                             ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                     │
│                           TRANSFORMACIÓN (DBT)                                      │
│                                                                                     │
│  ┌───────────────┐        ┌───────────────┐        ┌───────────────┐                │
│  │  Modelos      │        │  Modelos      │        │  Modelos      │                │
│  │  Base         │───────▶│  Staging      │───────▶│  Intermediate │───────┐        │
│  └───────────────┘        └───────────────┘        └───────────────┘       │        │
│                                                                            │        │
│  ┌───────────────┐        ┌───────────────┐        ┌───────────────┐       │        │
│  │  Tests        │        │  Macros       │        │  Documentación│       │        │
│  │  de Datos     │        │  dbt          │        │  Automática   │       │        │
│  └───────────────┘        └───────────────┘        └───────────────┘       │        │
│                                                                            ▼        │
│                                                                    ┌───────────────┐│
│                                                                    │  Modelos      ││
│                                                                    │  Mart         ││
│                                                                    └───────┬───────┘│
│                                                                            │        │
└────────────────────────────────────────────────────────────────────────────┼────────┘
                                                                             │
                                                                             ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                     │
│                           ANÁLISIS Y CONSUMO                                        │
│                                                                                     │
│  ┌───────────────┐        ┌───────────────┐        ┌───────────────┐                │
│  │  Modelos      │        │  Cálculo      │        │  Visualización│                │
│  │  Predictivos  │        │  de KPIs      │        │  (Futuro)     │                │
│  └───────────────┘        └───────────────┘        └───────────────┘                │
│                                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐                  │
│  │                                                               │                  │
│  │  Índice de     Análisis de      Índice de                     │                  │
│  │  Zonas         Rentabilidad     Saturación                    │                  │
│  │  Emergentes    por Inversión    de Mercado                    │                  │
│  │                                                               │                  │
│  └───────────────────────────────────────────────────────────────┘                  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## Flujo de Datos

1. **Extracción**:
   - Los DAGs de Airflow programados extraen datos de las APIs inmobiliarias
   - El cliente Python maneja autenticación, paginación y reintentos
   - Se realiza una validación inicial de estructura y completitud
   - Los datos se cargan en tablas del esquema `base` en BigQuery

2. **Transformación**:
   - Los modelos dbt procesan los datos a través de las capas:
     - `base` → `staging` → `intermediate` → `mart`
   - Cada capa aplica transformaciones específicas:
     - `base`: Tipado y renombrado
     - `staging`: Limpieza y normalización
     - `intermediate`: Lógica de negocio y agregaciones
     - `mart`: KPIs y modelos específicos por dominio
   - Tests de datos validan la calidad en cada paso
   - Macros dbt proporcionan funcionalidad reutilizable

3. **Análisis**:
   - Los modelos finales en el esquema `mart` alimentan:
     - Cálculos de KPIs (Índice de Zonas Emergentes, etc.)
     - Modelos predictivos para tendencias de precios
     - Visualizaciones y dashboards (fase posterior)

## Componentes Clave

### Capa de Extracción
- **DAGs de Airflow**: Orquestación del pipeline
- **Cliente API**: Interacción con fuentes de datos
- **Validación Inicial**: Verificación de estructura y completitud

### Capa de Almacenamiento
- **Esquemas BigQuery**: Organización lógica de datos
- **Particionamiento**: Optimización por fecha
- **Políticas de Retención**: Gestión del ciclo de vida de datos

### Capa de Transformación
- **Modelos dbt**: Transformaciones SQL declarativas
- **Tests de Datos**: Validación de calidad
- **Documentación**: Generación automática de documentación

### Capa de Análisis
- **Modelos Predictivos**: Algoritmos para tendencias de precios
- **Cálculo de KPIs**: Métricas de negocio clave
- **Visualización**: Presentación de insights (fase posterior)

## Interacciones entre Componentes

- **Airflow → BigQuery**: Carga de datos extraídos
- **dbt → BigQuery**: Transformaciones SQL
- **Análisis → BigQuery**: Consultas a modelos finales
- **Airflow → dbt**: Orquestación de transformaciones

## Consideraciones de Implementación

- **Frecuencia de Actualización**:
  - Extracción: Diaria
  - Transformaciones: Diaria (tras extracción)
  - Modelos analíticos: Semanal

- **Monitoreo**:
  - Logs de Airflow para extracción
  - Tests dbt para calidad de datos
  - Alertas para fallos en el pipeline

- **Escalabilidad**:
  - Diseño modular para añadir nuevas fuentes
  - Estructura preparada para múltiples ciudades/regiones
