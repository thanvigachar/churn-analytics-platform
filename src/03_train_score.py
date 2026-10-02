"""Train 3 models, evaluate at 3 thresholds (9 MLflow runs), extract drivers, score active customers."""
import os
import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from utils import get_con

con = get_con()
df = con.execute("SELECT * FROM gold.churn_features").df()
df["senior_citizen"] = df["senior_citizen"].astype(str)   # treat as categorical

drop_cols = ["customer_id", "churn_flag"]
X, y = df.drop(columns=drop_cols), df["churn_flag"]
num_cols = ["tenure", "monthly_charges", "total_charges"]
cat_cols = [c for c in X.columns if c not in num_cols]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42)

pre = ColumnTransformer([
    ("num", StandardScaler(), num_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
])

models = {
    "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "random_forest": RandomForestClassifier(n_estimators=300, max_depth=8,
                                            class_weight="balanced", random_state=42),
    "gradient_boosting": GradientBoostingClassifier(random_state=42),
}
THRESHOLDS = (0.3, 0.4, 0.5)

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("churn_prediction")

fitted, rows = {}, []
for name, clf in models.items():
    pipe = Pipeline([("pre", pre), ("clf", clf)]).fit(X_train, y_train)
    fitted[name] = pipe
    proba = pipe.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, proba)
    for thr in THRESHOLDS:
        pred = (proba >= thr).astype(int)
        m = {"model": name, "threshold": thr,
             "recall": recall_score(y_test, pred),
             "precision": precision_score(y_test, pred),
             "f1": f1_score(y_test, pred),
             "roc_auc": auc}
        rows.append(m)
        with mlflow.start_run(run_name=f"{name}_thr{thr}"):
            mlflow.log_params({"model": name, "threshold": thr})
            mlflow.log_metrics({k: v for k, v in m.items() if k not in ("model", "threshold")})
            if thr == 0.5:
                mlflow.sklearn.log_model(
                    pipe,
                    name="model",
                    skops_trusted_types=["sklearn.tree._tree.Tree"],
        )

results = pd.DataFrame(rows).round(3)
print(results.to_string(index=False))

# Best model by ROC-AUC
best_name = results.sort_values("roc_auc", ascending=False).iloc[0]["model"]
best = fitted[best_name]
print("Best model by ROC-AUC:", best_name)
os.makedirs("models", exist_ok=True)
joblib.dump(best, "models/best_model.joblib")

# Churn drivers
names = best.named_steps["pre"].get_feature_names_out()
clf = best.named_steps["clf"]
imp = clf.feature_importances_ if hasattr(clf, "feature_importances_") else np.abs(clf.coef_[0])
drivers = (pd.DataFrame({"feature": names, "importance": imp})
           .sort_values("importance", ascending=False))
drivers["feature"] = drivers["feature"].str.replace(r"^(num|cat)__", "", regex=True)

# Score active customers -> risk bands and revenue at risk
active = df[df["churn_flag"] == 0].copy()
active["churn_probability"] = best.predict_proba(active.drop(columns=drop_cols))[:, 1]
active["risk_band"] = pd.cut(active["churn_probability"], [0, 0.3, 0.6, 1.0],
                             labels=["Low", "Medium", "High"], include_lowest=True).astype(str)
risk = active[["customer_id", "contract", "internet_service", "payment_method",
               "tenure_group", "monthly_charges", "churn_probability", "risk_band"]]

# Save to gold layer
for tbl, frame in (("model_results", results), ("churn_drivers", drivers), ("customer_risk", risk)):
    con.register("tmp_df", frame)
    con.execute(f"CREATE OR REPLACE TABLE gold.{tbl} AS SELECT * FROM tmp_df")
    con.unregister("tmp_df")

# Headline numbers
rev_at_risk = float((risk.monthly_charges * risk.churn_probability).sum())
high = risk[risk.risk_band == "High"]
high_rev = float(high.monthly_charges.sum())
best_row = results[results.model == best_name].sort_values("recall", ascending=False).iloc[0]
overall_churn = float(df.churn_flag.mean() * 100)

print(f"Expected monthly revenue at risk: ${rev_at_risk:,.0f}")
print(f"High-risk customers: {len(high)} (${high_rev:,.0f}/month)")

os.makedirs("docs", exist_ok=True)
with open("docs/results.md", "w") as f:
    f.write(f"""# Results (auto-generated)

- Customer records: {len(df):,}
- Overall churn rate: {overall_churn:.1f}%
- Best model (ROC-AUC): {best_name} ({best_row.roc_auc})
- Recall at threshold {best_row.threshold}: {best_row.recall:.1%} (precision {best_row.precision:.1%})
- Expected monthly revenue at risk: ${rev_at_risk:,.0f}
- High-risk active customers: {len(high)} (${high_rev:,.0f}/month)
- Estimated impact at 20% save rate: ${0.2 * high_rev:,.0f}/month (assumption, not a measured result)

## Model comparison
{results.to_markdown(index=False) if hasattr(results, 'to_markdown') else results.to_string(index=False)}
""")
print("Wrote docs/results.md")