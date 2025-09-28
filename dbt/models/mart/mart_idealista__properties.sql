{{
    config(
        materialized='view',
        alias='madrid_south_real_estate_metrics'
    )
}}

select * from {{ ref('int_idealista__properties_enriched') }}
