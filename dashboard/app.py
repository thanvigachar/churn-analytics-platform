# """Streamlit + Plotly dashboard reading directly from the DuckDB gold layer."""
# import duckdb
# import pandas as pd
# import plotly.express as px
# import streamlit as st

# st.set_page_config(page_title="Churn Analytics Platform", page_icon="📉", layout="wide")
# DB = "data/warehouse.duckdb"


# @st.cache_data
# def q(sql: str) -> pd.DataFrame:
#     con = duckdb.connect(DB, read_only=True)
#     try:
#         return con.execute(sql).df()
#     finally:
#         con.close()


# feat = q("SELECT customer_id, contract, internet_service, monthly_charges, churn_flag FROM gold.churn_features")
# seg = q("SELECT * FROM gold.churn_by_segment")
# drv = q("SELECT * FROM gold.churn_drivers")
# risk = q("SELECT * FROM gold.customer_risk")
# models = q("SELECT * FROM gold.model_results")

# # ---------- Sidebar filters ----------
# st.sidebar.header("Filters")
# contracts = st.sidebar.multiselect("Contract", sorted(feat.contract.unique()),
#                                    default=sorted(feat.contract.unique()))
# internet = st.sidebar.multiselect("Internet service", sorted(feat.internet_service.unique()),
#                                   default=sorted(feat.internet_service.unique()))
# save_rate = st.sidebar.slider("Assumed save rate for high-risk customers", 0, 100, 20) / 100

# f = feat[feat.contract.isin(contracts) & feat.internet_service.isin(internet)]
# r = risk[risk.contract.isin(contracts) & risk.internet_service.isin(internet)]
# high = r[r.risk_band == "High"]

# # ---------- Header and KPIs ----------
# st.title("📉 Customer Churn Analytics Platform")
# st.caption("Pipeline: Kaggle CSV → DuckDB (bronze → silver → gold) → scikit-learn + MLflow → this dashboard")

# k1, k2, k3, k4, k5 = st.columns(5)
# k1.metric("Customers", f"{len(f):,}")
# k2.metric("Churn rate", f"{f.churn_flag.mean() * 100:.1f}%" if len(f) else "n/a")
# k3.metric("Monthly revenue lost to churn", f"${f.loc[f.churn_flag == 1, 'monthly_charges'].sum():,.0f}")
# k4.metric("Revenue at risk / month", f"${(r.monthly_charges * r.churn_probability).sum():,.0f}")
# k5.metric("High-risk customers", f"{len(high):,}")
# st.info(f"At a {save_rate:.0%} save rate, retaining high-risk customers would protect about "
#         f"**${high.monthly_charges.sum() * save_rate:,.0f}/month** "
#         f"(assumption controlled by the sidebar slider, not a measured result).")

# tab1, tab2, tab3, tab4 = st.tabs(["Churn by segment", "Churn drivers", "Model comparison", "At-risk customers"])

# with tab1:
#     dim = st.selectbox("Segment dimension", sorted(seg.dimension.unique()))
#     s = seg[seg.dimension == dim].sort_values("churn_rate_pct")
#     c1, c2 = st.columns(2)
#     c1.plotly_chart(px.bar(s, x="churn_rate_pct", y="segment", orientation="h", text="churn_rate_pct",
#                            color="churn_rate_pct", color_continuous_scale="Reds",
#                            title=f"Churn rate (%) by {dim}"), use_container_width=True)
#     c2.plotly_chart(px.bar(s, x="monthly_revenue_lost", y="segment", orientation="h",
#                            text="monthly_revenue_lost", title=f"Monthly revenue lost ($) by {dim}"),
#                     use_container_width=True)

# with tab2:
#     top = drv.head(10).sort_values("importance")
#     st.plotly_chart(px.bar(top, x="importance", y="feature", orientation="h",
#                            title="Top 10 churn drivers (best model)"), use_container_width=True)

