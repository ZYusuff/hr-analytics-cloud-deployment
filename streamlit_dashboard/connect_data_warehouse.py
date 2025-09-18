import os
import duckdb
import snowflake.connector
from dotenv import load_dotenv
from pandas import DataFrame


def query_job_listings(mart_table: str) -> DataFrame:
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

        cursor = conn.cursor()
        cursor.execute(query)
        df = cursor.fetch_pandas_all()

        print(f"Successfully fetched {len(df)} rows into a Pandas DataFrame.")

        return df


def create_job_listings_db(
    mart_table: str,
    duckdb_table_name: str = "job_listings",
) -> duckdb.DuckDBPyConnection:
    """Loads a job listings table into an in-memory DuckDB and returns the connection."""

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

        print(f"Executing query and fetching data for '{mart_table}' as a PyArrow Table...")

        cursor = conn.cursor()
        cursor.execute(query)
        tbl_mart = cursor.fetch_arrow_all()

        print(f"Successfully fetched {tbl_mart.num_rows} rows from Snowflake into a PyArrow Table.")

    print("Loading data into in-memory DuckDB...")

    duck_conn = duckdb.connect(database=":memory:", read_only=False)
    duck_conn.register(duckdb_table_name, tbl_mart)  # zero-copy

    print(f"Successfully registered {tbl_mart.num_rows} rows into DuckDB as table '{duckdb_table_name}'.")

    return duck_conn

if __name__ == "__main__":
    df = query_job_listings("marts.job_listings")
    print(df.head())  # Visa de första raderna