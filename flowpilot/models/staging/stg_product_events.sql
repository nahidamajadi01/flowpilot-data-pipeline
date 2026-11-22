
SELECT
    event_id::VARCHAR AS event_id,
    user_id::VARCHAR AS user_id,
    account_id::VARCHAR AS account_id,
    session_id::VARCHAR AS session_id,

    TRIM(event_name) AS event_name,
    TRIM(feature_area) AS feature_area,
    TRIM(platform) AS platform,
    TRIM(plan_at_event) AS plan_at_event,

    TRY_TO_TIMESTAMP_TZ(event_timestamp) AS event_timestamp,
    TRY_TO_NUMBER(duration_ms) AS duration_ms

FROM {{ source('flowpilot_raw', 'product_events') }}
