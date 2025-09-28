{{
    config(
        materialized='table',
        schema='dbt_staging'
    )
}}

with
    base_data as (
        select * from {{ ref('base_raw_data_idealista__properties') }}
    ),

    cleaned as (
        select
            property_code,
            price,
            property_type,
            operation,
            size,
            rooms,
            bathrooms,
            address,
            province,
            municipality,
            location_id,
            latitude,
            longitude,
            url,
            description,
            status,
            phone_number_for_mobile_dialing,
            contact_name,
            user_type,
            has_parking_space,
            price_by_area,
            has_swimming_pool,
            has_terrace,
            has_air_conditioning,
            has_box_room,
            has_garden,
            origin_location_name,
            
            -- Data quality flags
            case 
                when price is null or price <= 0 then false
                when size is null or size <= 0 then false
                when latitude is null or longitude is null then false
                else true
            end as is_valid_record,
            
            -- Timestamp for tracking when the record was processed
            current_timestamp() as processed_at
            
        from base_data
        where 
            property_code is not null
            and status is not null
    )

select * from cleaned
