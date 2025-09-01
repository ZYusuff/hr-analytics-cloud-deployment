import os
from dataclasses import field
from pathlib import Path
from pprint import pprint

import dlt
import duckdb
from dlt.sources.config import configspec
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import OffsetPaginator


@configspec
class JobsearchConfig:
    query: str = ""
    occupation_fields: list[str] = field(default_factory=lambda: [""])
    limit: int = 100
    offset: int = 0
    max_offset: int = 1000


@dlt.source
def jobsearch_source(
    config: JobsearchConfig = dlt.config.value,
):
    client = RESTClient(
        base_url="https://jobsearch.api.jobtechdev.se/",
        paginator=OffsetPaginator(
            limit=config.limit,
            offset=config.offset,
            maximum_offset=config.max_offset,
        ),
    )

    @dlt.resource(
        name="jobads",
        write_disposition="append",
        primary_key="id",
    )
    def get_jobads():
        for occupation_field in config.occupation_fields:
            for page in client.paginate(
                path="/search",
                params={"q": config.query, "occupation-field": occupation_field},
            ):
                response_json = page.response.json()

                for jobad in response_json.get("hits", []):
                    yield jobad

    yield get_jobads()


if __name__ == "__main__":
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
