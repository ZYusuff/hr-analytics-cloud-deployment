import os
from pathlib import Path
from pprint import pprint

import dlt
import duckdb
from sources.jobsearch_source import jobsearch_source


def main():
    os.chdir(Path(__file__).parent)

    db = duckdb.connect(":memory:")
    p = dlt.pipeline(
        pipeline_name="jobsearch",
        destination=dlt.destinations.duckdb(db),
        dataset_name="jobads",
        # dev_mode=True,
    )

    dlt_loadinfo = p.run(jobsearch_source())

    print(dlt_loadinfo)

    print("\n", "Loaded Occupational Fields:")
    pprint(
        db.sql(
            """
        select distinct occupation_field__label, occupation_field__concept_id from jobads;
        """
        ).fetchall()
    )


if __name__ == "__main__":
    main()
