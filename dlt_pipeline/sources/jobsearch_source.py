from dataclasses import field

import dlt
from dlt.sources.config import configspec
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import OffsetPaginator


@configspec
class JobsearchConfig:
    table_name: str = "job_ads"  # default
    query: str = ""
    occupation_fields: list[str] = field(default_factory=lambda: [""])
    limit: int = 100
    offset: int = 0
    max_offset: int = 1900  # jobsearch limitation


@dlt.source
def jobsearch_source(
    config: JobsearchConfig = dlt.config.value,
):
    client = RESTClient(
        base_url="https://jobsearch.api.jobtechdev.se/",
        paginator=OffsetPaginator(
            limit=config.limit,
            offset=config.offset,
            total_path="$.total.value",
            maximum_offset=config.max_offset,
        ),
    )

    @dlt.resource(
        name="job_ads_resource",
        table_name=config.table_name,
        write_disposition="merge",
        primary_key="id",
        merge_key="id",
        
    )
    def get_jobads():
        for occupation_field in config.occupation_fields:
            for page_obj in client.paginate(
                path="/search",
                params={"q": config.query, "occupation-field": occupation_field},
            ):
                response_json = page_obj.response.json()

                for job_ad in response_json.get("hits", []):
                    yield job_ad

    yield get_jobads()
