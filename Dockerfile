
FROM python:3.12-slim

WORKDIR /workspace/flowpilot

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    dbt-core==1.13.0b1 \
    dbt-snowflake==1.12.5

ENTRYPOINT ["dbt"]
