import json
from pathlib import Path

import folium
import geopandas
import streamlit as st
from branca.colormap import linear
import branca
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

rel_folium_data = con.sql(
    """
    select location_key, sum_total_vacancies
    from rel_field_region_total
"""
)

df_data = rel_folium_data.df()

gdf_region = geopandas.read_file(GEOJSON_REGION_PATH, columns=["ref:se:länskod"])
gdf_region = gdf_region.rename(columns={"ref:se:länskod": "LOCATION_KEY"})

gdf_merge = gdf_region.merge(df_data, how="left", left_on="LOCATION_KEY", right_on="LOCATION_KEY")


colormap = branca.colormap.LinearColormap(
    vmin=gdf_merge["sum_total_vacancies"].quantile(0.0),
    vmax=gdf_merge["sum_total_vacancies"].quantile(1),
    colors=["yellow", "green"],
)

m = folium.Map(location=MAP_LOCATION)
m.fit_bounds(MAP_BOUNDS)
m.options["maxBounds"] = MAP_BOUNDS


tooltip = folium.GeoJsonTooltip(
    fields=["sum_total_vacancies"],
    aliases=["Vacancies:"],
    localize=True,
    sticky=False,
    labels=True,
    style="""
        background-color: #F0EFEF;
        border: 0px solid black;
        border-radius: 5px;
        box-shadow: 3px;
    """,
    max_width=800,
)

popup = folium.GeoJsonPopup(
    fields=["LOCATION_KEY"],
    aliases=["% Change"],
    localize=True,
    labels=True,
    style="background-color: yellow;",
)

g = folium.GeoJson(
    gdf_merge,
    style_function=lambda x: {
        "fillColor": colormap(x["properties"]["sum_total_vacancies"]),
        "color": "black",
        "fillOpacity": 0.4,
        "stroke": True,
        "weight": 0.1,
    },
    tooltip=tooltip,
    popup=popup
).add_to(m)

st_data = st_folium(m, width=725)
