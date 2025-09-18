import streamlit as st


st.title("🏠 Welcome to the Job Market Analytics Dashboard")
st.write("Welcome to your comprehensive Swedish job market analytics platform! This dashboard provides valuable insights into labor market trends, employer demands, and job opportunities across different occupations and regions in Sweden.")

st.markdown("""
## About This Dashboard

This dashboard analyzes real-time job listings data to help you understand the labor market landscape. Whether you're a job seeker, recruiter, policy maker, or researcher, you can find valuable insights to support your decisions.

Use the sidebar on the left to filter data by occupation field. This filter applies across all pages, allowing you to focus on specific sectors of interest.

## Dashboard Pages

### 📈 Demand Overview
Explore occupation demand trends and discover which occupations are most in-demand in the Swedish job market. View total active vacancies, top occupation groups, and detailed breakdowns of demand by field, group, and specific occupation.

### 🏢 Employer Analysis
Identify which employers have the highest demand for talent across different occupations. See which companies are actively hiring, their vacancy distributions, and which employers dominate specific occupation fields.

### ⏳ Application Urgency
Track which roles need urgent filling based on application deadlines. View the distribution of job ads by urgency category, from highly urgent positions closing within 7 days to those with normal timelines.

### 🌍 Geography
Visualize job demand across different regions and municipalities in Sweden using interactive maps. Understand geographic distribution of opportunities and analyze regional labor market trends.

### 🔎 Job Browser
Search and explore individual job listings in detail. Filter by headline, employer, or region to find specific opportunities, and view complete job descriptions and requirements.
""")

st.info("Use the sidebar to navigate between pages and to filter data by occupation field.")
