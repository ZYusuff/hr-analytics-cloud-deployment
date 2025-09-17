from pathlib import Path

import geopandas
import streamlit as st
from connect_data_warehouse import load_snowflake_to_duckdb


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

rel_geo = con.table(MART_GEOGRAPHY)
rel_urgency = con.table(MART_URGENCY_GEOGRAPHY)

# load geojson to cached geopandas
gdf_region = load_geopandas(GEOJSON_REGION_PATH, columns=[GEOJSON_REGION_KEY])
gdf_region = gdf_region.rename(columns={GEOJSON_REGION_KEY: LOCATION_KEY})

gdf_muni = load_geopandas(GEOJSON_MUNICIPALITY_PATH, columns=[GEOJSON_MUNICIPALITY_KEY])
gdf_muni = gdf_muni.rename(columns={GEOJSON_MUNICIPALITY_KEY: LOCATION_KEY})


# -- query datasets


# ...
