import streamlit as st
# from connect_data_warehouse import query_job_listings

# Set the title and a short description for this page in the Streamlit app.
st.title("🏢 Employer overview")

# Retrieve the selected occupation field from the session state.
# This value is set by a filter on another page (e.g., the main page).
selected_occupation_field = st.session_state.occupation_field_filter

# Display a confirmation message to the user showing which filter is currently active.
st.write(f"Analyzing data for occupation field: **{selected_occupation_field}**")