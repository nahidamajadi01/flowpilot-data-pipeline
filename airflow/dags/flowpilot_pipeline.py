from datetime import datetime
import os

from airflow.sdk import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount


PROJECT_DIR = os.environ["FLOWPILOT_PROJECT_DIR"]
DBT_PROFILE_DIR = os.environ["DBT_PROFILE_DIR"]

docker_mounts = [
    Mount(
        source=PROJECT_DIR,
        target="/workspace/flowpilot",
        type="bind",
    ),
    Mount(
        source=DBT_PROFILE_DIR,
        target="/root/.dbt",
        type="bind",
        read_only=True,
    ),
]

with DAG(
    dag_id="flowpilot_dbt_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["flowpilot", "dbt"],
) as dag:

    dbt_run = DockerOperator(
        task_id="dbt_run",
        image="flowpilot-data-pipeline-dbt:latest",
        command="run",
        docker_url="unix:///var/run/docker.sock",
        docker_conn_id=None,
        mount_tmp_dir=False,
        mounts=docker_mounts,
        working_dir="/workspace/flowpilot",
        environment={
            "DBT_PROFILES_DIR": "/root/.dbt",
            "SNOWFLAKE_TOKEN": os.environ.get("SNOWFLAKE_TOKEN", ""),
        },
        auto_remove="success",
    )

    dbt_test = DockerOperator(
        task_id="dbt_test",
        image="flowpilot-data-pipeline-dbt:latest",
        command="test",
        docker_url="unix:///var/run/docker.sock",
        docker_conn_id=None,
        mount_tmp_dir=False,
        mounts=docker_mounts,
        working_dir="/workspace/flowpilot",
        environment={
            "DBT_PROFILES_DIR": "/root/.dbt",
            "SNOWFLAKE_TOKEN": os.environ.get("SNOWFLAKE_TOKEN", ""),
        },
        auto_remove="success",
    )

    dbt_run >> dbt_test
