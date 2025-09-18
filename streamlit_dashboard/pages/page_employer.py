import streamlit as st
import plotly.express as px
from connect_data_warehouse import get_job_listings

# Set the title and a short description for this page in the Streamlit app
st.title("🏢 Employer Analysis")
st.write("Identify which employers have the highest demand for talent across different occupations.")

# Retrieve the selected occupation field from the session state
selected_occupation_field = st.session_state.occupation_field_filter

# Query the data warehouse to get the 'mart_employer_demand' data mart
df_employer = get_job_listings("mart_employer_demand")

# Filter data based on occupation field selection
if selected_occupation_field != "All":
    df_employer_filtered = df_employer[df_employer["OCCUPATION_FIELD"] == selected_occupation_field]
else:
    df_employer_filtered = df_employer

# ==================================
# KPI SECTION
# ==================================
# Create a row with one column for the KPI
kpi_col1, _ = st.columns([1, 1])

# Filter dataframes by level for different metrics
df_field = df_employer_filtered[df_employer_filtered["LEVEL"] == "field"]

# Get total employers count (unique employers) for the selected field
# Since we've changed the calculation in the mart to count across all fields, 
# we need to count unique employers in the filtered dataframe if a specific field is selected
if selected_occupation_field != "All":
    # Count unique employers only within the selected field
    unique_employers = df_field["EMPLOYER_ID"].nunique()
else:
    # Use the precalculated total from the mart for all fields
    unique_employers = df_field["TOTAL_EMPLOYER_COUNT"].max()

# Format numbers with spaces as thousand separators
formatted_unique = f"{unique_employers:,}".replace(",", " ")

# KPI: Total Unique Employers
with kpi_col1:
    st.markdown(f"""
    <div style="display: flex; align-items: center;">
        <div>
            <div style="font-size: 1.5rem; font-weight: bold; margin-bottom: 0;">
                Total Active Employers
            </div>
            <div style="font-size: 1rem; color: #666; margin-top: 0;">
                for {selected_occupation_field if selected_occupation_field != 'All' else 'All Fields'}
            </div>
        </div>
        <div style="margin-left: 30px;">
            <span style="font-size: 2.5rem; color: #0066b2; font-weight: bold;">
                {formatted_unique}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Add vertical spacing between sections
st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

# ==================================
# EMPLOYER TRENDS SECTION
# ==================================

# Add CSS for better layout of titles and toggles
st.markdown("""
<style>
.section-header {
    display: flex;
    align-items: center;
    margin-bottom: 0;
}
.section-header h3 {
    margin-bottom: 0;
    margin-right: 15px;
}
</style>
""", unsafe_allow_html=True)

# Create section header with title and toggle for top employers
st.markdown('<div class="section-header"><h3>Top Employers:</h3></div>', unsafe_allow_html=True)
employers_top_n = st.radio("Number of employers to display", [5, 10], horizontal=True, key="employers_toggle", label_visibility="hidden")

# Get top N employers by demand based on toggle selection
# We're filtering by field level and using overall_rank to get top employers
df_field_employers = df_employer_filtered[df_employer_filtered["LEVEL"] == "field"]
top_employers = df_field_employers.sort_values("VACANCY_COUNT", ascending=False).head(employers_top_n)

# Create horizontal bar chart for top employers
fig_top_employers = px.bar(
    top_employers,
    y="EMPLOYER_NAME",
    x="VACANCY_COUNT",
    color="OCCUPATION_FIELD",
    orientation="h",
    title=f"Top {employers_top_n} Employers by Demand",
    labels={"VACANCY_COUNT": "Number of Vacancies"},
    height=400
)
# Update layout without y-axis label to declutter
fig_top_employers.update_layout(
    yaxis={
        'categoryorder': 'total ascending',
        'title': None  # Remove y-axis title
    },
    margin=dict(l=20, r=20, t=40, b=20)  # Adjust margins
)
st.plotly_chart(fig_top_employers, width='stretch')

# ==================================
# GROUP SECTION
# ==================================

# Occupation Group Selection for Drill-down
st.markdown("### Drill Down into Employers by Occupation Group")

# Get unique occupation groups for the selected field
df_group = df_employer_filtered[df_employer_filtered["LEVEL"] == "group"]
available_groups = df_group["OCCUPATION_GROUP"].unique()

if len(available_groups) > 0:
    selected_group = st.selectbox("Select an occupation group to explore", available_groups)
    
    # Get all employers for the selected group
    employers_in_group = df_group[df_group["OCCUPATION_GROUP"] == selected_group]
    all_group_employers = employers_in_group.sort_values("VACANCY_COUNT", ascending=False)

    # Create a table showing all employers within the selected group
    employers_table = all_group_employers[["EMPLOYER_NAME", "VACANCY_COUNT"]].sort_values("VACANCY_COUNT", ascending=False)
    
    # Display the table with employers and their vacancy counts
    st.markdown(f"#### All Employers in {selected_group}")
    st.dataframe(
        employers_table,
        column_config={
            "EMPLOYER_NAME": "Employer",
            "VACANCY_COUNT": st.column_config.NumberColumn(
                "Number of Vacancies",
                format="%d",
            )
        },
        hide_index=True,
        width='stretch'
    )
else:
    st.write("No occupation groups available for the selected field.")

