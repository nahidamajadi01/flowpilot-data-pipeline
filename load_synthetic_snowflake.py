import csv
import gzip
import os
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent
load_dotenv(BASE / '.env', override=True)

SOURCES = {
    'ga4_events': 'GA4_EVENTS',
    'product_events': 'PRODUCT_EVENTS',
    'meta_ads_daily': 'META_ADS_DAILY',
    'subscriptions': 'SUBSCRIPTIONS',
}


def columns_from_file(path):
    with gzip.open(path, 'rt', newline='', encoding='utf-8') as file:
        columns = next(csv.reader(file))
    if not columns or any(not col.isidentifier() for col in columns):
        raise ValueError(f'Unexpected CSV header: {path.name}: {columns}')
    return columns


# Check all files BEFORE connecting to Snowflake (no compute credits).
files = {}
for source in SOURCES:
    path = BASE / f'{source}.csv.gz'
    if not path.is_file():
        raise FileNotFoundError(f'Missing {path}. Put the generated .csv.gz files next to this script.')
    files[source] = (path, columns_from_file(path))

if not os.getenv('SNOWFLAKE_TOKEN'):
    raise RuntimeError('SNOWFLAKE_TOKEN is missing from .env')

conn = snowflake.connector.connect(
    account='DISMCGZ-CH79851',
    user='TISHA9248@GMAIL.COM',
    authenticator='PROGRAMMATIC_ACCESS_TOKEN',
    token=os.environ['SNOWFLAKE_TOKEN'],
    role='FLOWPILOT_ROLE',
    warehouse='FLOWPILOT_WH',
    database='FLOWPILOT_DB',
    schema='RAW',
)

try:
    with conn.cursor() as cur:
        cur.execute('''
            CREATE STAGE IF NOT EXISTS SYNTHETIC_CSV_STAGE
            FILE_FORMAT = (
                TYPE = CSV
                COMPRESSION = AUTO
                SKIP_HEADER = 1
                FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                NULL_IF = ('')
                ERROR_ON_COLUMN_COUNT_MISMATCH = TRUE
            )
        ''')

        for source, table in SOURCES.items():
            path, columns = files[source]
            definitions = ', '.join(f'"{col.upper()}" VARCHAR' for col in columns)
            cur.execute(f'CREATE TABLE IF NOT EXISTS {table} ({definitions})')

            # Stage uploads are not warehouse-compute operations.
            cur.execute(
                f"PUT 'file://{path.as_posix()}' "
                f'@SYNTHETIC_CSV_STAGE/{source}/ AUTO_COMPRESS=FALSE OVERWRITE=FALSE'
            )

            # COPY tracks loaded files; repeat runs skip previously loaded files.
            cur.execute(
                f'COPY INTO {table} '
                f'FROM @SYNTHETIC_CSV_STAGE/{source}/ '
                f"FILES = ('{path.name}') "
                f'ON_ERROR = ABORT_STATEMENT'
            )
            results = cur.fetchall()
            for row in results:
                print(f'{table}: COPY status={row[1]}, rows_loaded={row[3]:,}')

            cur.execute(f'SELECT COUNT(*) FROM {table}')
            print(f'{table}: total rows in Snowflake={cur.fetchone()[0]:,}')
finally:
    conn.close()
