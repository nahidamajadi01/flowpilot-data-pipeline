import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)
token = os.getenv("SNOWFLAKE_TOKEN", "").strip()
print("token length:", len(token), "ends:", token[-4:])

conn = snowflake.connector.connect(
    account="DISMCGZ-CH79851",
    user="TISHA9248@GMAIL.COM",
    authenticator="PROGRAMMATIC_ACCESS_TOKEN",
    token=token,
    role="FLOWPILOT_ROLE",
    warehouse="FLOWPILOT_WH",
    database="FLOWPILOT_DB",
    schema="RAW",
)

try:
    cursor = conn.cursor()
    cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE()")
    print("Connected to Snowflake!")
    print(cursor.fetchone())
finally:
    conn.close()