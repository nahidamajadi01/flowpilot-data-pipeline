
{{ config(
    materialized = 'view'
) }}

WITH source AS (

    SELECT
        DATA AS source_payload,

        DATA:id::STRING AS id_raw,
        DATA:archived::STRING AS archived_raw,
        DATA:createdAt::STRING AS created_at_raw,
        DATA:updatedAt::STRING AS updated_at_raw,
        DATA:url::STRING AS url_raw,

        DATA:properties:amount::STRING AS amount_raw,
        DATA:properties:closedate::STRING AS closedate_raw,
        DATA:properties:dealname::STRING AS dealname_raw,
        DATA:properties:dealstage::STRING AS dealstage_raw,
        DATA:properties:pipeline::STRING AS pipeline_raw

    FROM {{ source('flowpilot_raw', 'hubspot_deals') }}

),

staged AS (

    SELECT
        NULLIF(TRIM(id_raw), '') AS id,

        TRY_TO_BOOLEAN(archived_raw) AS archived,

        TRY_TO_TIMESTAMP_TZ(NULLIF(TRIM(created_at_raw), '')) AS created_at,
        TRY_TO_TIMESTAMP_TZ(NULLIF(TRIM(updated_at_raw), '')) AS updated_at,

        NULLIF(TRIM(url_raw), '') AS url,

        TRY_TO_DECIMAL(NULLIF(TRIM(amount_raw), ''), 18, 2) AS amount,
        TRY_TO_TIMESTAMP_TZ(NULLIF(TRIM(closedate_raw), '')) AS close_date,

        NULLIF(TRIM(dealname_raw), '') AS deal_name,
        NULLIF(TRIM(dealstage_raw), '') AS deal_stage_id,
        NULLIF(TRIM(pipeline_raw), '') AS pipeline_id,

        source_payload

    FROM source

)

SELECT *
FROM staged
