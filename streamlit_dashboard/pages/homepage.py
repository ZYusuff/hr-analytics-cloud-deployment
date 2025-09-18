import streamlit as st

# Titel
st.title("🏠 Welcome to the HR Analytics Dashboard")

# intro
st.info("Use the sidebar to navigate between pages.")

# Beskrivning
st.markdown(
    """
    This HR Analytics Dashboard helps talent acquisition specialists work smarter by turning messy job ads from 
    Arbetsförmedlingen into clear and actionable insights.  
    """
)
# Key features
st.markdown(
    """
    ### Key Features  
    - **Track job openings** across different occupation fields  
    - **Spot demand trends** to identify the right candidates  
    - **Save time** by focusing on analysis instead of manual data prep  
    """
)

# Avslut
st.markdown(
    """
    ---
     This tool streamlines the workflow, helping specialists connect the right talent 
    with the right opportunities faster.
    """
)
