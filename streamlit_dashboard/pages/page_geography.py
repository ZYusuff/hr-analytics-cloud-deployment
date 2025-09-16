import json
from pathlib import Path

import plotly.express as px
import streamlit as st
from connect_data_warehouse import create_job_listings_db

PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_PATH = PROJECT_ROOT / "assets"

GEOJSON_REGION_PATH = ASSETS_PATH / "swedish_regions.geojson"
GEOJSON_MUNICIPALITY_PATH = ASSETS_PATH / "swedish_municipalities.geojson"


@st.cache_data
def load_geojson(path):
    with open(path, "r") as f:
        return json.load(f)


# page setup
st.set_page_config(
    page_title="Geographic Analysis",
    page_icon="🗺️",
    layout="wide",
)

# load cached geojson
geojson_region = load_geojson(GEOJSON_REGION_PATH)
geojson_municipality = load_geojson(GEOJSON_MUNICIPALITY_PATH)

# create cached in-memroy duckdb
con = create_job_listings_db("mart_geography", duckdb_table_name="mart_geography")

# filter mart by OCCUPATION_FIELD
selected_occupation_field = st.session_state.occupation_field_filter

if selected_occupation_field == "All":
    rel_base = con.sql("select * from mart_geography")
else:
    rel_base = con.sql(
        "select * from mart_geography where OCCUPATION_FIELD = ?",
        params=[selected_occupation_field],
    )

# -- create datasets

rel_field_region_total = con.sql(
    """
    select
        location_key,
        location_display_name,
        occupation_display_name,
        sum(total_vacancies) as sum_total_vacancies
    from rel_base
    where
        location_level = 'region'
        and occupation_level = 'field'
    group by 1, 2, 3
    order by sum_total_vacancies desc
"""
)

rel_field_municipality_total = con.sql(
    """
    select
        location_key,
        location_display_name,
        occupation_display_name,
        sum(total_vacancies) as sum_total_vacancies
    from rel_base
    where
        location_level = 'municipality'
        and occupation_level = 'field'
    group by 1, 2, 3
    order by sum_total_vacancies desc
"""
)

# -- plotly

fig = px.choropleth_map(
    data_frame=rel_field_region_total.df(),
    geojson=geojson_region,
    locations="LOCATION_KEY",
    featureidkey="properties.ref:se:länskod",
    color="sum_total_vacancies",
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

st.dataframe(rel_field_region_total.df())

st.dataframe(rel_field_municipality_total.df())
