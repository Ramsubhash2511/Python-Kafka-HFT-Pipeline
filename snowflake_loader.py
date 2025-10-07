import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

# --- Snowflake Configuration (read from environment only) ---
# Ensure you have a .env or environment set with the following keys
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_ROLE = os.getenv('SNOWFLAKE_ROLE')
SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE')
SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE')
SNOWFLAKE_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA')
SNOWFLAKE_TABLE = os.getenv('SNOWFLAKE_TABLE')

# --- File to Load (must be set in env or .env) ---
CSV_FILE_PATH = os.getenv('CSV_FILE_PATH')

# Validate required environment variables early and fail fast
required = {
    'SNOWFLAKE_USER': SNOWFLAKE_USER,
    'SNOWFLAKE_PASSWORD': SNOWFLAKE_PASSWORD,
    'SNOWFLAKE_ACCOUNT': SNOWFLAKE_ACCOUNT,
    'SNOWFLAKE_ROLE': SNOWFLAKE_ROLE,
    'SNOWFLAKE_WAREHOUSE': SNOWFLAKE_WAREHOUSE,
    'SNOWFLAKE_DATABASE': SNOWFLAKE_DATABASE,
    'SNOWFLAKE_SCHEMA': SNOWFLAKE_SCHEMA,
    'SNOWFLAKE_TABLE': SNOWFLAKE_TABLE,
    'CSV_FILE_PATH': CSV_FILE_PATH,
}
missing = [k for k, v in required.items() if not v]
if missing:
    raise RuntimeError(
        f"Missing required environment variables: {', '.join(missing)}")

try:
    print("Connecting to Snowflake...")
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )
    print("Successfully connected to Snowflake.")

    # --- Data Preparation ---
    print(f"Reading data from {CSV_FILE_PATH}...")
    df = pd.read_csv(CSV_FILE_PATH)

    # Rename columns to match the Snowflake table exactly (UPPERCASE)
    df.rename(columns={
        'datetime': 'TIMESTAMP',
        'open': 'OPEN',
        'high': 'HIGH',
        'low': 'LOW',
        'close': 'CLOSE',
        'volume': 'VOLUME'
    }, inplace=True)

    df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
    print(f"Prepared {len(df)} rows for upload.")

    # --- Upload to Snowflake ---
    print(f"Uploading data to {SNOWFLAKE_TABLE}...")
    success, nchunks, nrows, _ = write_pandas(
        conn=conn,
        df=df[['TIMESTAMP', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']],
        table_name=SNOWFLAKE_TABLE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
        auto_create_table=False,  # Table should already exist
        overwrite=True, 
        use_logical_type=True  # Use logical types for better type mapping
    )
    print(f"Upload complete. Success: {success}, Rows uploaded: {nrows}")

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
        print("Snowflake connection closed.")
