from pathlib import Path
import duckdb

# data warehouse directory
FILE_SHARE_PATH = Path("/mnt/data/job_ads.duckdb")
 

def query_job_listings(query='SELECT * FROM marts.mart_technical_jobs'):
    with duckdb.connect(db_path, read_only=True) as conn:
        return conn.query(f"{query}").df()