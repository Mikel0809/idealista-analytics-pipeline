# Project Brief: Análisis Predictivo del Mercado Inmobiliario Español

## Resumen Ejecutivo

Este proyecto tiene como objetivo desarrollar un pipeline analítico end-to-end para identificar tendencias emergentes en el mercado inmobiliario español, con énfasis en la detección temprana de zonas con potencial de revalorización. Utilizando datos de portales inmobiliarios, se construirá una solución que combine ingeniería de datos moderna con análisis predictivo para generar insights accionables sobre el mercado.

## Objetivos del Proyecto

1. Construir un pipeline de datos automatizado y escalable que extraiga, procese y analice datos inmobiliarios
2. Desarrollar KPIs avanzados para identificar zonas emergentes antes de que los precios suban significativamente
3. Implementar modelos predictivos para tendencias de precios y oportunidades de inversión
4. Crear una arquitectura técnica moderna basada en dbt, BigQuery y Airflow

## Alcance

### Incluido
- Extracción de datos de API de Idealista (o alternativa)
- Procesamiento y almacenamiento en BigQuery
- Transformaciones con dbt siguiendo arquitectura de tres capas
- Orquestación completa con Airflow
- Desarrollo de KPIs y métricas analíticas
- Implementación inicial para 1-2 ciudades principales (Madrid/Barcelona)

### Excluido
- Desarrollo de frontend/UI (posible extensión futura)
- Integración con sistemas externos de transacción
- Análisis de datos no estructurados (imágenes, descripciones textuales)

## Stack Tecnológico

- **Extracción de datos**: Python, APIs RESTful
- **Orquestación**: Apache Airflow
- **Almacenamiento**: Google BigQuery
- **Transformación**: dbt (data build tool)
- **Análisis**: Python (pandas, scikit-learn)
- **Visualización**: Opcional (Looker, Data Studio)

## Arquitectura de Datos

### Estructura de Esquemas en BigQuery
1. **Esquema RAW** (`idealista_raw`): Datos extraídos sin modificaciones
2. **Esquema INTERMEDIATE** (`idealista_intermediate`): Transformaciones intermedias
3. **Esquema FINAL** (`idealista_analytics`): Modelos analíticos finales

### Flujo de Datos
1. Airflow extrae datos de APIs y los carga en BigQuery (esquema RAW)
2. dbt transforma los datos en modelos intermedios y finales
3. Los modelos finales alimentan KPIs y análisis predictivos

## KPIs Principales

### 1. Índice de Zonas Emergentes
Métrica compuesta que identifica barrios con potencial de revalorización basada en:
- Aceleración en el crecimiento de precios
- Reducción del tiempo medio en mercado
- Incremento en volumen de transacciones
- Factores contextuales (nuevos negocios, proyectos urbanos, demografía)

### 2. Análisis de Rentabilidad por Inversión
- ROI estimado (compra vs. alquiler)
- Proyección de revalorización a 5 años
- Comparativa entre zonas

### 3. Índice de Saturación de Mercado
- Equilibrio oferta/demanda por zona
- Tiempo estimado para absorber oferta actual
- Indicador de presión compradora/vendedora

## Requisitos Técnicos

### Extracción de Datos
- Frecuencia: Diaria
- Volumen estimado: 10-50K registros diarios
- Manejo de límites de API y paginación
- Detección de cambios incrementales

### Procesamiento
- Transformaciones idempotentes
- Tests automatizados para calidad de datos
- Documentación de linaje de datos

### Análisis
- Modelos predictivos actualizados semanalmente
- Detección de anomalías en tendencias
- Alertas configurables para cambios significativos

## Plan de Implementación

### Fase 1: Configuración y Extracción (2-3 semanas)
- Configurar entorno técnico
- Implementar extracción básica de datos
- Diseñar esquema en BigQuery

### Fase 2: Transformación y KPIs Básicos (3-4 semanas)
- Desarrollar modelos dbt
- Implementar cálculos de métricas básicas
- Crear primeras visualizaciones

### Fase 3: Análisis Avanzado y Predicción (4-5 semanas)
- Desarrollar algoritmo de identificación de zonas emergentes
- Implementar modelos predictivos
- Validar resultados con datos históricos

### Fase 4: Refinamiento y Automatización (2-3 semanas)
- Optimizar pipeline para eficiencia
- Implementar alertas automáticas
- Crear dashboard interactivo

## Consideraciones Adicionales

### Escalabilidad
- Diseño para soportar múltiples ciudades/regiones
- Capacidad para incorporar nuevas fuentes de datos
- Optimización para crecimiento de volumen de datos

### Calidad de Datos
- Validaciones en cada etapa del pipeline
- Manejo de datos faltantes o inconsistentes
- Registro de métricas de calidad

### Privacidad y Cumplimiento
- Anonimización de datos sensibles
- Cumplimiento con GDPR para datos personales
- Almacenamiento seguro de credenciales

## Métricas de Éxito

1. **Técnicas**:
   - Pipeline completamente automatizado y resiliente
   - Tiempo de procesamiento < 2 horas para ciclo completo
   - Cobertura de tests > 80%

2. **Analíticas**:
   - Precisión > 70% en identificación de zonas emergentes
   - Error medio < 10% en predicciones de precios
   - Capacidad para detectar tendencias 3-6 meses antes que indicadores tradicionales

## Dependencias y Riesgos

### Dependencias
- Acceso a API de Idealista (requiere solicitud y posible pago)
- Disponibilidad de datos históricos para entrenamiento de modelos
- Recursos de computación para BigQuery y Airflow

### Riesgos
- Limitaciones o cambios en APIs de fuentes de datos
- Calidad inconsistente de datos inmobiliarios
- Complejidad en la modelización de factores externos (económicos, sociales)

## Próximos Pasos

1. Validación del brief con equipo técnico
2. Definición detallada de arquitectura con agente arquitecto
3. Configuración de entorno de desarrollo
4. Implementación de prueba de concepto para extracción de datos
