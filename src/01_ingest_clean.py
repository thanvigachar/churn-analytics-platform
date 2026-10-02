"""Bronze + silver layers: load raw Kaggle CSV into DuckDB, then clean and type it."""
from utils import get_con, run_sql_file

con = get_con()
run_sql_file(con, "sql/01_bronze.sql")
run_sql_file(con, "sql/02_silver.sql")

n_raw = con.execute("SELECT COUNT(*) FROM bronze.telco_raw").fetchone()[0]
n_clean = con.execute("SELECT COUNT(*) FROM silver.telco_clean").fetchone()[0]
null_ids = con.execute("SELECT COUNT(*) FROM silver.telco_clean WHERE customer_id IS NULL").fetchone()[0]
dupes = con.execute("SELECT COUNT(*) - COUNT(DISTINCT customer_id) FROM silver.telco_clean").fetchone()[0]
null_tc = con.execute("SELECT COUNT(*) FROM silver.telco_clean WHERE total_charges IS NULL").fetchone()[0]

assert null_ids == 0, "null customer ids found"
assert dupes == 0, "duplicate customer ids found"
assert null_tc == 0, "null total_charges remain"
print(f"bronze rows: {n_raw} | silver rows: {n_clean} | null ids: {null_ids} | duplicates: {dupes}")