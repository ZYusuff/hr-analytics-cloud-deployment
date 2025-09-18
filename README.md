# jobmarket-hr-analytics
The project aims to implement the modern data stack to: - automate the data extraction from Arbetsförmedlingen - transform and structure data - design a dashboard for talent acquisition specialists.

This project was created by: Hugo Lundberg, Katrin Rylander, Masoud Abdisaran, Zamzam Yusuf

This README will guide you through understanding, setting up, and running the project.


### 🛠️ Architecture
```mermaid
graph TB
    classDef source fill:#FFF3CF,stroke:#333,stroke-width:2px
    classDef ingest fill:#FFD6A5,stroke:#333,stroke-width:2px
    classDef warehouse_bg fill:#f9f9f9,stroke:#ddd
    classDef analytics fill:#CDE8E5,stroke:#333,stroke-width:2px
    classDef stg_layer fill:#f2efea,stroke:#555,stroke-dasharray: 2 2
    classDef core_layer fill:#e6f0fa,stroke:#555
    classDef mart_layer fill:#d1e0f1,stroke:#555

    subgraph Source
        API[("JobtechDev API")]
        class API source
    end

    subgraph Ingestion [dlt]
        DLT_SCRIPT["jobsearch_source.py"]
        class DLT_SCRIPT ingest
    end

    subgraph DW [Data Warehouse - Snowflake]
        style DW warehouse_bg
        direction TB

        subgraph Staging Layer
            STG_ADS["stg_ads"]
            class STG_ADS stg_layer
        end
        
        subgraph dbt Core Models
            direction TB
            subgraph src [Staging Models]
                SRC_MODELS["src_*.sql<br>(Clean, Pivot)"]
            end
            subgraph star [Star Schema]
                direction LR
                DIM_MODELS["dim_*.sql"]
                FCT_MODEL["fct_job_ads.sql"]
            end
            class SRC_MODELS,DIM_MODELS,FCT_MODEL core_layer
        end

        subgraph marts [dbt Marts]
            MART_MODELS["mart_*.sql<br>(Aggregated/Denormalized)"]
            class MART_MODELS mart_layer
        end
    end

    subgraph Presentation
        STREAMLIT[("Streamlit App<br>Analytics Dashboard")]
        class STREAMLIT analytics
    end

    %% --- Data Flow ---
    API -- "1. Fetches Job Ad JSON" --> DLT_SCRIPT
    DLT_SCRIPT -- "2. Loads Raw Data" --> STG_ADS
    STG_ADS -- "3. Read via dbt source()" --> SRC_MODELS
    SRC_MODELS -- "4. Builds Star Schema<br>(Surrogate Keys & FKs)" --> DIM_MODELS & FCT_MODEL
    DIM_MODELS & FCT_MODEL -- "5. Consumed & Aggregated" --> MART_MODELS
    MART_MODELS -- "6. Queries Optimized Marts" --> STREAMLIT
```


### ⚙️ Installation
1. Clone the repository
```
git clone https://github.com/<your-repo>/jobmarket-hr-analytics.git
cd jobmarket-hr-analytics
```

2. Create a virtual environment
```
python3 -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows
```

3. Install dependencies
pip install -r requirements.txt

### 🔑 Configuration
1. Create a .env file

In the project root, create a .env file with your Snowflake credentials:

```
SNOWFLAKE_USER="svc_streamlit_app"
SNOWFLAKE_PASSWORD="<PASSWORD_STREAMLIT>"
SNOWFLAKE_ACCOUNT="<ACCOUNT_IDENTIFIER>"
SNOWFLAKE_WAREHOUSE="compute_wh"
SNOWFLAKE_DATABASE="job_ads"
SNOWFLAKE_SCHEMA="marts"
SNOWFLAKE_ROLE="analytics_reader"
```

### 📦 Data Pipelines
1. Load raw data with dlt
```
cd dlt_pipeline
python jobsearch_pipeline.py
```

2. Transform data with dbt
```
cd dbt_code
dbt run
```

### 🖥️ Run the Dashboard

From the streamlit_dashboard folder:

```
streamlit run dashboard_main.py
```

The dashboard opens in your browser (`default: http://localhost:8501`
).
