import streamlit as st
from connect_data_warehouse import create_job_listings_db

# create cached in-memroy duckdb
con = create_job_listings_db("mart_geography", duckdb_table_name="db_mart")

# filter mart by OCCUPATION_FIELD
selected_occupation_field = st.session_state.occupation_field_filter

if selected_occupation_field == "All":
    rel_filtered = con.sql("select * from db_mart")
else:
    rel_filtered = con.sql(
        "select * from db_mart where OCCUPATION_FIELD = ?",
        params=[selected_occupation_field],
    )

