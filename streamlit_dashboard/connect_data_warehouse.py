import os

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv


def query_job_listings(mart_table: str) -> pd.DataFrame:
    """Queries a job listings table and returns the data as a pandas DataFrame."""

    load_dotenv()

    print("Initializing connection to Snowflake...")

    with snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE"),
    ) as conn:
        query = f"SELECT * FROM {mart_table}"

        print(f"Executing query and fetching data for '{mart_table}'...")

        df = pd.read_sql(query, conn)

        print(f"Successfully fetched {len(df)} rows into a Pandas DataFrame.")

        return df