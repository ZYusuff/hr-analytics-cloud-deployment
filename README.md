## ☁️ Azure File Share Setup & Cost Estimation

### Purpose
When deploying our data pipeline to the cloud, we need persistent storage to replace the local `data_warehouse` folder used in local development.  
To achieve this, we use **Azure File Share**, which provides a simple and scalable cloud-based storage solution for our DuckDB database and `dbt profiles.yml`.

---

### Step 1 – Create Azure Storage Account

1. Navigate to [Azure Portal](https://portal.azure.com)
2. Search for **“Storage accounts”** → click **Create**
3. Fill in the form:

| Field | Example Value |
|--------|----------------|
| **Subscription** | (Your Azure subscription) |
| **Resource group** | `rg-hranalytics` |
| **Storage account name** | `hranalyticsstorage` *(must be unique)* |
| **Region** | `Sweden Central` |
| **Performance** | Standard |
| **Redundancy** | Locally-redundant storage (LRS) |

Click **Review + Create** → **Create**

---

### 📁 Step 2 – Create File Share

Once the storage account is created:

1. Go to your **Storage account**
2. Open **Data storage → File shares**
3. Click **➕ File share**
4. Fill in:

| Field | Example |
|--------|----------|
| **Name** | `data` |
| **Quota (GB)** | 100 |
| **Access tier** | Transaction optimized |

Click **Create**

---

### 📂 Step 3 – Upload `dbt profiles.yml`

1. Go to your newly created **File Share → data**
2. Click **➕ Add directory**, name it `.dbt`
3. Inside the `.dbt` directory, click **Upload**
4. Upload your local `profiles.yml` file (usually located at `~/.dbt/profiles.yml`)

---

### 🔑 Step 4 – Retrieve Access Keys

Your containerized applications will need credentials to access the File Share.

1. Go to your **Storage account**
2. Click **Security + networking → Access keys**
3. Click **Show keys**
4. Copy the following details:

| Variable | Description |
|-----------|--------------|
| **STORAGE_ACCOUNT_NAME** | e.g., `hranalyticsstorage` |
| **STORAGE_ACCOUNT_KEY** | (your key1 value) |
| **FILE_SHARE_NAME** | `data` |

These values will later be referenced in your Docker Compose or environment configuration.

---

### 🐳 Step 5 – Mount Azure File Share in Docker

To make your containers access the Azure File Share, add the following configuration in your `docker-compose.yml`:

```yaml
volumes:
  - azurefileshare:/pipeline/data_warehouse

volumes:
  azurefileshare:
    driver: azure_file
    driver_opts:
      share_name: data
      storage_account_name: hranalyticsstorage
      storage_account_key: ${STORAGE_ACCOUNT_KEY}
```


## Cost Estimation — Cloud Deployment (Azure)

This section provides an overview of the expected monthly cost for deploying the HR Analytics pipeline and dashboard on Azure.  
The goal is to keep the dashboard **available 24/7** and update the **DuckDB data warehouse once per day**.

### Azure Resources & Cost Drivers

| **Azure Resource** | **Description** | **Primary Cost Model** | **Fixed Cost Components (Charged 24/7)** | **Running Cost Components** |
|--------------------|-----------------|------------------------|------------------------------------------|-----------------------------|
| **App Service Plan** | Hosts the Streamlit dashboard. Using the **Basic (B1)** Linux plan with 1 instance. Each tier has a fixed amount of vCPU, RAM, and storage, paid 24/7 even if idle. | Fixed (Reserved Compute) | Basic tier with 1 instance | N/A |
| **Container Registry** | Stores, manages, and distributes Docker images. Pricing is tier-based; we use the **Basic** tier. | Fixed (Tier-Based) | Daily fee for Basic tier (includes base storage) | Extra cost only if storage limits are exceeded |
| **Storage Account (Azure File Share)** | Used for persistent storage of the **DuckDB** data warehouse and `profiles.yml`. Billed by GB/month and transaction count. Using **LRS** redundancy and “Cool” access tier. | Consumption (Usage-Based) | N/A | Storage capacity (GB/month) and transactions (per 10,000 ops) |
| **Container Instances (ACI)** | Runs the pipeline container once per day. Billed per vCPU-second and GB-second while running. | Consumption (Serverless Compute) | N/A | vCPU and memory usage duration (per second) |

### Assumptions
- DuckDB file size: **~1 GB**
- Pipeline runs **once per day**
- Dashboard runs **24/7**
- Region: **Sweden Central**
- Pricing model: **Pay-As-You-Go**

### Pricing Example

| **Resource** | **Pricing Details** | **Estimated Monthly Cost (USD)** |
|---------------|---------------------|----------------------------------|
| **Container Instance – DWH Pipeline** | 1 container group (4GB RAM, ~17% CPU usage).<br>Price: $0.0000129 per vCPU/s + $0.0000014 per GB/s | ≈ **$33.55 + $14.72 = $48.27** |
| **Container Instance – Dashboard** | 1 container group (4GB RAM, same specs as pipeline) | ≈ **$48.27** |
| **Storage Account (Azure File Share)** | 1 GB stored, <10,000 operations | **$0.26** |
| **App Service Plan (Basic B1)** | 1 Core, 1.75 GB RAM, 10 GB Storage | **$13.14** |
| **Azure Container Registry (Basic Tier)** | $0.167/day × 30 days | **$5.00** |

### Total Monthly Estimate

| **Resource Group** | **Monthly Cost (USD)** |
|--------------------|------------------------|
| Containers (2x) | $96.54 |
| Storage | $0.26 |
| Web App | $13.14 |
| Container Registry | $5.00 |
| **Total Estimated Monthly Cost** | **≈ $115.00 / month** |

> 💬 *This estimate reflects a lightweight educational deployment in Sweden Central using Pay-as-you-go pricing. Costs may vary slightly depending on usage, scaling, and Azure region.*

