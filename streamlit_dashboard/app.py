import streamlit as st
from connect_data_warehouse import get_db_connection

MART_FOR_OCCUPATION_FIELDS = "mart_occupation_demand"
_OPTION_LABEL_ALL = "All"  # for use with widgets

# -- setup streamlit pages

st.set_page_config(page_title="Jobsearch Dashboard", page_icon="📊", layout="wide")

pages = {
    "": [st.Page("pages/homepage.py", title="Home", icon="🏠")],
    "Analysis": [
        st.Page("pages/page_demand.py", title="Demand Overview", icon="📈"),
        st.Page("pages/page_employer.py", title="Employer Overview", icon="🏢"),
        st.Page("pages/page_urgency.py", title="Application Urgency", icon="⏳"),
        st.Page("pages/page_geography.py", title="Urgency by region", icon="🌍"),
        st.Page("pages/page_browser.py", title="Job Browser", icon="🔎"),
    ],
}

# -- get available occupation fields for widget

con = get_db_connection([MART_FOR_OCCUPATION_FIELDS])

rel_occupation_fields = con.sql(
    query=f"""
SELECT occupation_field
FROM {MART_FOR_OCCUPATION_FIELDS}
GROUP BY 1
ORDER BY 1 DESC;
"""
)

available_occupation_fields = [item for (item,) in rel_occupation_fields.fetchall()]

# -- sidebar selectbox filter

st.sidebar.selectbox(
    "Filter by **occupation field**",
    [
        _OPTION_LABEL_ALL,
        *available_occupation_fields,
    ],
    key="occupation_field_filter",
)

# -- run!

pg = st.navigation(pages)
pg.run()
