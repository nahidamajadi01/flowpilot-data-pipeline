# FlowPilot — End-to-End Data Engineering Pipeline

## What is FlowPilot?

FlowPilot is a data engineering project built around a SaaS business environment. It brings together data from different business systems, including CRM, marketing platforms, product analytics, and subscription services, into a centralized Snowflake data warehouse.

The project demonstrates how raw data from multiple sources can be ingested, standardized, transformed, and validated through an automated pipeline.

## The Problem

A SaaS business generates data across multiple independent platforms:

- CRM systems contain customer, company, and sales information.
- Marketing platforms contain advertising and campaign data.
- Product analytics platforms capture user activity and events.
- Subscription systems contain billing and subscription records.

These systems have different data structures, formats, identifiers, and quality issues.

Without a reliable data pipeline, bringing this information together becomes difficult. Inconsistent fields, missing values, duplicate records, timestamp inconsistencies, and unreliable source data can affect downstream data processing.

**The challenge is to build a reliable and automated pipeline that can process data from these different sources while preserving data integrity and making data quality issues visible.**

## The Engineering Approach

FlowPilot uses the following architecture:

**RAW → STAGING → MART**

- **Snowflake:** Centralized data warehouse for raw and transformed data.
- **Python:** Data extraction, ingestion, and synthetic data generation.
- **dbt:** SQL-based transformations, source definitions, and data quality testing.
- **Docker:** Containerized execution environments.
- **Apache Airflow:** Workflow orchestration and task dependencies.

The pipeline processes seven data sources covering CRM, marketing, product events, and subscriptions.

The mart layer provides a consolidated view of data quality across the sources.

## Technical Challenges

Building the pipeline involved several practical engineering challenges:

**1. Source data profiling**

Understanding the actual structure and quality of each source before writing transformations. This included examining missing values, duplicate records, identifiers, timestamps, and data types.

**2. Inconsistent source structures**

Working with different source formats, including JSON and CSV, and resolving differences between source column names and dbt source definitions.

**3. Data quality decisions**

Distinguishing genuine duplicate records from records that share business identifiers but contain different values. Determining which missing values are acceptable rather than applying arbitrary transformations.

**4. dbt configuration and testing**

Configuring dbt sources and staging models consistently, resolving project configuration issues, and implementing tests based on observed source characteristics.

**5. Snowflake connectivity**

Resolving authentication and network policy requirements so that the pipeline could connect to Snowflake from containerized execution environments.

**6. Docker and Airflow integration**

Configuring Docker containers, connecting Airflow to the Docker engine, managing environment variables and volume mounts, and making the DAG independent of hardcoded local paths.

**7. Pipeline orchestration**

Implementing task dependencies so that dbt transformations execute before data quality tests, with successful execution validated through Airflow.

## Final Outcome

The completed project includes:

- Seven source-specific staging models.
- A mart layer for consolidated data quality reporting.
- 58 dbt tests.
- Dockerized dbt execution.
- An Apache Airflow DAG orchestrating `dbt run` and `dbt test`.
- Successful end-to-end pipeline execution.

## Repository Structure

```text
flowpilot-data-pipeline/
├── airflow/
│   ├── dags/
│   ├── Dockerfile
│   └── compose.yaml
├── flowpilot/
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   └── dbt_project.yml
├── data/
├── Dockerfile
├── compose.yaml
└── Python ingestion and generation scripts
```

Generated datasets, credentials, local environments, and build artifacts are excluded from version control.
git init
git status --short
