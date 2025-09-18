# jobmarket-hr-analytics
The project aims to implement the modern data stack to: - automate the data extraction from Arbetsförmedlingen - transform and structure data - design a dashboard for talent acquisition specialists.

This project was created by:
 Hugo Lundberg
 Katrin Rylander
 Masoud Abdisaran
 Zamzam Yusuf

- This README will guide you through understanding, setting up, and running the project.


### ⚙️ Installation
1. Clone the repository
git clone https://github.com/<your-repo>/jobmarket-hr-analytics.git
cd jobmarket-hr-analytics

2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows

3. Install dependencies
pip install -r requirements.txt

### 🔑 Configuration
1. Create a .env file

In the project root, create a .env file with your Snowflake credentials:

SNOWFLAKE_ACCOUNT=xxxxxx
SNOWFLAKE_USER=xxxxxx
SNOWFLAKE_PASSWORD=xxxxxx
SNOWFLAKE_ROLE=xxxxxx
SNOWFLAKE_WAREHOUSE=xxxxxx
SNOWFLAKE_DATABASE=xxxxxx
SNOWFLAKE_SCHEMA=xxxxxx

### 📦 Data Pipelines
1. Load raw data with dlt
cd dlt_pipeline
python jobsearch_pipeline.py

2. Transform data with dbt
cd dbt_code
dbt run --select mart_urgency

### 🖥️ Run the Dashboard

From the streamlit_dashboard folder:

streamlit run dashboard_main.py

The dashboard opens in your browser (default: http://localhost:8501
).
