{{
    config(
        materialized='table'
    )
}}

with
    staging_data as (
        select * from {{ ref('stg_idealista__properties') }}
        where is_valid_record = true
    ),

    -- Geographic zone metrics calculations
    location_metrics as (
        select
            municipality,
            round(latitude, 3) as lat_zone,
            round(longitude, 3) as lng_zone,
            
            -- Price metrics by zone
            round(avg(price), 2) as avg_price_zone,
            -- Using approximate median via approx_quantiles as percentile_cont is not supported
            round(approx_quantiles(price, 100)[offset(50)], 2) as median_price_zone,
            round(min(price), 2) as min_price_zone,
            round(max(price), 2) as max_price_zone,
            round(stddev(price), 2) as stddev_price_zone,
            
            -- Price per m2 metrics by zone
            round(avg(price_by_area), 2) as avg_price_m2_zone,
            round(approx_quantiles(price_by_area, 100)[offset(50)], 2) as median_price_m2_zone,
            
            -- Size metrics by zone
            round(avg(size), 2) as avg_size_zone,
            round(approx_quantiles(size, 100)[offset(50)], 2) as median_size_zone,
            
            -- Counters by zone
            count(*) as properties_count_zone,
            count(distinct property_type) as property_types_count_zone,
            
            -- Feature percentages by zone
            round(avg(cast(has_parking_space as int64)), 2) as pct_parking_zone,
            round(avg(cast(has_swimming_pool as int64)), 2) as pct_pool_zone,
            round(avg(cast(has_terrace as int64)), 2) as pct_terrace_zone,
            round(avg(cast(has_air_conditioning as int64)), 2) as pct_ac_zone,
            round(avg(cast(has_garden as int64)), 2) as pct_garden_zone
            
        from staging_data
        group by municipality, lat_zone, lng_zone
    ),

    -- Property type metrics calculations
    property_type_metrics as (
        select
            property_type,
            operation,
            
            -- Price metrics by type
            round(avg(price), 2) as avg_price_type,
            round(approx_quantiles(price, 100)[offset(50)], 2) as median_price_type,
            round(min(price), 2) as min_price_type,
            round(max(price), 2) as max_price_type,
            
            -- Price per m2 metrics by type
            round(avg(price_by_area), 2) as avg_price_m2_type,
            round(approx_quantiles(price_by_area, 100)[offset(50)], 2) as median_price_m2_type,
            
            -- Counters by type
            count(*) as properties_count_type
            
        from staging_data
        group by property_type, operation
    ),

    -- Main enriched table
    enriched as (
        select
            s.*,
            
            -- Simplified geographic zone
            round(s.latitude, 3) as lat_zone,
            round(s.longitude, 3) as lng_zone,
            
            -- Price segmentation
            case 
                when s.price < 200000 then 'Budget'
                when s.price < 400000 then 'Mid-Range'
                when s.price < 600000 then 'High-End'
                else 'Premium'
            end as price_segment,
            
            -- Size segmentation
            case 
                when s.size < 60 then 'Small'
                when s.size < 100 then 'Medium'
                when s.size < 150 then 'Large'
                else 'Extra Large'
            end as size_segment,
            
            -- Premium features index
            (cast(s.has_parking_space as int64) + 
             cast(s.has_swimming_pool as int64) + 
             cast(s.has_terrace as int64) + 
             cast(s.has_air_conditioning as int64) + 
             cast(s.has_garden as int64)) as premium_features_count,
            
            -- Zone metrics
            lm.avg_price_zone,
            lm.median_price_zone,
            lm.min_price_zone,
            lm.max_price_zone,
            lm.stddev_price_zone,
            lm.avg_price_m2_zone,
            lm.median_price_m2_zone,
            lm.avg_size_zone,
            lm.median_size_zone,
            lm.properties_count_zone,
            lm.property_types_count_zone,
            lm.pct_parking_zone,
            lm.pct_pool_zone,
            lm.pct_terrace_zone,
            lm.pct_ac_zone,
            lm.pct_garden_zone,
            
            -- Property type metrics
            ptm.avg_price_type,
            ptm.median_price_type,
            ptm.min_price_type,
            ptm.max_price_type,
            ptm.avg_price_m2_type,
            ptm.median_price_m2_type,
            ptm.properties_count_type,
            
            -- Calculated KPIs
            -- Price deviation from zone average
            case 
                when lm.avg_price_zone > 0 then 
                    round((s.price - lm.avg_price_zone) / lm.avg_price_zone * 100, 2)
                else null
            end as price_deviation_zone_pct,
            
            -- Price per m2 deviation from zone average
            case 
                when lm.avg_price_m2_zone > 0 then 
                    round((s.price_by_area - lm.avg_price_m2_zone) / lm.avg_price_m2_zone * 100, 2)
                else null
            end as price_m2_deviation_zone_pct,
            
            -- Price deviation from property type average
            case 
                when ptm.avg_price_type > 0 then 
                    round((s.price - ptm.avg_price_type) / ptm.avg_price_type * 100, 2)
                else null
            end as price_deviation_type_pct,
            
            -- Competitiveness index (price vs features)
            case 
                when s.price_by_area > 0 and lm.avg_price_m2_zone > 0 then
                    round(
                        ((cast(s.has_parking_space as int64) + 
                          cast(s.has_swimming_pool as int64) + 
                          cast(s.has_terrace as int64) + 
                          cast(s.has_air_conditioning as int64) + 
                          cast(s.has_garden as int64)) / 5.0) / 
                        (s.price_by_area / lm.avg_price_m2_zone), 3
                    )
                else null
            end as competitiveness_index,
            
            -- Opportunity classification
            case 
                when s.price < lm.avg_price_zone * 0.8 and 
                     (cast(s.has_parking_space as int64) + 
                      cast(s.has_swimming_pool as int64) + 
                      cast(s.has_terrace as int64) + 
                      cast(s.has_air_conditioning as int64) + 
                      cast(s.has_garden as int64)) >= 2 then 'Opportunity'
                when s.price > lm.avg_price_zone * 1.2 then 'Overvalued'
                else 'Market'
            end as opportunity_classification
            
        from staging_data s
        left join location_metrics lm 
            on s.municipality = lm.municipality 
            and round(s.latitude, 3) = lm.lat_zone 
            and round(s.longitude, 3) = lm.lng_zone
        left join property_type_metrics ptm 
            on s.property_type = ptm.property_type 
            and s.operation = ptm.operation
    )

select * from enriched
