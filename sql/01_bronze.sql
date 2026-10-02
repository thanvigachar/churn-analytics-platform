-- BRONZE: raw data, everything as text, untouched
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

CREATE OR REPLACE TABLE bronze.telco_raw AS
SELECT *, current_timestamp AS _ingested_at
FROM read_csv_auto('data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv',
                   header = true, all_varchar = true);