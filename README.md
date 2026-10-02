# End-to-End Churn Analytics Platform

Telecom customers who cancel (churn) cost revenue. This project takes the public Telco Customer Churn dataset (7,043 customers) from raw CSV to business recommendations: who churns, why, who is at risk next, and how much revenue is involved.

**Architecture:** Kaggle CSV -> DuckDB bronze / silver / gold -> scikit-learn + MLflow -> Streamlit + Plotly dashboard

**Tech stack:** Python, SQL, DuckDB, scikit-learn, MLflow, Streamlit, Plotly, Bash

## Who is this for?

| User | Uses | Decision |
|---|---|---|
| Retention manager | "Who to contact first" tab, CSV export | Which at-risk customers to contact this week |
| Marketing | "Who churns" tab | Which segments need campaigns or contract offers |
| Product / pricing | "Why they churn" tab | Which plan features drive churn |
| Finance / leadership | KPI cards, save-rate slider | Revenue at risk and retention budget |
| Data science | "Model comparison" tab | Which model and threshold to use |

## Quick start

1. Download the dataset from Kaggle (`blastchar/telco-customer-churn`) into `data/raw/`
2. Install and run:

    pip install -r requirements.txt
    ./run_all.sh
    mlflow ui --backend-store-uri sqlite:///mlflow.db

On Windows without Git Bash, run the four scripts in `src/` in order, then `streamlit run dashboard/app.py`.

## Results

- 7,043 customers, 26.5% overall churn
- Best model by ROC-AUC: logistic regression (0.853)
- Recall at threshold 0.3: 92.2% (precision 42.3%); at 0.5: 84.0% (precision 52.3%)
- 9 MLflow runs (3 models x 3 thresholds)
- Expected revenue at risk: about $114,508/month (model estimate)
- 1,002 high-risk active customers worth $77,223/month
- 20% save rate would protect about $15,445/month (assumption, to be validated by an A/B test)

Full numbers: [docs/results.md](docs/results.md)

## Key findings

- Month-to-month contracts churn at 42.7%; two-year contracts at 2.8%
- Customers in their first 12 months churn at 47.4%
- Electronic check payers (45.3%) and fiber optic users (41.9%) churn more
- Short tenure, month-to-month contracts and fiber optic raise churn; long contracts lower it

## Screenshots

![MLflow runs](docs/screenshots/mlflow_runs.png)
![Who churns](docs/screenshots/dash_segments.png)
![Why they churn](docs/screenshots/dash_drivers.png)
![Model comparison](docs/screenshots/dash_models.png)
![Who to contact first](docs/screenshots/dash_risk.png)

## Business recommendations

See [docs/business_summary.md](docs/business_summary.md).

## Limitations

Public dataset, not a real company. The model predicts risk but does not prove that a retention offer works. Revenue at risk is an estimate, not a measured loss.
