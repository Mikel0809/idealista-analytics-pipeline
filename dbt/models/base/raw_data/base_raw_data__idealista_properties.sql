
with
    source as (select * from {{ source("idealista", "idealista_properties") }}),


    renamed as (

        select
            propertyCode as property_code,
            cast(price as float64) as price,
            propertyType as property_type,
            operation as operation,
            cast(size as float64) as size,
            cast(rooms as int64) as rooms,
            cast(bathrooms as int64) as bathrooms,
            address as address,
            province as province,
            municipality as municipality,
            locationId as location_id,
            cast(latitude as float64) as latitude,
            cast(longitude as float64) as longitude,
            url as url,
            description as description,
            status as status,
            phoneNumberForMobileDialing as phone_number_for_mobile_dialing,
            contactName as contact_name,
            userType as user_type,
            cast(hasParkingSpace as bool) as has_parking_space,
            cast(priceByArea as float64) as price_by_area,
            cast(hasSwimmingPool as bool) as has_swimming_pool,
            cast(hasTerrace as bool) as has_terrace,
            cast(hasAirConditioning as bool) as has_air_conditioning,
            cast(hasBoxRoom as bool) as has_box_room,
            cast(hasGarden as bool) as has_garden,
            origin_location_name as origin_location_name,
            row_number() over (partition by propertyCode) as rn
        from source
        qualify rn = 1 --Data quality issues were reported from the API, as we do not have control over it, we are removing duplicates in dbt.

    )

select * from renamed
