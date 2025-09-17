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
GEOJSON_MUNICIPALITY_KEY = "id"

MAP_LOCATION = [59.3293, 18.0686]  # Stockholm
MAP_BOUNDS = [[55.33, 10.93], [69.06, 24.17]]  # Sweden

MART_GEOGRAPHY = "mart_geography"
MART_URGENCY_GEOGRAPHY = "mart_urgency_geography"

LOCATION_KEY = "LOCATION_KEY"

LOCATION_LEVEL_REGION = "region"
LOCATION_LEVEL_MUNICIPALITY = "municipality"

LOCATION_LEVEL_SELECTBOX_CONFIG = {
    LOCATION_LEVEL_REGION: "Region",
    LOCATION_LEVEL_MUNICIPALITY: "Municipality",
}

URGENCY_CATGEGORIES_SELECTBOX_CONFIG = {
    "urgent_7days": "7 days",
    "closing_14days": "14 days",
    "closing_30days": "30 days",
    "normal": "Normal",
}

_FILTER_OCCUPATION_FIELD_KEY = "occupation_field_filter"
_OPTION_LABEL_ALL = "All"

# -- utils


@st.cache_resource
def get_db_connection():
    mart_tables = [MART_URGENCY_GEOGRAPHY]
    return load_snowflake_to_duckdb(mart_tables)


@st.cache_data
def load_geopandas(path, key_column) -> geopandas.GeoDataFrame:
    gdf = geopandas.read_file(path)
    return gdf[[key_column, "geometry"]].rename(columns={key_column: LOCATION_KEY})


# -- setup page


st.set_page_config(page_title="Geographic Analysis", page_icon="🗺️", layout="wide")


# -- cache datasets


# create cached in-memroy duckdb
con = get_db_connection()

# load geojson to cached geopandas
gdf_region = load_geopandas(GEOJSON_REGION_PATH, GEOJSON_REGION_KEY)
gdf_muni = load_geopandas(GEOJSON_MUNICIPALITY_PATH, GEOJSON_MUNICIPALITY_KEY)


# -- query datasets

# global sidebar selectbox widget value
selected_occupation_field = st.session_state.get(_FILTER_OCCUPATION_FIELD_KEY, _OPTION_LABEL_ALL)

# local sidebar selectbox widgets
selected_location_level = st.sidebar.selectbox(
    label="Filter by location level",
    options=list(LOCATION_LEVEL_SELECTBOX_CONFIG.keys()),
    format_func=lambda key: LOCATION_LEVEL_SELECTBOX_CONFIG[key],
)

selected_urgency_category = st.sidebar.selectbox(
    label="Filter by urgency",
    options=list(URGENCY_CATGEGORIES_SELECTBOX_CONFIG.keys()),
    format_func=lambda key: URGENCY_CATGEGORIES_SELECTBOX_CONFIG[key],
)


rel_map_data = con.sql(
    query=f"""
SELECT
    location_key as {LOCATION_KEY},
    ANY_VALUE(location_display_name) as location_display_name,
    SUM(total_vacancies) as total_vacancies,
    SUM(total_job_ads) as total_job_ads,

FROM {MART_URGENCY_GEOGRAPHY}
WHERE
    (occupation_field = $occupation_field
        OR $occupation_field = $label_all)

    AND (location_level = $location_level
        OR $location_level = $label_all)

    AND (urgency_category = $urgency_category
        OR $urgency_category = $label_all)

GROUP BY location_key
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
cmap_fill = colormap.LinearColormap(
    vmin=0,
    vmax=gdf_map["total_vacancies"].fillna(0).max(),
    colors=["#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"],
).to_step(n=15, method="log")

# create folium map objects
m = folium.Map(location=MAP_LOCATION)
m.fit_bounds(MAP_BOUNDS)
m.options["maxBounds"] = MAP_BOUNDS

tooltip = folium.GeoJsonTooltip(
    fields=["location_display_name", "total_vacancies"],
    aliases=["_Region_", "Vacancies:"],
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
    fields=["location_display_name", "total_job_ads"],
    aliases=["_Region_", "total job ads: "],
    localize=True,
    labels=True,
    style="background-color: yellow;",
)

g = folium.GeoJson(
    gdf_map,
    style_function=lambda x: {
        "fillColor": cmap_fill(x["properties"]["total_vacancies"])
        if x["properties"]["total_vacancies"] is not None
        else "transparent",
        "color": "black",
        "fillOpacity": 0.5,
        "stroke": True,
        "weight": 0.1,
    },
    tooltip=tooltip,
    popup=popup,
).add_to(m)

cmap_fill.add_to(m)

st_folium(m, use_container_width=True)
