import os, duckdb, mlflow
from streamlit.testing.v1 import AppTest

ok = True
def check(name, cond, detail=""):
    global ok
    print(("PASS  " if cond else "FAIL  ") + name + (f"  ({detail})" if detail else ""))
    ok = ok and bool(cond)

# --- Files ---
for f in ["sql/01_bronze.sql","sql/02_silver.sql","sql/03_gold.sql","src/utils.py",
          "src/01_ingest_clean.py","src/02_gold.py","src/03_train_score.py",
          "src/04_drivers_signed.py","dashboard/app.py","run_all.sh","requirements.txt",
          "README.md","docs/results.md","docs/business_summary.md","models/best_model.joblib"]:
    check(f"file {f}", os.path.exists(f))

for f in ["README.md", "docs/business_summary.md"]:
    check(f"{f} is not empty", os.path.exists(f) and os.path.getsize(f) > 200)

sh = open("run_all.sh", encoding="utf-8").read() if os.path.exists("run_all.sh") else ""
check("run_all.sh has no stray backticks", "`" not in sh)
check("run_all.sh calls all 4 scripts", all(s in sh for s in
      ["01_ingest_clean", "02_gold", "03_train_score", "04_drivers_signed"]))

shots = os.listdir("docs/screenshots") if os.path.isdir("docs/screenshots") else []
check("screenshots saved (5 expected)", len(shots) >= 5, f"{len(shots)} found")

# --- Database ---
c = duckdb.connect("data/warehouse.duckdb", read_only=True)
tables = {f"{s}.{t}" for s, t in c.execute(
    "select table_schema, table_name from information_schema.tables "
    "where table_schema in ('bronze','silver','gold')").fetchall()}
for t in ["bronze.telco_raw","silver.telco_clean","gold.churn_features","gold.churn_by_segment",
          "gold.churn_drivers","gold.churn_drivers_signed","gold.customer_risk","gold.model_results"]:
    check(f"table {t}", t in tables)

check("bronze rows = 7043", c.execute("select count(*) from bronze.telco_raw").fetchone()[0] == 7043)
check("silver rows = 7043", c.execute("select count(*) from silver.telco_clean").fetchone()[0] == 7043)
check("no null total_charges", c.execute("select count(*) from silver.telco_clean where total_charges is null").fetchone()[0] == 0)
check("no duplicate customers", c.execute("select count(*)-count(distinct customer_id) from silver.telco_clean").fetchone()[0] == 0)
check("model_results has 9 rows", c.execute("select count(*) from gold.model_results").fetchone()[0] == 9)
check("customer_risk has active customers (5174)", c.execute("select count(*) from gold.customer_risk").fetchone()[0] == 5174)
rate = c.execute("select round(avg(churn_flag)*100,1) from gold.churn_features").fetchone()[0]
check("churn rate = 26.5%", rate == 26.5, f"{rate}%")
dirs = {r[0] for r in c.execute("select distinct direction from gold.churn_drivers_signed").fetchall()}
check("drivers have both directions", dirs == {"Increases churn", "Reduces churn"}, str(dirs))
c.close()

# --- MLflow ---
mlflow.set_tracking_uri("sqlite:///mlflow.db")
n = len(mlflow.search_runs(experiment_names=["churn_prediction"]))
check("MLflow runs = 9", n == 9, f"{n} runs")

# --- Dashboard loads without errors ---
at = AppTest.from_file("dashboard/app.py", default_timeout=90).run()
check("dashboard runs without exceptions", len(at.exception) == 0,
      "; ".join(str(e.value) for e in at.exception))
check("dashboard has 4 tabs", len(at.tabs) == 4, f"{len(at.tabs)} found")
metrics = {m.label: m.value for m in at.metric}
check("dashboard shows 7,043 customers", metrics.get("Customers") == "7,043", str(metrics.get("Customers")))
check("dashboard shows 26.5% churn", metrics.get("Churn rate") == "26.5%", str(metrics.get("Churn rate")))

print("\nALL CHECKS PASSED" if ok else "\nSOME CHECKS FAILED - fix the FAIL lines above")
