
{{ config(materialized='table') }}

WITH source_metrics AS (

    -- 1. HubSpot Companies
    SELECT
        'hubspot_companies' AS source_name,
        COUNT(*) AS record_count,
        COUNT(DISTINCT company_id) AS distinct_record_count,
        COUNT_IF(company_id IS NOT NULL)
            - COUNT(DISTINCT company_id) AS duplicate_record_count,
        COUNT_IF(company_id IS NULL) AS missing_key_count,
        MIN(created_at::DATE) AS earliest_record_date,
        MAX(created_at::DATE) AS latest_record_date
    FROM {{ ref('stg_hubspot_companies') }}

    UNION ALL

    -- 2. HubSpot Contacts
    SELECT
        'hubspot_contacts',
        COUNT(*),
        COUNT(DISTINCT contact_id),
        COUNT_IF(contact_id IS NOT NULL)
            - COUNT(DISTINCT contact_id),
        COUNT_IF(contact_id IS NULL),
        MIN(created_at::DATE),
        MAX(created_at::DATE)
    FROM {{ ref('stg_hubspot_contacts') }}

    UNION ALL

    -- 3. HubSpot Deals
    SELECT
        'hubspot_deals',
        COUNT(*),
        COUNT(DISTINCT id),
        COUNT_IF(id IS NOT NULL)
            - COUNT(DISTINCT id),
        COUNT_IF(id IS NULL),
        MIN(created_at::DATE),
        MAX(created_at::DATE)
    FROM {{ ref('stg_hubspot_deals') }}

    UNION ALL

    -- 4. Subscriptions
    SELECT
        'subscriptions',
        COUNT(*),
        COUNT(DISTINCT subscription_id),
        COUNT_IF(subscription_id IS NOT NULL)
            - COUNT(DISTINCT subscription_id),
        COUNT_IF(subscription_id IS NULL),
        MIN(started_at::DATE),
        MAX(started_at::DATE)
    FROM {{ ref('stg_subscriptions') }}

    UNION ALL

    -- 5. GA4 Events
    SELECT
        'ga4_events',
        COUNT(*),
        COUNT(DISTINCT event_id),
        COUNT_IF(event_id IS NOT NULL)
            - COUNT(DISTINCT event_id),
        COUNT_IF(event_id IS NULL),
        MIN(event_date),
        MAX(event_date)
    FROM {{ ref('stg_ga4_events') }}

    UNION ALL

    -- 6. Meta Ads Daily
    
    -- 6. Meta Ads Daily
    SELECT
        'meta_ads_daily',
        COUNT(*),

        -- Distinct exact records across all nine columns
        COUNT(DISTINCT
            ad_date,
            campaign_id,
            ad_id,
            placement,
            impressions,
            clicks,
            spend_eur,
            platform_conversions,
            currency
        ),

        -- Exact duplicate records
        COUNT_IF(
            ad_date IS NOT NULL
            AND campaign_id IS NOT NULL
            AND ad_id IS NOT NULL
            AND placement IS NOT NULL
        )
        -
        COUNT(DISTINCT
            ad_date,
            campaign_id,
            ad_id,
            placement,
            impressions,
            clicks,
            spend_eur,
            platform_conversions,
            currency
        ),

        -- Missing composite-key components
        COUNT_IF(
            ad_date IS NULL
            OR campaign_id IS NULL
            OR ad_id IS NULL
            OR placement IS NULL
        ),

        MIN(ad_date),
        MAX(ad_date)
    FROM {{ ref('stg_meta_ads_daily') }}

    UNION ALL

    -- 7. Product Events
    SELECT
        'product_events',
        COUNT(*),
        COUNT(DISTINCT event_id),
        COUNT_IF(event_id IS NOT NULL)
            - COUNT(DISTINCT event_id),
        COUNT_IF(event_id IS NULL),
        MIN(event_timestamp::DATE),
        MAX(event_timestamp::DATE)
    FROM {{ ref('stg_product_events') }}

)

SELECT
    source_name,
    record_count,
    distinct_record_count,
    duplicate_record_count,
    missing_key_count,
    earliest_record_date,
    latest_record_date,

    CASE
        WHEN duplicate_record_count = 0
         AND missing_key_count = 0
        THEN 'PASS'
        ELSE 'REVIEW'
    END AS data_quality_status

FROM source_metrics
