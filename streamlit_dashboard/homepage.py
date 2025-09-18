import streamlit as st

st.set_page_config(page_title="Dashboard Home", page_icon="🏠")

st.title("🏠 Welcome to the Dashboard")
st.write("Välkommen! Här kan du välja vilken analys du vill se.")
st.info("Yrkesområdet är förinställt till **Hälso- och sjukvård**.")

# Sätt yrkesområdet direkt som en variabel i session_state
st.session_state.occupation_field_filter = "Hälso- och sjukvård"

# Välj vilken sida du vill gå till
page_options = {
    "📈 Demand Overview": "page_demand",
    "🌍 Geography": "page_geography",
    "⏳ Application Urgency": "page_urgency",
    "🔍 Job Browser": "page_browser"
}

selected_page = st.selectbox("Välj analyssida:", list(page_options.keys()))

# Navigeringsknapp
if st.button("Gå till vald sida"):
    st.switch_page(page_options[selected_page])