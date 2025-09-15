import streamlit as st
from connect_data_warehouse import query_job_listings

def show():
    st.title("📈 Demand overview")
    st.write("This is where you can show which specific occupation groups and specific occupations are in demand.")

    df = query_job_listings('mart_occupation_demand')

    selected_occupation_field = "Hälso- och sjukvård"
    
    st.markdown("## Raw data for selected occupation field: " + selected_occupation_field)
    st.dataframe(df[df['OCCUPATION_FIELD'] == selected_occupation_field])
    #st.dataframe(df)