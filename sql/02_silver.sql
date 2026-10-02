-- SILVER: typed, deduplicated, snake_case columns
CREATE OR REPLACE TABLE silver.telco_clean AS
SELECT
  customerID                       AS customer_id,
  gender,
  CAST(SeniorCitizen AS INTEGER)   AS senior_citizen,
  Partner                          AS partner,
  Dependents                       AS dependents,
  CAST(tenure AS INTEGER)          AS tenure,
  PhoneService                     AS phone_service,
  MultipleLines                    AS multiple_lines,
  InternetService                  AS internet_service,
  OnlineSecurity                   AS online_security,
  OnlineBackup                     AS online_backup,
  DeviceProtection                 AS device_protection,
  TechSupport                      AS tech_support,
  StreamingTV                      AS streaming_tv,
  StreamingMovies                  AS streaming_movies,
  Contract                         AS contract,
  PaperlessBilling                 AS paperless_billing,
  PaymentMethod                    AS payment_method,
  CAST(MonthlyCharges AS DOUBLE)   AS monthly_charges,
  COALESCE(TRY_CAST(NULLIF(TRIM(TotalCharges), '') AS DOUBLE), 0) AS total_charges,
  CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END AS churn_flag
FROM (SELECT DISTINCT * EXCLUDE (_ingested_at) FROM bronze.telco_raw);