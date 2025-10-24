import streamlit as st
import duckdb
import os
from pathlib import Path

# =======================
#   Database setup
# =======================

DB_PATH = os.getenv("DUCKDB_PATH", str(Path(__file__).parents[1] / "data_warehouse/job_ads.duckdb"))

# =======================
#   Streamlit setup
# =======================

MART_FOR_OCCUPATION_FIELDS = "marts.mart_occupation_demand"
_OPTION_LABEL_ALL = "All"  # for use with widgets



st.set_page_config(page_title="Job Market Analytics Dashboard", page_icon="📊", layout="wide")

pages = {
    "": [st.Page("pages/homepage.py", title="Home", icon="🏠")],
    "Analysis": [
        st.Page("pages/page_demand.py", title="Demand Overview", icon="📈"),
        st.Page("pages/page_employer.py", title="Employer Overview", icon="🏢"),
        st.Page("pages/page_urgency.py", title="Application Urgency", icon="⏳"),
        st.Page("pages/page_geography.py", title="Urgency by Region", icon="🌍"),
        st.Page("pages/page_browser.py", title="Job Browser", icon="🔎"),
    ],
}

# =======================
#   Load data
# =======================

@st.cache_data
def load_occupation_fields():
    """Fetch available occupation fields from DuckDB."""
    query = f"""
        SELECT occupation_field
        FROM {MART_FOR_OCCUPATION_FIELDS}
        GROUP BY 1
        ORDER BY 1 DESC;
    """
    with duckdb.connect(DB_PATH, read_only=True) as conn:
        results = conn.execute(query).fetchall()
    return [item for (item,) in results]

available_occupation_fields = load_occupation_fields()

# =======================
#   Sidebar filter
# =======================

st.sidebar.selectbox(
    "Filter by **Occupation field**",
    [
        _OPTION_LABEL_ALL,
        *available_occupation_fields,
    ],
    key="occupation_field_filter",
)

# =======================
#   Run navigation
# =======================

pg = st.navigation(pages)
pg.run()
