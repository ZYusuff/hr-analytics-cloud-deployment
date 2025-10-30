from pathlib import Path
import duckdb

# data warehouse directory
db_path = Path("/mnt/data/job_ads.duckdb")
 

def get_job_listings(query='SELECT * FROM marts.mart_technical_jobs'):
    with duckdb.connect(db_path, read_only=True) as conn:
        return conn.query(f"{query}").df()