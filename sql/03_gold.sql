-- GOLD: analytics-ready tables
CREATE OR REPLACE TABLE gold.churn_features AS
SELECT *,
  CASE WHEN tenure <= 12 THEN '0-12 mo'
       WHEN tenure <= 24 THEN '13-24 mo'
       WHEN tenure <= 48 THEN '25-48 mo'
       ELSE '49+ mo' END AS tenure_group
FROM silver.telco_clean;

CREATE OR REPLACE TABLE gold.churn_by_segment AS
SELECT 'contract' AS dimension, contract AS segment, COUNT(*) AS customers,
       SUM(churn_flag) AS churned, ROUND(AVG(churn_flag) * 100, 1) AS churn_rate_pct,
       ROUND(SUM(CASE WHEN churn_flag = 1 THEN monthly_charges ELSE 0 END), 0) AS monthly_revenue_lost
FROM gold.churn_features GROUP BY contract
UNION ALL
SELECT 'internet_service', internet_service, COUNT(*), SUM(churn_flag),
       ROUND(AVG(churn_flag) * 100, 1),
       ROUND(SUM(CASE WHEN churn_flag = 1 THEN monthly_charges ELSE 0 END), 0)
FROM gold.churn_features GROUP BY internet_service
UNION ALL
SELECT 'payment_method', payment_method, COUNT(*), SUM(churn_flag),
       ROUND(AVG(churn_flag) * 100, 1),
       ROUND(SUM(CASE WHEN churn_flag = 1 THEN monthly_charges ELSE 0 END), 0)
FROM gold.churn_features GROUP BY payment_method
UNION ALL
SELECT 'tenure_group', tenure_group, COUNT(*), SUM(churn_flag),
       ROUND(AVG(churn_flag) * 100, 1),
       ROUND(SUM(CASE WHEN churn_flag = 1 THEN monthly_charges ELSE 0 END), 0)
FROM gold.churn_features GROUP BY tenure_group
UNION ALL
SELECT 'paperless_billing', paperless_billing, COUNT(*), SUM(churn_flag),
       ROUND(AVG(churn_flag) * 100, 1),
       ROUND(SUM(CASE WHEN churn_flag = 1 THEN monthly_charges ELSE 0 END), 0)
FROM gold.churn_features GROUP BY paperless_billing
UNION ALL
SELECT 'senior_citizen', CAST(senior_citizen AS VARCHAR), COUNT(*), SUM(churn_flag),
       ROUND(AVG(churn_flag) * 100, 1),
       ROUND(SUM(CASE WHEN churn_flag = 1 THEN monthly_charges ELSE 0 END), 0)
FROM gold.churn_features GROUP BY senior_citizen;