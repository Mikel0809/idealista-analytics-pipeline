# Project Brief: Madrid Real Estate Investment Analytics Pipeline

## Executive Summary

This project aims to develop an end-to-end analytics pipeline to identify emerging trends in the Spanish real estate market, with emphasis on early detection of areas with appreciation potential. Using data from real estate portals, we will build a solution that combines modern data engineering with advanced analytics to generate actionable insights about the market, focusing on southern Madrid.

## Project Objectives

1. Build an automated and scalable data pipeline that extracts, processes, and analyzes real estate data
2. Develop advanced KPIs to identify emerging zones before prices rise significantly
3. Implement analytics models for price trends and investment opportunities
4. Create a modern technical architecture based on dbt, BigQuery, and Airflow

## Scope

### Included
- Data extraction from Idealista API (via RapidAPI)
- Processing and storage in Google BigQuery
- Transformations with dbt following three-layer architecture
- Complete orchestration with Apache Airflow
- Development of KPIs and analytical metrics
- Initial implementation for southern Madrid

### Excluded
- Frontend/UI development (possible future extension)
- Integration with external transaction systems
- Unstructured data analysis (images, textual descriptions)

## Technology Stack

- **Data Extraction**: Python, RESTful APIs
- **Orchestration**: Apache Airflow
- **Storage**: Google BigQuery
- **Transformation**: dbt (data build tool)
- **Analysis**: Python (pandas, numpy)
- **Visualization**: Optional (Looker, Data Studio)

## Data Architecture

### BigQuery Schema Structure
1. **RAW Schema** (`raw_data`): Extracted data without modifications
2. **INTERMEDIATE Schema** (`dbt_intermediate`): Intermediate transformations
3. **FINAL Schema** (`dbt_mart`): Final analytical models

### Data Flow
1. Airflow extracts data from APIs and loads it into BigQuery (RAW schema)
2. dbt transforms the data into intermediate and final models
3. Final models feed KPIs and analytical insights

## Key Performance Indicators

### 1. Emerging Zones Index
Composite metric that identifies neighborhoods with appreciation potential based on:
- Acceleration in price growth
- Reduction in average time on market
- Increase in transaction volume
- Contextual factors (new businesses, urban projects, demographics)

### 2. Investment Return Analysis
- Estimated ROI (purchase vs. rental)
- 5-year appreciation projection
- Comparison between zones

### 3. Market Saturation Index
- Supply/demand balance by zone
- Estimated time to absorb current supply
- Buyer/seller pressure indicator

## Technical Requirements

### Data Extraction
- Frequency: Daily
- Estimated volume: 1-2K records daily
- API rate limit handling and pagination
- Incremental change detection

### Processing
- Idempotent transformations
- Automated data quality tests
- Data lineage documentation

### Analysis
- Analytics models updated daily
- Trend anomaly detection
- Configurable alerts for significant changes

## Implementation Plan

### Phase 1: Setup and Extraction (2-3 weeks)
- Configure technical environment
- Implement basic data extraction
- Design BigQuery schema

### Phase 2: Transformation and Basic KPIs (3-4 weeks)
- Develop dbt models
- Implement basic metric calculations
- Create initial visualizations

### Phase 3: Advanced Analysis (4-5 weeks)
- Develop emerging zones identification algorithm
- Implement opportunity classification
- Validate results with historical data

### Phase 4: Refinement and Automation (2-3 weeks)
- Optimize pipeline for efficiency
- Implement automated alerts
- Create interactive dashboard

## Additional Considerations

### Scalability
- Design to support multiple cities/regions
- Ability to incorporate new data sources
- Optimization for data volume growth

### Data Quality
- Validations at each pipeline stage
- Handling of missing or inconsistent data
- Quality metrics logging

### Privacy and Compliance
- Anonymization of sensitive data
- GDPR compliance for personal data
- Secure credential storage

## Success Metrics

1. **Technical**:
   - Fully automated and resilient pipeline
   - Processing time < 2 hours for complete cycle
   - Test coverage > 80%

2. **Analytical**:
   - Accuracy > 70% in identifying emerging zones
   - Average error < 10% in price analysis
   - Ability to detect trends 3-6 months before traditional indicators

## Dependencies and Risks

### Dependencies
- Access to Idealista API via RapidAPI (may require payment)
- Availability of historical data for model training
- Computing resources for BigQuery and Airflow

### Risks
- Changes to the Idealista API that affect extraction
- Limitations in available data volume
- Complexity in detecting emerging patterns
- Seasonal variability in the real estate markets

## Next Steps

1. Validate the brief with the technical team
2. Define the detailed architecture with the lead architect
3. Configure the development environment
4. Implement a proof of concept for data extraction
