import streamlit as st
import pandas as pd
import plotly.express as px
from connect_data_warehouse import get_job_listings

# Set the title and a short description for this page in the Streamlit app
st.title("📈 Demand overview")
st.write("Analyze occupation demand trends and see which occupations are most in-demand.")

# Retrieve the selected occupation field from the session state
selected_occupation_field = st.session_state.occupation_field_filter

# Query the data warehouse to get the data marts
df_demand = get_job_listings("mart_occupation_demand")
df_trends = get_job_listings("mart_trends")
df_requirements = get_job_listings("mart_occupation_requirements")

# Filter data based on occupation field selection
if selected_occupation_field != "All":
    df_demand_filtered = df_demand[df_demand["OCCUPATION_FIELD"] == selected_occupation_field]
    df_trends_filtered = df_trends[df_trends["OCCUPATION_FIELD"] == selected_occupation_field]
    df_requirements_filtered = df_requirements[df_requirements["OCCUPATION_FIELD"] == selected_occupation_field]
else:
    df_demand_filtered = df_demand
    df_trends_filtered = df_trends
    df_requirements_filtered = df_requirements

# ==================================
# KPI SECTION
# ==================================
# Create a row with two columns - one for the KPI title and value, one for spacing
kpi_col, spacing_col = st.columns([3, 1])

# Filter dataframes by level for different metrics
df_field = df_demand_filtered[df_demand_filtered["LEVEL"] == "field"]
df_group = df_demand_filtered[df_demand_filtered["LEVEL"] == "group"]
df_occupation = df_demand_filtered[df_demand_filtered["LEVEL"] == "occupation"]

# Calculate total vacancies (should be the same across all levels if data is consistent)
total_vacancies = df_field["VACANCY_COUNT"].sum()

# Format number with spaces as thousand separators
formatted_vacancies = f"{total_vacancies:,}".replace(",", " ")

