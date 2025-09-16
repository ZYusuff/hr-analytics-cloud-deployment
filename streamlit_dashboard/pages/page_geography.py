import streamlit as st
from connect_data_warehouse import create_job_listings_db

# create cached in-memroy duckdb
con = create_job_listings_db("mart_geography", duckdb_table_name="mart_geography")

# filter mart by OCCUPATION_FIELD
selected_occupation_field = st.session_state.occupation_field_filter

if selected_occupation_field == "All":
    rel_base = con.sql("select * from mart_geography")
else:
    rel_base = con.sql(
        "select * from mart_geography where OCCUPATION_FIELD = ?",
        params=[selected_occupation_field],
    )

# -- create datasets

rel_field_country_total = con.sql(
    """
    select
        location_key AS country_code,
        location_display_name,
        total_vacancies,
        occupation_display_name
    from rel_base
    where
        location_level = 'country'
        and occupation_level = 'field'
"""
)

st.dataframe(rel_field_country_total.df())
