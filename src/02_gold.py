"""Gold layer: feature table and churn-by-segment table."""
from utils import get_con, run_sql_file

con = get_con()
run_sql_file(con, "sql/03_gold.sql")

print(con.execute("""
    SELECT dimension, segment, customers, churn_rate_pct, monthly_revenue_lost
    FROM gold.churn_by_segment ORDER BY churn_rate_pct DESC LIMIT 8
""").df().to_string(index=False))
print("Overall churn rate %:",
      con.execute("SELECT ROUND(AVG(churn_flag) * 100, 1) FROM gold.churn_features").fetchone()[0])