# with tab3:
#     st.dataframe(models, use_container_width=True)
#     c1, c2 = st.columns(2)
#     c1.plotly_chart(px.line(models, x="threshold", y="recall", color="model", markers=True,
#                             title="Recall by decision threshold"), use_container_width=True)
#     c2.plotly_chart(px.bar(models.drop_duplicates("model"), x="model", y="roc_auc",
#                            text="roc_auc", title="ROC-AUC by model"), use_container_width=True)
#     st.caption("Lower thresholds catch more churners (higher recall) at the cost of more false alarms.")

# with tab4:
#     c1, c2 = st.columns(2)
#     c1.plotly_chart(px.pie(r, names="risk_band", hole=0.5, title="Active customers by risk band"),
#                     use_container_width=True)
#     band = r.groupby("risk_band", as_index=False).monthly_charges.sum()
#     c2.plotly_chart(px.bar(band, x="risk_band", y="monthly_charges", title="Monthly revenue by risk band"),
#                     use_container_width=True)
#     top20 = high.sort_values("monthly_charges", ascending=False).head(20).round(2)
#     st.subheader("Top 20 high-risk customers by monthly charges")
#     st.dataframe(top20, use_container_width=True)
#     st.download_button("Download all high-risk customers (CSV)",
#                        high.round(3).to_csv(index=False), "high_risk_customers.csv", "text/csv")
"""Streamlit + Plotly dashboard reading directly from the DuckDB gold layer."""
import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Churn Analytics Platform", page_icon="📉", layout="wide")
DB = "data/warehouse.duckdb"


@st.cache_data
def q(sql: str) -> pd.DataFrame:
    con = duckdb.connect(DB, read_only=True)
    try:
        return con.execute(sql).df()
    finally:
        con.close()


feat = q("SELECT customer_id, contract, internet_service, monthly_charges, churn_flag FROM gold.churn_features")
seg = q("SELECT * FROM gold.churn_by_segment")
drv = q("SELECT * FROM gold.churn_drivers_signed")
risk = q("SELECT * FROM gold.customer_risk")
models = q("SELECT * FROM gold.model_results")

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
contracts = st.sidebar.multiselect("Contract", sorted(feat.contract.unique()),
                                   default=sorted(feat.contract.unique()))
internet = st.sidebar.multiselect("Internet service", sorted(feat.internet_service.unique()),
                                  default=sorted(feat.internet_service.unique()))
save_rate = st.sidebar.slider("Assumed save rate for high-risk customers", 0, 100, 20) / 100

f = feat[feat.contract.isin(contracts) & feat.internet_service.isin(internet)]
r = risk[risk.contract.isin(contracts) & risk.internet_service.isin(internet)]
high = r[r.risk_band == "High"]

# ---------- Header, takeaway and KPIs ----------
st.title("📉 Customer Churn Analytics Platform")
st.caption("Pipeline: Kaggle CSV → DuckDB (bronze → silver → gold) → scikit-learn + MLflow → this dashboard")

worst = seg.sort_values("churn_rate_pct", ascending=False).iloc[0]
st.success(f"Biggest hotspot: **{worst.dimension} = {worst.segment}** churns at "
           f"**{worst.churn_rate_pct}%**, losing ${worst.monthly_revenue_lost:,.0f}/month.")
st.caption("Filters apply to the KPI cards and the 'Who to contact first' tab. Other tabs show the full dataset.")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Customers", f"{len(f):,}")
k2.metric("Churn rate", f"{f.churn_flag.mean() * 100:.1f}%" if len(f) else "n/a")
k3.metric("Monthly revenue already lost",
          f"${f.loc[f.churn_flag == 1, 'monthly_charges'].sum():,.0f}",
          help="Monthly charges of customers who have already churned.")
k4.metric("Revenue at risk / month (estimate)",
          f"${(r.monthly_charges * r.churn_probability).sum():,.0f}",
          help="Model estimate for current customers: monthly charge x predicted churn probability. "
               "Not a measured loss.")
