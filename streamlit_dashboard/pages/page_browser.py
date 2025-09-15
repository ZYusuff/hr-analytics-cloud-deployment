import streamlit as st
from connect_data_warehouse import query_job_listings

def show():
    st.title("📈 Job browser")
    st.write("This is where you can search and view full content of a specific ad.")

    df = query_job_listings('mart_job_browser')

    selected_occupation_field = "Hälso- och sjukvård"   
    
    st.markdown("## Job listings data for selected occupation field: " + selected_occupation_field)
    st.dataframe(df[df['OCCUPATION_FIELD'] == selected_occupation_field])
