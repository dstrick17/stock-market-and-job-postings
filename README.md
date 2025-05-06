# Job & Stock Market Insight Platform (Azure Data Pipeline Project)

This project explores the relationship between job postings and stock market trends using a scalable Azure data pipeline. It integrates real-time and batch data from the Adzuna API (job listings) and Alpha Vantage API (stock data), processes it through a medallion architecture (Bronze → Silver → Gold), and enables downstream analysis via Azure ML and Power BI.

Dashboard link - https://app.powerbi.com/view?r=eyJrIjoiYjVmNDZiOGItNmZmNi00Mzk0LTgzN2MtYTZhYmRmZmJmMzc3IiwidCI6ImQ1N2QzMmNjLWMxMjEtNDg4Zi1iMDdiLWRmZTcwNTY4MGM3MSIsImMiOjN9

---

##  Architecture Overview

**1. Data Sources**
- **Adzuna API**: Job listings across 23 categories (e.g., IT, Engineering, Finance).
- **Alpha Vantage API**: Batch and live stock prices for 25 publicly traded companies and 3 ETFs (QQQ, XLF, XLV).

**2. Azure Services Used**
- **Azure Function Apps**: Ingest live stock prices into Event Hub.
- **Azure Data Factory**: ETL pipeline for batch job and stock data.
- **Azure Synapse Analytics**: SQL-based transformations for Gold layer.
- **Azure ML**: Salary prediction using AutoML VotingEnsemble model.
- **Power BI**: Dashboards to visualize trends in job postings vs. stock movements.

**3. Medallion Architecture**
- **Bronze Layer**: Raw API data (JSON).
- **Silver Layer**: Cleaned, flattened Parquet files.
- **Gold Layer**: Aggregated metrics (job counts, average salaries, stock prices).

---

## Repository Structure

| Folder | Description |
|--------|-------------|
| `dataflow/` | Data Factory Data Flow definitions |
| `dataset/` | Datasets used in pipelines |
| `factory/` | Factory-wide configurations |
| `functionApp/` | Code for live ingestion from Alpha Vantage |
| `linkedService/` | Linked service configs (HTTP, Data Lake) |
| `pipeline/` | ETL pipeline JSON definitions |
| `trigger/` | Pipeline trigger configurations |
| `parameters.json` | Deployment parameters for ARM |
| `template.json` | Main ARM template |
| `publish_config.json` | Publish settings for Azure deployment |

---

## Deployment Instructions

1. Clone the repo and open in Azure Data Factory.
2. Deploy `template.json` and `parameters.json` to your resource group.
3. Configure your Event Hub and Function App for live streaming.
4. Use Synapse or Power BI for downstream analytics.

---

## Model Summary (Azure ML)

- **Algorithm**: VotingEnsemble (XGBoost, LightGBM)
- **nRMSE**: 0.01019
- **MAE**: $717.57
- **R²**: 0.9959

---

## Power BI Dashboard

The Power BI report includes:
- Sector trends over time
- Hiring trends in relation to stock market
- Hiring trends vs market volatility
- Salary prediction model results
- Interactive comparison of job postings vs. stock price (e.g., QQQ vs IT jobs)

---

##  Future Work

- Integrate LinkedIn or Indeed APIs for broader job coverage.
- Expand to multi-year time series analysis.
- Add forecast models for salary and demand trends.

---

## License

MIT License – feel free to use, extend, or cite with attribution.