k5.metric("High-risk customers", f"{len(high):,}",
          help="Active customers with predicted churn probability above 60%.")

st.info(f"At a {save_rate:.0%} save rate, retaining high-risk customers would protect about "
        f"**${high.monthly_charges.sum() * save_rate:,.0f}/month** "
        f"(assumption controlled by the sidebar slider, not a measured result).")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Who churns", "Why they churn", "Model comparison", "Who to contact first"])

# ---------- Tab 1: who churns ----------
with tab1:
    dim = st.selectbox("Segment dimension", sorted(seg.dimension.unique()))
    s = seg[seg.dimension == dim].sort_values("churn_rate_pct")
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.bar(s, x="churn_rate_pct", y="segment", orientation="h", text="churn_rate_pct",
                           color="churn_rate_pct", color_continuous_scale="Reds",
                           title=f"Churn rate (%) by {dim}"), use_container_width=True)
    c2.plotly_chart(px.bar(s, x="monthly_revenue_lost", y="segment", orientation="h",
                           text="monthly_revenue_lost",
                           title=f"Monthly revenue lost ($) by {dim}"), use_container_width=True)

# ---------- Tab 2: why they churn (signed drivers) ----------
with tab2:
    top = drv.head(10).sort_values("strength")
    fig = px.bar(top, x="coefficient", y="feature", orientation="h", color="direction",
                 color_discrete_map={"Increases churn": "#e5484d", "Reduces churn": "#30a46c"},
                 title="Top 10 factors: what pushes customers to leave or stay")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Red bars raise the chance a customer leaves; green bars lower it. "
               "Longer bar = stronger effect.")

# ---------- Tab 3: model comparison ----------
with tab3:
    st.dataframe(models, use_container_width=True)
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.line(models, x="threshold", y="recall", color="model", markers=True,
                            title="Recall by decision threshold"), use_container_width=True)
    fig_auc = px.bar(models.drop_duplicates("model"), x="model", y="roc_auc", text="roc_auc",
                     title="ROC-AUC by model (axis zoomed to 0.80-0.90)")
    fig_auc.update_yaxes(range=[0.80, 0.90])
    c2.plotly_chart(fig_auc, use_container_width=True)

    best_model = models.sort_values("roc_auc", ascending=False).iloc[0]["model"]
    bm = models[models.model == best_model].set_index("threshold")
    st.success(f"{best_model.replace('_', ' ').title()} ranks customers best. At a 0.3 threshold it catches "
               f"about {bm.loc[0.3, 'recall']:.0%} of churners but flags more false alarms; "
               f"at 0.5 it catches {bm.loc[0.5, 'recall']:.0%} with fewer.")
    st.caption("Lower thresholds catch more churners (higher recall) at the cost of more false alarms.")

# ---------- Tab 4: who to contact first ----------
with tab4:
    order = ["Low", "Medium", "High"]
    colors = {"Low": "#30a46c", "Medium": "#f5a524", "High": "#e5484d"}
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.pie(r, names="risk_band", hole=0.5, color="risk_band",
                           color_discrete_map=colors, category_orders={"risk_band": order},
                           title="Active customers by risk band"), use_container_width=True)
    band = r.groupby("risk_band", as_index=False).monthly_charges.sum()
    c2.plotly_chart(px.bar(band, x="risk_band", y="monthly_charges", color="risk_band",
                           color_discrete_map=colors, category_orders={"risk_band": order},
                           title="Monthly revenue by risk band"), use_container_width=True)

    top20 = high.sort_values("monthly_charges", ascending=False).head(20).round(2)
    st.subheader("Top 20 high-risk customers by monthly charges")
    st.dataframe(top20, use_container_width=True)
    st.download_button("Download all high-risk customers (CSV)",
                       high.round(3).to_csv(index=False), "high_risk_customers.csv", "text/csv")