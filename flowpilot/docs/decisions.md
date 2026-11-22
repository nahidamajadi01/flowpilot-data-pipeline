
# FlowPilot — Data Engineering Decisions

## GA4_EVENTS

### Profiling findings
- Total records: 1,500,000
- Unique event IDs: 1,500,000
- Duplicate or null event IDs: 0
- Missing user IDs: 0
- Campaign-tagged events: 674,495
- Distinct campaign IDs: 300
- Invalid engagement values: 0
- Negative engagement values: 0
- Latest event: 2025-12-31

### Staging decisions
- Preserve one row per event ID.
- Do not deduplicate; no duplicate IDs were found.
- Convert event timestamps from VARCHAR to TIMESTAMP_TZ.
- Convert engagement time to a numeric type.
- Standardize categorical values using TRIM, LOWER and UPPER.
- Convert blank campaign IDs to NULL.
- Preserve original campaign identifiers for matching with Meta Ads.

### Pending validation
- Confirm timestamp conversion results.
- Confirm campaign IDs match Meta Ads.
- Verify source and staging dbt tests.
