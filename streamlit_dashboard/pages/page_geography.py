import streamlit as st
from connect_data_warehouse import query_job_listings

def show():
    st.title("📈 Demand overview")
    st.write("This is where you can check which regions have the highest demand for certain occupations.")

    #df = query_job_listings('mart_occupation_demand')
    
    st.markdown("## Raw data")
    #st.dataframe(df)