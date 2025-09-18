import os

import duckdb
import snowflake.connector
import streamlit as st
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


@st.cache_data
def get_job_listings(mart_table: str) -> DataFrame:
    return query_job_listings(mart_table)


def load_snowflake_to_duckdb(
    mart_tables: list[str],
    ddb_table_name_prefix: str | None = None,
    schema: str | None = None,
) -> duckdb.DuckDBPyConnection:
    """
    Loads specified Snowflake tables into a cached, in-memory DuckDB instance.
    Args:
        mart_tables: A list of table names to load from Snowflake.
        ddb_table_name_prefix: Optional prefix to add to table names in DuckDB.
        schema: Optional schema to connect to in Snowflake. If not provided,
                it defaults to the SNOWFLAKE_SCHEMA environment variable.
    Returns:
        A single DuckDB connection with all specified tables registered and ready to query.
    """
    load_dotenv()
    print("Initializing DB: Connecting to Snowflake and loading tables...")
    duck_conn = duckdb.connect(database=":memory:", read_only=False)
    # Determine which schema to use: the argument if provided, otherwise the env var.
    snowflake_schema = schema or os.getenv("SNOWFLAKE_SCHEMA")
    try:
        with snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=snowflake_schema,
            role=os.getenv("SNOWFLAKE_ROLE"),
        ) as conn:
            cursor = conn.cursor()
            print(f"Connected to Snowflake schema: '{snowflake_schema}'")
            for mart_table in mart_tables:
                # Determine the name for the table in DuckDB
                duckdb_table_name = f"{ddb_table_name_prefix}{mart_table}" if ddb_table_name_prefix else mart_table
                # Fetch from Snowflake as a PyArrow table
                tbl_arrow = cursor.execute(f"SELECT * FROM {mart_table}").fetch_arrow_all()
                # Register in DuckDB (zero-copy)
                duck_conn.register(duckdb_table_name, tbl_arrow)
                # A single, concise log line per table
                print(f"  > Loaded '{mart_table}' as '{duckdb_table_name}' ({tbl_arrow.num_rows:,} rows)")
    except Exception as e:
        print(f"An error occurred: {e}")
        # Close the connection and re-raise to ensure the caller knows it failed
        duck_conn.close()
        raise
    print("DB initialization complete.")
    return duck_conn


@st.cache_resource
def get_db_connection(mart_tables: list[str]):
    return load_snowflake_to_duckdb(mart_tables)
