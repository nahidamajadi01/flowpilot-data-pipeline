
SELECT
    -- Contact identifier
    DATA:id::VARCHAR AS contact_id,

    -- Archive status
    DATA:archived::BOOLEAN AS is_archived,

    -- Creation and modification timestamps
    TRY_TO_TIMESTAMP_TZ(DATA:createdAt::VARCHAR) AS created_at,
    TRY_TO_TIMESTAMP_TZ(DATA:updatedAt::VARCHAR) AS updated_at,

    -- Contact information
    LOWER(TRIM(DATA:properties:email::VARCHAR)) AS email,
    TRIM(DATA:properties:firstname::VARCHAR) AS first_name,
    TRIM(DATA:properties:lastname::VARCHAR) AS last_name,

    -- Original HubSpot record URL
    DATA:url::VARCHAR AS url,

    -- Preserve original JSON payload
    DATA AS source_payload

FROM {{ source('flowpilot_raw', 'hubspot_contacts') }}