# Create a cleaner KPI display with title on top row and field info on second row
with kpi_col:
    st.markdown(f"""
    <div style="display: flex; align-items: center;">
        <div>
            <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0;">
                Total Active Vacancies
            </div>
            <div style="font-size: 1.5rem; color: #666; margin-top: 0;">
                for {selected_occupation_field if selected_occupation_field != 'All' else 'All Fields'}
            </div>
        </div>
        <div style="margin-left: 30px;">
            <span style="font-size: 3rem; color: #0066b2; font-weight: bold;">
                {formatted_vacancies}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Add vertical spacing between sections
st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

# ==================================
# DEMAND TRENDS SECTION
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

# Create section header with title and toggle
st.markdown('<div class="section-header"><h3>Top Occupation Groups:</h3></div>', unsafe_allow_html=True)
groups_top_n = st.radio("Number of groups to display", [5, 10], horizontal=True, key="groups_toggle", label_visibility="hidden")

# Get top N occupation groups by demand based on toggle selection
top_groups = df_group.sort_values("VACANCY_COUNT", ascending=False).head(groups_top_n)

# Create horizontal bar chart for top occupation groups
fig_top_groups = px.bar(
    top_groups,
    y="OCCUPATION_GROUP",
    x="VACANCY_COUNT",
    color="OCCUPATION_FIELD",
    orientation="h",
    title=f"Top {groups_top_n} Groups by Demand",
    labels={"VACANCY_COUNT": "Number of Vacancies"},
    height=400
)
# Update layout without y-axis label to declutter
fig_top_groups.update_layout(
    yaxis={
        'categoryorder': 'total ascending',
        'title': None  # Remove y-axis title
    },
    margin=dict(l=20, r=20, t=40, b=20)  # Adjust margins
)
st.plotly_chart(fig_top_groups, width='stretch')

# Create section header with title and toggle for occupations
st.markdown('<div class="section-header"><h3>Top Occupations:</h3></div>', unsafe_allow_html=True)
occupations_top_n = st.radio("Number of occupations to display", [5, 10], horizontal=True, key="occupations_toggle", label_visibility="hidden")

# Get top N occupations by demand based on toggle selection
top_occupations = df_occupation.sort_values("VACANCY_COUNT", ascending=False).head(occupations_top_n)

# Create horizontal bar chart for top occupations
fig_top_occupations = px.bar(
    top_occupations,
    y="OCCUPATION_LABEL",
    x="VACANCY_COUNT",
    color="OCCUPATION_GROUP",
    orientation="h",
    title=f"Top {occupations_top_n} Occupations by Demand",
    labels={"VACANCY_COUNT": "Number of Vacancies"},
    height=400
)
# Update layout without y-axis label to declutter
fig_top_occupations.update_layout(
    yaxis={
        'categoryorder': 'total ascending',
        'title': None  # Remove y-axis title
    },
    margin=dict(l=20, r=20, t=40, b=20)  # Adjust margins
)
st.plotly_chart(fig_top_occupations, width='stretch')

# ==================================
# GROUP SECTION
# ==================================

# Occupation Group Selection for Drill-down
st.markdown("### Drill Down into Specific Occupation Group")

# Get unique occupation groups for the selected field
available_groups = df_group["OCCUPATION_GROUP"].unique()
available_groups = sorted(available_groups)  # Sort alphabetically
selected_group = st.selectbox("Select an occupation group to explore", available_groups)

# Create a table showing occupations within the selected group
occupations_in_group = df_occupation[df_occupation["OCCUPATION_GROUP"] == selected_group]
occupations_table = occupations_in_group[["OCCUPATION_LABEL", "VACANCY_COUNT"]].sort_values("VACANCY_COUNT", ascending=False)

# Get requirements data for the selected group
requirements_group = df_requirements_filtered[
    (df_requirements_filtered["LEVEL"] == "group") & 
    (df_requirements_filtered["OCCUPATION_GROUP"] == selected_group)
]

requirements_occupations = df_requirements_filtered[
    (df_requirements_filtered["LEVEL"] == "occupation") & 
    (df_requirements_filtered["OCCUPATION_GROUP"] == selected_group)
]

# Merge demand and requirements data for occupations
if not requirements_occupations.empty:
    merged_data = pd.merge(
        occupations_table,
        requirements_occupations[["OCCUPATION_LABEL", "EXPERIENCE_REQUIRED_PERCENTAGE", 
                                "DRIVER_LICENSE_PERCENTAGE", "OWN_CAR_PERCENTAGE"]],
        on="OCCUPATION_LABEL",
        how="left"
    )
    
    # Display the table with occupations and their vacancy counts and requirements
    st.markdown(f"#### Occupations within {selected_group}")
    
    # Format merged data
    st.dataframe(
        merged_data,
        column_config={
            "OCCUPATION_LABEL": "Occupation",
            "VACANCY_COUNT": st.column_config.NumberColumn(
                "Number of Vacancies",
                format="%d",
            ),
            "EXPERIENCE_REQUIRED_PERCENTAGE": st.column_config.NumberColumn(
                "% Requiring Experience",
                format="%.1f%%",
            ),
            "DRIVER_LICENSE_PERCENTAGE": st.column_config.NumberColumn(
                "% Requiring Driver's License",
                format="%.1f%%",
            ),
            "OWN_CAR_PERCENTAGE": st.column_config.NumberColumn(
                "% Requiring Car",
                format="%.1f%%",
            )
        },
        hide_index=True,
        width='stretch'
    )
    
    # Display a summary of requirements for the selected group
    if not requirements_group.empty:
        st.markdown(f"#### Overall Requirements for {selected_group}")
        col1, col2, col3 = st.columns(3)
        
        # Extract the percentages (there should be just one row for the selected group)
        exp_pct = requirements_group["EXPERIENCE_REQUIRED_PERCENTAGE"].iloc[0]
        lic_pct = requirements_group["DRIVER_LICENSE_PERCENTAGE"].iloc[0]
        car_pct = requirements_group["OWN_CAR_PERCENTAGE"].iloc[0]
        
        with col1:
            st.metric("Experience Required", f"{exp_pct:.1f}%")
        with col2:
            st.metric("Driver's License Required", f"{lic_pct:.1f}%")
        with col3:
            st.metric("Own Car Required", f"{car_pct:.1f}%")
else:
    # Display the original table if no requirements data is available
    st.markdown(f"#### Occupations within {selected_group}")
    st.dataframe(
        occupations_table,
        column_config={
            "OCCUPATION_LABEL": "Occupation",
            "VACANCY_COUNT": st.column_config.NumberColumn(
                "Number of Vacancies",
                format="%d",
            )
        },
        hide_index=True,
        width='stretch'
    )

# Add vertical spacing between sections
st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

# ==================================
# TRENDS VISUALIZATION SECTION
# ==================================

st.markdown("## 📊 Vacancy Trends Over Time")
st.write("Analyze how job vacancies have changed over time")

# Create a section for field-level trends
st.markdown(f"### Trends for {selected_occupation_field if selected_occupation_field != 'All' else 'All Fields'}")

# Filter the trends data for field level with daily granularity
field_trends = df_trends_filtered[
    (df_trends_filtered["TIME_GRANULARITY"] == "daily") & 
    (df_trends_filtered["OCCUPATION_GROUP"].isna()) & 
    (df_trends_filtered["OCCUPATION_LABEL"].isna())
]

# Sort the data by trend_date to ensure proper time series display
field_trends = field_trends.sort_values("TREND_DATE")

# Create the line chart for field-level trends
if not field_trends.empty:
    fig_field_trends = px.line(
        field_trends,
        x="TREND_DATE",
        y="VACANCIES",
        color="OCCUPATION_FIELD" if selected_occupation_field == "All" else None,
        title=f"Vacancy Trends for {selected_occupation_field if selected_occupation_field != 'All' else 'All Fields'}",
        labels={
            "TREND_DATE": "Publication Date",
            "VACANCIES": "Number of Vacancies"
        },
        height=400
    )
    
    # Improve the layout and add markers for better visibility
    fig_field_trends.update_traces(mode='lines+markers', marker=dict(size=6))
    fig_field_trends.update_layout(
        xaxis_title="Publication Date",
        yaxis_title="Number of Vacancies",
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified"  # Show all values for the same x coordinate
    )
    
    st.plotly_chart(fig_field_trends, use_container_width=True)
else:
    st.info(f"No trend data available for {selected_occupation_field}. Please select a different occupation field.")

# Add a separator
st.markdown("<hr style='margin-top: 1.5rem; margin-bottom: 1.5rem;'>", unsafe_allow_html=True)

# Create a section for group-level trends
st.markdown("### Group-Level Trends")
st.write("Select a specific occupation group to see its vacancy trends over time")

# Get unique occupation groups from the filtered trends data
trend_groups = df_trends_filtered[
    (df_trends_filtered["OCCUPATION_GROUP"].notna()) & 
    (df_trends_filtered["OCCUPATION_LABEL"].isna())
]["OCCUPATION_GROUP"].unique()

# Sort the trend groups alphabetically
trend_groups = sorted(trend_groups)

if len(trend_groups) > 0:
    # Create a selectbox for group selection
    selected_trend_group = st.selectbox(
        "Select an occupation group",
        trend_groups,
        key="trend_group_selector"
    )

    # Filter the trends data for the selected group with daily granularity
    group_trends = df_trends_filtered[
        (df_trends_filtered["TIME_GRANULARITY"] == "daily") & 
        (df_trends_filtered["OCCUPATION_GROUP"] == selected_trend_group) & 
        (df_trends_filtered["OCCUPATION_LABEL"].isna())
    ]

    # Sort the data by trend_date to ensure proper time series display
    group_trends = group_trends.sort_values("TREND_DATE")

    # Create the line chart for group-level trends
    if not group_trends.empty:
        fig_group_trends = px.line(
            group_trends,
            x="TREND_DATE",
            y="VACANCIES",
            title=f"Vacancy Trends for {selected_trend_group}",
            labels={
                "TREND_DATE": "Publication Date",
                "VACANCIES": "Number of Vacancies"
            },
            height=400
        )
        
        # Improve the layout and add markers for better visibility
        fig_group_trends.update_traces(mode='lines+markers', marker=dict(size=6))
        fig_group_trends.update_layout(
            xaxis_title="Publication Date",
            yaxis_title="Number of Vacancies",
            margin=dict(l=20, r=20, t=40, b=20),
            hovermode="x unified"  # Show all values for the same x coordinate
        )
        
        st.plotly_chart(fig_group_trends, use_container_width=True)
    else:
        st.info(f"No trend data available for {selected_trend_group}.")
else:
    st.warning(f"No occupation groups available for {selected_occupation_field}. Please select a different occupation field.")

# Add vertical spacing between sections
st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)


# ==================================
# RAW DATA SECTION
# ==================================
# Add an expander for raw data
#with st.expander("View Raw Data"):
#    st.markdown(f"## Raw data for selected occupation field: {selected_occupation_field}")
#    st.dataframe(df_demand_filtered, width='stretch')
