with source as (

    select * from {{ source('flowpilot_raw', 'ga4_events') }}

),

parsed as (

    select
        nullif(trim(event_id), '')       as event_id,
        nullif(trim(user_id), '')        as user_id,
        nullif(trim(session_id), '')     as session_id,
        nullif(trim(campaign_id), '')    as campaign_id,
        lower(nullif(trim(event_name), '')) as event_name,
        coalesce(lower(nullif(trim(traffic_source), '')), 'unknown') as traffic_source,
        convert_timezone('UTC', try_to_timestamp_tz(event_timestamp)) as event_timestamp_utc,
        try_to_number(engagement_time_msec) as raw_engagement_time_msec
    from source

),

cleaned as (

    select
        event_id,
        user_id,
        session_id,
        campaign_id,
        event_name,
        traffic_source,
        event_timestamp_utc,
        event_timestamp_utc::date as event_date,
        raw_engagement_time_msec,
        greatest(coalesce(raw_engagement_time_msec, 0), 0) as engagement_time_msec,
        campaign_id is not null as has_campaign,
        coalesce(raw_engagement_time_msec, 0) > 0 as is_engaged_event
    from parsed
    where event_id is not null
      and event_timestamp_utc is not null

),

deduplicated as (

    select *
    from cleaned
    qualify row_number() over (
        partition by event_id
        order by event_timestamp_utc desc,
                 raw_engagement_time_msec desc nulls last  -- replace with a load timestamp if you have one
    ) = 1

)

select * from deduplicated