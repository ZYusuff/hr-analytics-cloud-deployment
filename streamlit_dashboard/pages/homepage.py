import streamlit as st

# Titel

st.title("🏠 Job Market Analytics Dashboard")
st.write("This dashboard provides valuable insights into labor market trends, employer demands, and job opportunities across different occupations and regions in Sweden.")
# Key features
st.markdown(
    """
    ### Key Features  
    - **Track job openings** across different occupation fields  
    - **Spot demand trends** to identify the right candidates  
    - **Save time** by focusing on analysis instead of manual data prep  
    """
)
st.info("Use the sidebar to navigate between pages and to filter data by occupation field.")

st.markdown(
"""## Dashboard Pages

### 📈 Demand Overview
- Explore occupation demand trends and discover which occupations are most in-demand in the Swedish job market. 
- View total active vacancies, top occupation groups, and detailed breakdowns of demand by field, group, and specific occupation.

### 🏢 Employer Analysis
- Identify which employers have the highest demand for talent across different occupations. 
- See which companies are actively hiring, their vacancy distributions, and which employers dominate specific occupation fields.

### ⏳ Application Urgency
- Track which roles need urgent filling based on application deadlines. 
- View the distribution of job ads by urgency category, from highly urgent positions closing within 7 days to those with normal timelines.

### 🌍 Geography
- Visualize job demand across different regions and municipalities in Sweden using interactive maps. 
- Understand geographic distribution of opportunities and analyze regional labor market trends.

### 🔎 Job Browser
- Search and explore individual job listings in detail. 
- Filter by headline, employer, or region to find specific opportunities, and view complete job descriptions and requirements.
""")


