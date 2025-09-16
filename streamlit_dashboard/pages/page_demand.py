import streamlit as st
from connect_data_warehouse import query_job_listings

# Set the title and a short description for this page in the Streamlit app.
st.title("📈 Demand overview")
st.write("This is where you can show which specific occupation groups and specific occupations are in demand.")


# Retrieve the selected occupation field from the session state.
# This value is set by a filter on another page (e.g., the main page).
selected_occupation_field = st.session_state.occupation_field_filter

# Display a confirmation message to the user showing which filter is currently active.
st.write(f"Analyzing data for region: **{selected_occupation_field}**")

# Query the data warehouse to get the 'mart_urgency' data mart.
# This DataFrame contains all the data needed for our urgency analysis.
df = query_job_listings("mart_job_browser")

# Add a subheader for the raw data table.
st.markdown("## Raw data for selected occupation field: " + selected_occupation_field)

# Filter the DataFrame based on the user's selection.
if selected_occupation_field != "All":
    # If a specific field is chosen, filter the DataFrame to only show rows matching it.
    display_df = df[df["OCCUPATION_FIELD"] == selected_occupation_field]
else:
    # If "All" is selected, use the entire, unfiltered DataFrame.
    display_df = df

# Display the resulting DataFrame (either filtered or full) in an interactive table on the page.
st.dataframe(display_df)
