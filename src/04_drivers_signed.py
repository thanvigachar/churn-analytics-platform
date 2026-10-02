"""Signed churn drivers: shows whether each factor raises or lowers churn risk."""
import joblib
import numpy as np
import pandas as pd
from utils import get_con

best = joblib.load("models/best_model.joblib")
names = best.named_steps["pre"].get_feature_names_out()
clf = best.named_steps["clf"]

if hasattr(clf, "coef_"):                      # logistic regression: sign = direction
    coef = clf.coef_[0]
else:                                          # tree models have no sign; fall back to importance
    coef = clf.feature_importances_

df = pd.DataFrame({
    "feature": pd.Series(names).str.replace(r"^(num|cat)__", "", regex=True),
    "coefficient": coef,
})
df["strength"] = df.coefficient.abs()
df["direction"] = np.where(df.coefficient > 0, "Increases churn", "Reduces churn")
df = df.sort_values("strength", ascending=False)

con = get_con()
con.register("t", df)
con.execute("CREATE OR REPLACE TABLE gold.churn_drivers_signed AS SELECT * FROM t")
print(df.head(10).to_string(index=False))