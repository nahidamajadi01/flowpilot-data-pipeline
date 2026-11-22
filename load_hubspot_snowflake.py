
import os
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv

load_dotenv(override=True)

DATA_DIR = Path(__file__).resolve().parent / "data" / "raw"

SOURCES = {
    "companies": "HUBSPOT_COMPANIES",
    "contacts": "HUBSPOT_CONTACTS",
    "deals": "HUBSPOT_DEALS",
}

conn = snowflake.connector.connect(
    account="DISMCGZ-CH79851",
    user="TISHA9248@GMAIL.COM",
    authenticator="PROGRAMMATIC_ACCESS_TOKEN",
    token=os.getenv("SNOWFLAKE_TOKEN"),
    role="FLOWPILOT_ROLE",
    warehouse="FLOWPILOT_WH",
    database="FLOWPILOT_DB",
    schema="RAW",
)

try:
    with conn.cursor() as cur:
        # Reusable JSON file format
        cur.execute("""
            CREATE FILE FORMAT IF NOT EXISTS HUBSPOT_JSON_FORMAT
            TYPE = JSON
            STRIP_OUTER_ARRAY = TRUE
        """)

        # Internal stage for HubSpot files
        cur.execute("""
            CREATE STAGE IF NOT EXISTS HUBSPOT_STAGE
            FILE_FORMAT = HUBSPOT_JSON_FORMAT
        """)

        for source, table in SOURCES.items():
            file_path = DATA_DIR / f"{source}.json"

            if not file_path.is_file():
                raise FileNotFoundError(file_path)

            # Create the RAW table automatically
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    DATA VARIANT
                )
            """)

            # Upload local JSON to Snowflake's internal stage
            cur.execute(
                f"PUT 'file://{file_path.as_posix()}' "
                f"@HUBSPOT_STAGE/{source}/ "
                "AUTO_COMPRESS=TRUE OVERWRITE=TRUE"
            )

            # Replace this source's RAW snapshot on each run
            cur.execute("BEGIN")

            try:
                cur.execute(f"DELETE FROM {table}")

                cur.execute(f"""
                    COPY INTO {table} (DATA)
                    FROM (
                        SELECT $1
                        FROM @HUBSPOT_STAGE/{source}/
                    )
                    FILE_FORMAT = (
                        FORMAT_NAME = HUBSPOT_JSON_FORMAT
                    )
                    FORCE = TRUE
                """)

                copy_results = cur.fetchall()
                loaded = sum(
                    int(row[3]) for row in copy_results
                )

                cur.execute("COMMIT")
                print(f"{table}: {loaded} rows loaded")

            except Exception:
                cur.execute("ROLLBACK")
                raise

finally:
    conn.close()
