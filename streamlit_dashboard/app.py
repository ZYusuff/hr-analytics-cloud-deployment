import streamlit as st

st.set_page_config(page_title="Main Dashboard", page_icon="📊", layout="wide")

pages = {
    "Home": [st.Page("pages/homepage.py", title="Home", icon="🏠")],
    "Analysis": [
        st.Page("pages/page_demand.py", title="Demand Overview", icon="📈"),
        st.Page("pages/page_urgency.py", title="Application Urgency", icon="⏳"),
        st.Page("pages/page_geography.py", title="Geography", icon="🌍"),
        st.Page("pages/page_browser.py", title="Job Browser", icon="🔎"),
    ],
}

st.sidebar.selectbox(
    "Filter by **occupation field**",
    [
        "All",
        "Hälso- och sjukvård",
    ],
    key="occupation_field_filter",
)

pg = st.navigation(pages)

pg.run()
