import streamlit as st
from pathlib import Path
import sys
from connect_data_warehouse import query_job_listings





# Set the title and a short description for this page in the Streamlit app.
st.title("📈Job browser")
st.write("This is where you can search and view full content of a specific ad.")

# Retrieve the selected occupation field from the session state.
# This value is set by a filter on another page (e.g., the main page).
selected_occupation_field = st.session_state.occupation_field_filter

# Display a confirmation message to the user showing which filter is currently active.
st.write(f"Analyzing data for region: **{selected_occupation_field}**")

# Query the data warehouse to get the 'mart_urgency' data mart.
# This DataFrame contains all the data needed for our urgency analysis.
df = query_job_listings("mart_job_browser")

# Add a subheader for the raw data table.
st.markdown("## Job listings data for selected occupation field: " + selected_occupation_field)

# Filter the DataFrame based on the user's selection.
if selected_occupation_field != "All":
    # If a specific field is chosen, filter the DataFrame to only show rows matching it.
    display_df = df[df["OCCUPATION_FIELD"] == selected_occupation_field]
else:
    # If "All" is selected, use the entire, unfiltered DataFrame.
    display_df = df

# Visa antal annonser som hittats
st.markdown(f"**Antal annonser hittade:** {len(display_df)}")

# Visa tabellen med bred layout
st.dataframe(display_df, use_container_width=True)

# Grupp och räkna antal annonser per region
region_counts = display_df.groupby("WORKPLACE_REGION")["EMPLOYER_NAME"].count().sort_values(ascending=False)

# Visa bar chart
st.markdown("### Number of job ads per region")
st.bar_chart(region_counts)



# Lägg en sökfunktion 
st.markdown("###  Search job ads")
search_term = st.text_input("Search by headline, employer or region:")

filtered_df = display_df.copy()

if search_term:
    filtered_df = filtered_df[
        filtered_df["HEADLINE"].str.contains(search_term, case=False, na=False)
        | filtered_df["EMPLOYER_NAME"].str.contains(search_term, case=False, na=False)
        | filtered_df["WORKPLACE_REGION"].str.contains(search_term, case=False, na=False)
    ]

# Visa resultaten av sökningen
st.markdown("###  Filtered job ads")
if not filtered_df.empty:
    job_selection = st.selectbox(
        "Select a job ad to view details:",
        options=filtered_df["JOB_AD_ID"].astype(str),
        format_func=lambda x: f"{x} - {filtered_df.loc[filtered_df['JOB_AD_ID'].astype(str)==x,'HEADLINE'].values[0]}",
    )

    # Visa detaljerad information för vald annons
    job = filtered_df[filtered_df["JOB_AD_ID"].astype(str) == job_selection].iloc[0]

    st.subheader(job["HEADLINE"])
    st.write(f"**Employer:** {job['EMPLOYER_NAME']}")
    st.write(f"**Location:** {job['WORKPLACE_CITY']}, {job['WORKPLACE_REGION']}, {job['WORKPLACE_COUNTRY']}")
    st.write(f"**Employment type:** {job['EMPLOYMENT_TYPE']}")
    st.write(f"**Duration:** {job['DURATION']}")
    st.write(f"**Salary type:** {job['SALARY_TYPE']}")
    st.write(f"**Vacancies:** {job.get('VACANCIES','N/A')}")

    st.markdown("###  Description")
    st.write(job["DESCRIPTION"])

    st.markdown("### Requirements")
    st.write(f"- Experience required: {job['EXPERIENCE_REQUIRED']}")
    st.write(f"- Driver’s license: {job['DRIVER_LICENSE']}")
    st.write(f"- Access to own car: {job['ACCESS_TO_OWN_CAR']}")
    st.write(f"- Must-have skills: {job.get('MUST_HAVE_SKILLS','N/A')}")
else:
    st.info("No job ads found matching your search.")