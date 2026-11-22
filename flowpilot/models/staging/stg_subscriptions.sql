
{{ config(materialized='view') }}

WITH source_data AS (

    SELECT
        subscription_id,
        user_id,
        account_id,
        started_at,
        cancelled_at,
        monthly_price_eur

    FROM {{ source('flowpilot_raw', 'subscriptions') }}

),

cleaned AS (

    SELECT
        NULLIF(TRIM(subscription_id), '') AS subscription_id,
        NULLIF(TRIM(user_id), '') AS user_id,
        NULLIF(TRIM(account_id), '') AS account_id,

        TO_DATE(
            NULLIF(TRIM(started_at), ''),
            'YYYY-MM-DD'
        ) AS started_at,

        TO_DATE(
            NULLIF(TRIM(cancelled_at), ''),
            'YYYY-MM-DD'
        ) AS cancelled_at,

        TO_DECIMAL(
            NULLIF(TRIM(monthly_price_eur), ''),
            12,
            2
        ) AS monthly_price_eur

    FROM source_data

)

SELECT
    subscription_id,
    user_id,
    account_id,
    started_at,
    cancelled_at,
    monthly_price_eur

FROM cleaned
