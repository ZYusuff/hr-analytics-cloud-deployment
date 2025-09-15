import streamlit as st

# Import subpages
import pages.homepage as homepage
import pages.page_demand as page_demand
import pages.page_urgency as page_urgency 
import pages.page_geography as page_geography  
import pages.page_browser as page_browser


# Sidebar navigation
st.sidebar.title("📊 Dashboard Navigation")
page = st.sidebar.radio("Go to", [
    "Home",
    "Demand Overview",  
    "Application Urgency",
    "Geography",
    "Job Browser"
])

# Routing logic
if page == "Home":
    homepage.show()
elif page == "Demand Overview":
    page_demand.show()
elif page == "Application Urgency":
    page_urgency.show()
elif page == "Geography":
    page_geography.show()
elif page == "Job Browser":
    page_browser.show()
