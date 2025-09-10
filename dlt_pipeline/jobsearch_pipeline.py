import os
from pathlib import Path

import dlt
from sources.jobsearch_source import jobsearch_source

_SCHEMA = "staging"


def main():
    os.chdir(Path(__file__).parent)

    p = dlt.pipeline(
        pipeline_name="jobsearch",
        destination="snowflake",
        dataset_name=_SCHEMA,
    )

    dlt_loadinfo = p.run(jobsearch_source())

    print(dlt_loadinfo)


if __name__ == "__main__":
    main()
