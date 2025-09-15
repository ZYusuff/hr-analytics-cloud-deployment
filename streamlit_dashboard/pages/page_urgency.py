import streamlit as st
from connect_data_warehouse import query_job_listings

def show():
    st.title("📈 Application urgency")
    st.write("This is where you can see which roles need urgent filling.")

    df = query_job_listings('mart_urgency')

    selected_occupation_field = "Hälso- och sjukvård"   
    
    st.markdown("## Raw data for selected occupation field: " + selected_occupation_field)
    st.dataframe(df[df['OCCUPATION_FIELD'] == selected_occupation_field])
