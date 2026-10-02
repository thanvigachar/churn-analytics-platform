@"
#!/usr/bin/env bash
set -euo pipefail
cd "`$(dirname "`$0")"

CSV="data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv"
if [ ! -f "`$CSV" ]; then
  kaggle datasets download -d blastchar/telco-customer-churn -p data/raw --unzip
fi

echo "[1/4] Bronze + silver layers";        python src/01_ingest_clean.py
echo "[2/4] Gold layer";                    python src/02_gold.py
echo "[3/] Train, track (MLflow), score";  python src/03_train_score.py
echo "[4/4] Signed churn drivers";          python src/04_drivers_signed.py

if [ "`${1:-}" != "--no-dashboard" ]; then
  echo "Launching dashboard at http://localhost:8501"
  streamlit run dashboard/app.py
fi
"@ | Set-Content -Encoding ascii run_all.sh