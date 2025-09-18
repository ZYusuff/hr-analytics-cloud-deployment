import streamlit as st

_OPTION_LABEL_ALL = "All"  # for use with widgets

st.set_page_config(page_title="Jobsearch Dashboard", page_icon="📊", layout="wide")

pages = {
    "Home": [st.Page("pages/homepage.py", title="Home", icon="🏠")],
    "Analysis": [
        st.Page("pages/page_demand.py", title="Demand Overview", icon="📈"),
        st.Page("pages/page_employer.py", title="Employer Overview", icon="🏢"),
        st.Page("pages/page_urgency.py", title="Application Urgency", icon="⏳"),
        st.Page("pages/page_geography.py", title="Geography", icon="🌍"),
        st.Page("pages/page_browser.py", title="Job Browser", icon="🔎"),
    ],
}

st.sidebar.selectbox(
    "Filter by **occupation field**",
    [
        _OPTION_LABEL_ALL,
        "Hälso- och sjukvård",
    ],
    key="occupation_field_filter",
)

pg = st.navigation(pages)

pg.run()
