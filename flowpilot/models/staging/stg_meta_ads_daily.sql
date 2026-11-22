
{{ config(materialized='view') }}

WITH source_data AS (

    SELECT *
    FROM {{ source('flowpilot_raw', 'meta_ads_daily') }}

),

cleaned AS (

    SELECT
        TRY_TO_DATE("DATE"::VARCHAR, 'YYYY-MM-DD') AS ad_date,

        NULLIF(TRIM(CAMPAIGN_ID::VARCHAR), '') AS campaign_id,
        NULLIF(TRIM(AD_ID::VARCHAR), '') AS ad_id,

        LOWER(NULLIF(TRIM(PLACEMENT::VARCHAR), '')) AS placement,

        TRY_TO_NUMBER(IMPRESSIONS::VARCHAR, 38, 0) AS impressions,
        TRY_TO_NUMBER(CLICKS::VARCHAR, 38, 0) AS clicks,

        TRY_TO_DECIMAL(SPEND::VARCHAR, 18, 4) AS spend_eur,

        TRY_TO_DECIMAL(
            PLATFORM_CONVERSIONS::VARCHAR, 18, 4
        ) AS platform_conversions,

        UPPER(NULLIF(TRIM(CURRENCY::VARCHAR), '')) AS currency

    FROM source_data

)

SELECT *
FROM cleaned
