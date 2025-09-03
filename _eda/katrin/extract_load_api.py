import requests
import json
import dlt
from pathlib import Path
import os


def _get_ads(url_for_search, params):
    headers = {'accept': 'application/json'}
    response = requests.get(url_for_search, headers=headers, params=params)
    response.raise_for_status()  # check for http errors
    return json.loads(response.content.decode('utf8'))

@dlt.resource(
    write_disposition="replace",
    # columns={
    #     'original_id': {'data_type': 'text'},
    #     'description__company_information': {'data_type': 'text'},
    #     'description__needs': {'data_type': 'text'},
    #     'description__requirements': {'data_type': 'text'},
    #     'employer__email': {'data_type': 'text'},
    #     'driving_license': {'data_type': 'json'},
    #     'removed_date': {'data_type': 'timestamp'}
    # }
)
def jobsearch_resource(params):
    """
    params should include at least:
      - "q": your query
      - "limit": page size (e.g. 100)
    """
    url = 'https://jobsearch.api.jobtechdev.se'
    url_for_search = f"{url}/search"

    limit = params.get('limit', 100)
    offset = 0

    while True:
        # build this page’s params
        page_params = dict(params, offset=offset)
        data = _get_ads(url_for_search, page_params)

        hits = data.get('hits', [])
        if not hits:
            # no more results
            break

        # yield each ad on this page
        for ad in hits:
            yield ad

        # if fewer than a full page was returned, we’re done
        if (len(hits) < limit) or (offset > 1900):
            break

        offset += limit

def run_pipeline(query, table_name, occupation_fields):
    pipeline = dlt.pipeline(
        pipeline_name="job_ads_project",
        destination=dlt.destinations.duckdb("ads_data_warehouse.duckdb"),
        dataset_name="staging",
    )

    for occupation_field in occupation_fields:
        params = {"q":query, "limit":100, "occupation-field": occupation_field}
        load_info = pipeline.run(
            jobsearch_resource(params=params), 
            table_name=table_name
            )
        
        print("\n" + "="*50)
        print(f"{occupation_field = }")
        print(f"Pipeline finished with status: {load_info}")



if __name__ == '__main__':
    working_directory = Path(__file__).parent
    os.chdir(working_directory)

    query = ""
    table_name = "job_ads"

    # "Försäljning", "Hälso sjukvård", "Hotell"
    occupation_fields = ("RPTn_bxG_ExZ", "NYW6_mP6_vwf", "ScKy_FHB_7wT")

    run_pipeline(query, table_name, occupation_fields)
