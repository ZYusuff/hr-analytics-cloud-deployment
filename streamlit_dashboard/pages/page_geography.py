from pathlib import Path

import branca.colormap as colormap
import folium
import geopandas
import streamlit as st
from connect_data_warehouse import load_snowflake_to_duckdb
from streamlit_folium import st_folium

# -- constants


_PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_PATH = _PROJECT_ROOT / "assets"

GEOJSON_REGION_PATH = ASSETS_PATH / "swedish_regions.geojson"
GEOJSON_REGION_KEY = "ref:se:länskod"

GEOJSON_MUNICIPALITY_PATH = ASSETS_PATH / "swedish_municipalities.geojson"
GEOJSON_MUNICIPALITY_KEY = "lan_code"

MAP_LOCATION = [59.3293, 18.0686]  # Stockholm
MAP_BOUNDS = [[55.33, 10.93], [69.06, 24.17]]  # Sweden

MART_GEOGRAPHY = "mart_geography"
MART_URGENCY_GEOGRAPHY = "mart_urgency_geography"
LOCATION_KEY = "LOCATION_KEY"

LOCATION_LEVEL_REGION = "region"
LOCATION_LEVEL_MUNICIPALITY = "municipality"

_FILTER_STATE_KEY = "occupation_field_filter"
_OPTION_LABEL_ALL = "All"

# -- utils


@st.cache_data
def load_geopandas(path, **kwargs) -> geopandas.GeoDataFrame:
    return geopandas.read_file(path, **kwargs)


# -- setup page


st.set_page_config(page_title="Geographic Analysis", page_icon="🗺️", layout="wide")


# -- cache datasets


# create cached in-memroy duckdb
mart_tables = [MART_GEOGRAPHY, MART_URGENCY_GEOGRAPHY]
con = load_snowflake_to_duckdb(mart_tables)

# load geojson to cached geopandas
gdf_region = load_geopandas(GEOJSON_REGION_PATH, columns=[GEOJSON_REGION_KEY])
gdf_region = gdf_region.rename(columns={GEOJSON_REGION_KEY: LOCATION_KEY})

gdf_muni = load_geopandas(GEOJSON_MUNICIPALITY_PATH, columns=[GEOJSON_MUNICIPALITY_KEY])
gdf_muni = gdf_muni.rename(columns={GEOJSON_MUNICIPALITY_KEY: LOCATION_KEY})


# -- query datasets


selected_occupation_field = st.session_state.get(_FILTER_STATE_KEY, _OPTION_LABEL_ALL)
selected_location_level = LOCATION_LEVEL_REGION  # selectbox placeholder
selected_urgency_category = "urgent_7days"  # selecctbox placeholder

rel_map_data = con.sql(
    query=f"""
SELECT
    location_key as {LOCATION_KEY},
    location_display_name,

    SUM(total_vacancies) as total_vacancies,
    SUM(total_job_ads) as total_job_ads,

    $occupation_field AS occupation_field

FROM {MART_URGENCY_GEOGRAPHY}
WHERE
    (occupation_field = $occupation_field
        OR $occupation_field = $label_all)

    AND (location_level = $location_level
        OR $location_level = $label_all)

    AND (urgency_category = $urgency_category
        OR $urgency_category = $label_all)

GROUP BY 1, 2
ORDER BY total_vacancies DESC;
""",
    params={
        "occupation_field": selected_occupation_field,
        "location_level": selected_location_level,
        "urgency_category": selected_urgency_category,
        "label_all": _OPTION_LABEL_ALL,
    },
)


# -- create geopandas DF for map


df_map_data = rel_map_data.df()

gdf_base = gdf_region if selected_location_level == LOCATION_LEVEL_REGION else gdf_muni

gdf_map = gdf_base.merge(df_map_data, on=LOCATION_KEY, how="left")


# -- create folium map


# create colormap
min_val = gdf_map["total_vacancies"].fillna(0).min()
max_val = gdf_map["total_vacancies"].fillna(0).max()

colormap = colormap.LinearColormap(
    vmin=min_val,
    vmax=max_val,
    colors={"white", "yellow", "red"},
).to_step(n=8, method="log")

# create folium map objects
m = folium.Map(location=MAP_LOCATION)
m.fit_bounds(MAP_BOUNDS)
m.options["maxBounds"] = MAP_BOUNDS

g = folium.GeoJson(
    gdf_map,
    style_function=lambda x: {
        "fillColor": colormap(x["properties"]["total_vacancies"])
        if x["properties"]["total_vacancies"] is not None
        else "transparent",
        "color": "black",
        "fillOpacity": 0.5,
        "stroke": True,
        "weight": 0.1,
    },
).add_to(m)

st_data = st_folium(m, width=725)
