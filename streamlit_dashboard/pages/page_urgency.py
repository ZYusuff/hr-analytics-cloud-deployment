import streamlit as st
from connect_data_warehouse import get_job_listings
import altair as alt


st.title("📈 Application urgency")
st.write("This page shows which categories need urgent filling based on application deadlines.")

# Hämta mart-data
df = get_job_listings("marts.mart_urgency")

# Låt användaren välja occupation_field
selected_occupation_field = st.session_state.get("occupation_field_filter", "All")

# Filter the DataFrame based on the user's selection.
if selected_occupation_field != "All":
    # If a specific field is chosen, filter the DataFrame to only show rows matching it.
    filtered_df = df[df["OCCUPATION_FIELD"] == selected_occupation_field]
else:
    # If "All" is selected, use the entire, unfiltered DataFrame.
    filtered_df = df

# KPI:er
total_job_ads = int(filtered_df['TOTAL_JOB_ADS'].sum())
total_vacancies = int(filtered_df['TOTAL_VACANCIES'].sum())

st.subheader("📊 Key Metrics")
col1, col2 = st.columns(2)
col1.metric("Total job ads", f"{total_job_ads:,}")
col2.metric("Total vacancies", f"{total_vacancies:,}")

# Grupp och summera per urgency category
urgency_table = (
    filtered_df.groupby("URGENCY_CATEGORY")[["TOTAL_JOB_ADS", "TOTAL_VACANCIES"]]
    .sum()
    .reset_index()
)

# Gör kategorin mer läsbar
urgency_table["URGENCY_CATEGORY"] = urgency_table["URGENCY_CATEGORY"].replace({
    "urgent_7days": "Urgent (≤ 7 days)",
    "closing_14days": "Closing soon (≤ 14 days)",
    "closing_30days": "Closing (≤ 30 days)",
    "normal": "Normal"
})

# Skapa en mapping för snygga rubriker
column_labels = {
    "URGENCY_CATEGORY": "Urgency Category",
    "TOTAL_JOB_ADS": "Total Job Ads",
    "TOTAL_VACANCIES": "Total Vacancies"
}

# Byt namn på kolumnerna med .rename
urgency_table_display = urgency_table.rename(columns=column_labels)

# Visa tabellen
st.subheader("Distribution by urgency category")
st.dataframe(
    urgency_table_display.style.format({
        "Total Job Ads": "{:,}", 
        "Total Vacancies": "{:,}"
    })
)


# Mapping mellan tekniska kolumnnamn och labels
metric_labels = {
    "TOTAL_JOB_ADS": "Total Job Ads",
    "TOTAL_VACANCIES": "Total Vacancies"
}

# Låt användaren välja metrik (visa snygga labels)
metric_label = st.radio(
    "Select metric to visualize:",
    options=list(metric_labels.values()),
    index=1,
    horizontal=True
)

# Konvertera tillbaka till det "riktiga" kolumnnamnet
metric = [k for k, v in metric_labels.items() if v == metric_label][0]


# Skapa interaktivt diagram
# Skapa horisontellt stapeldiagram
chart = (
    alt.Chart(urgency_table)
    .mark_bar()
    .encode(
        y=alt.Y("URGENCY_CATEGORY:N", sort='-x', title="Urgency Category"),
        x=alt.X(f"{metric}:Q", title=metric.replace("_", " ").title()),
        tooltip=["URGENCY_CATEGORY", "TOTAL_JOB_ADS", "TOTAL_VACANCIES"],
        color=alt.Color("URGENCY_CATEGORY:N", legend=None)  # liknar plotly färgkodning
    )
    .properties(
        title=f"Urgency Categories by {metric.replace('_', ' ').title()}",
        width=600,
        height=400
    )
)

st.altair_chart(chart, use_container_width=True)


