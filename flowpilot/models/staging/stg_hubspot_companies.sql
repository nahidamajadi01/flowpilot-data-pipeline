
WITH source AS (

    SELECT *
    FROM {{ source('flowpilot_raw', 'hubspot_companies') }}

),

renamed AS (

    SELECT
        TRIM(DATA:id::VARCHAR) AS company_id,
        TRIM(DATA:properties:hs_object_id::VARCHAR) AS hs_object_id,

        NULLIF(TRIM(DATA:properties:name::VARCHAR), '') AS company_name,
        NULLIF(LOWER(TRIM(DATA:properties:domain::VARCHAR)), '') AS domain,
        NULLIF(TRIM(DATA:url::VARCHAR), '') AS hubspot_url,

        TRY_TO_BOOLEAN(DATA:archived::VARCHAR) AS is_archived,

        TRY_TO_TIMESTAMP_TZ(DATA:createdAt::VARCHAR) AS created_at,
        TRY_TO_TIMESTAMP_TZ(DATA:updatedAt::VARCHAR) AS updated_at,

        DATA AS raw

    FROM source

)

SELECT *
FROM renamed
