import json
from pathlib import Path

import folium
import plotly.express as px
import streamlit as st
from connect_data_warehouse import create_job_listings_db
from streamlit_folium import st_folium

PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_PATH = PROJECT_ROOT / "assets"

GEOJSON_REGION_PATH = ASSETS_PATH / "swedish_regions.geojson"
GEOJSON_MUNICIPALITY_PATH = ASSETS_PATH / "swedish_municipalities.geojson"

MAP_LOCATION = [59.3293, 18.0686]  # Stockholm
MAP_BOUNDS = [[55.33, 10.93], [69.06, 24.17]]  # Sweden


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

# -- folium

m = folium.Map(location=MAP_LOCATION)

folium.Choropleth(
    geo_data=geojson_region,
    data=rel_field_region_total.df(),
    columns=["LOCATION_KEY", "sum_total_vacancies"],
    key_on="feature.properties.ref:se:länskod",
).add_to(m)

m.fit_bounds(MAP_BOUNDS)
m.options["maxBounds"] = MAP_BOUNDS

# call to render Folium map in Streamlit
st_data = st_folium(m, width=725)
