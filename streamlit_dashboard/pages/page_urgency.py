import streamlit as st
from connect_data_warehouse import query_job_listings
import pandas as pd
import altair as alt


def show():
    st.title("📈 Application urgency")
    st.write("See which roles need urgent filling based on application deadlines.")

    # Hämta mart-data
    df = query_job_listings("marts.mart_urgency")

    # Låt användaren välja occupation_field
    selected_occupation_field = st.selectbox(
        "Select occupation field:",
        sorted(df['OCCUPATION_FIELD'].unique())
    )

    # Filtrera data
    filtered_df = df[df['OCCUPATION_FIELD'] == selected_occupation_field]

    # KPI:er
    total_job_ads = int(filtered_df['TOTAL_JOB_ADS'].sum())
    total_vacancies = int(filtered_df['TOTAL_VACANCIES'].sum())

    st.subheader("📊 Key Metrics")
    col1, col2 = st.columns(2)
    col1.metric("Total Job Ads", f"{total_job_ads:,}")
    col2.metric("Total Vacancies", f"{total_vacancies:,}")

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

    # Sortera på antal vakanser
    urgency_table = urgency_table.sort_values("TOTAL_VACANCIES", ascending=False)

    # Visa tabellen
    st.subheader("📋 Distribution by urgency category")
    st.dataframe(
        urgency_table.style.format({"TOTAL_JOB_ADS": "{:,}", "TOTAL_VACANCIES": "{:,}"})
    )

    # Låt användaren välja metrik
    metric = st.radio(
        "Select metric to visualize:",
        options=["TOTAL_JOB_ADS", "TOTAL_VACANCIES"],
        index=1,
        horizontal=True
    )

    # Skapa interaktivt diagram
    chart = (
        alt.Chart(urgency_table)
        .mark_bar()
        .encode(
            x=alt.X("URGENCY_CATEGORY:N", sort="-y", title="Urgency Category"),
            y=alt.Y(f"{metric}:Q", title=metric.replace("_", " ").title()),
            tooltip=["URGENCY_CATEGORY", "TOTAL_JOB_ADS", "TOTAL_VACANCIES"]
        )
        .properties(width=600, height=400)
    )
    st.altair_chart(chart, use_container_width=True)

    # Raw data
    st.markdown(f"### 📂 Raw data for {selected_occupation_field}")
    st.dataframe(filtered_df)


