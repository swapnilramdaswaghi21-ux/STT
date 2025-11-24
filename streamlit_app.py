import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

st.set_page_config(page_title="CRM AI Control Tower", layout="wide")

st.title("CRM-Native AI for Strategic Decision Making")
st.caption("Demo inspired by Salesforce Einstein 1 + Agentforce decision logic")

# ----------------------------
# Sidebar controls
# ----------------------------
st.sidebar.header("Controls")
retention_budget = st.sidebar.slider("Retention Budget (₹)", 0, 50000, 15000, step=1000)
cost_per_save = st.sidebar.slider("Estimated cost per retained customer (₹)", 500, 10000, 3000, step=500)

uploaded = st.sidebar.file_uploader("Upload CRM data (CSV)", type=["csv"])

# ----------------------------
# Load data
# ----------------------------
if uploaded:
    df = pd.read_csv(uploaded)
else:
    df = pd.read_csv("sample_customers.csv")

st.subheader("Customer 360 Dataset")
st.dataframe(df, use_container_width=True)

# ----------------------------
# FEATURE ENGINEERING (simple but strategic)
# ----------------------------
df_model = df.copy()

# normalize numeric features
num_cols = ["MonthlySpend", "TenureMonths", "SupportTicketsLast90d",
            "DiscountSensitivity", "DigitalEngagementScore", "LastPurchaseDays"]
scaler = MinMaxScaler()
df_model[num_cols] = scaler.fit_transform(df_model[num_cols])

# ----------------------------
# "Einstein-style" scoring (transparent formulas)
# ----------------------------
# churn risk rises with tickets, discount sensitivity, last purchase gap
# falls with tenure + engagement
df["ChurnRisk"] = (
    0.35*df_model["SupportTicketsLast90d"] +
    0.25*df_model["DiscountSensitivity"] +
    0.25*df_model["LastPurchaseDays"] +
    0.15*(1 - df_model["DigitalEngagementScore"])
)

# CLV proxy: spend × tenure × engagement
df["CLV"] = (
    (df["MonthlySpend"] * (df["TenureMonths"]/12)) *
    (0.5 + df_model["DigitalEngagementScore"])
)

# Growth / upsell potential: high engagement + spend but low plan tier
plan_weight = df["PlanType"].map({"Bronze":0.2, "Silver":0.4, "Gold":0.7, "Platinum":1.0})
df["UpsellPotential"] = (
    0.5*df_model["DigitalEngagementScore"] +
    0.3*df_model["MonthlySpend"] +
    0.2*(1 - plan_weight)
)

# ----------------------------
# Next Best Action logic (MECE strategic rules)
# ----------------------------
def nba(row):
    if row["ChurnRisk"] >= 0.65 and row["CLV"] >= df["CLV"].median():
        return "Retain Now (high value, high risk)"
    if row["ChurnRisk"] >= 0.65 and row["CLV"] < df["CLV"].median():
        return "Low-cost Nudge (high risk, low value)"
    if row["UpsellPotential"] >= df["UpsellPotential"].quantile(0.7) and row["ChurnRisk"] < 0.5:
        return "Upsell / Cross-sell"
    if row["SupportTicketsLast90d"] >= 3:
        return "Service Escalation"
    return "Monitor / No action"

df["NextBestAction"] = df.apply(nba, axis=1)

# ----------------------------
# Strategic decision table
# ----------------------------
st.subheader("Einstein-Style Strategic Scores")
st.dataframe(
    df[["CustomerID","Segment","ChurnRisk","CLV","UpsellPotential","NextBestAction"]]
    .sort_values(["ChurnRisk","CLV"], ascending=False),
    use_container_width=True
)

# ----------------------------
# VISUALS
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Churn Risk vs CLV (Strategic Portfolio View)")
    fig = plt.figure(figsize=(6,4))
    plt.scatter(df["ChurnRisk"], df["CLV"])
    for i, r in df.iterrows():
        plt.text(r["ChurnRisk"]+0.005, r["CLV"], r["CustomerID"], fontsize=8)
    plt.xlabel("Churn Risk")
    plt.ylabel("Customer Lifetime Value (proxy)")
    st.pyplot(fig)

with col2:
    st.markdown("### Distribution of Next-Best Actions")
    action_counts = df["NextBestAction"].value_counts()
    fig2 = plt.figure(figsize=(6,4))
    plt.bar(action_counts.index, action_counts.values)
    plt.xticks(rotation=25, ha="right")
    plt.ylabel("Number of customers")
    st.pyplot(fig2)

# ----------------------------
# BUDGET-CONSTRAINED RETENTION SIMULATION
# ----------------------------
st.subheader("Retention Budget Optimizer (Strategic Simulation)")

# candidates = high churn
candidates = df[df["ChurnRisk"] >= 0.65].copy()
candidates["ExpectedValueSaved"] = candidates["CLV"] * candidates["ChurnRisk"]

# rank by value saved per cost
candidates["ValuePerRupee"] = candidates["ExpectedValueSaved"] / cost_per_save
candidates = candidates.sort_values("ValuePerRupee", ascending=False)

max_saves = retention_budget // cost_per_save
to_save = candidates.head(int(max_saves))

st.write(f"With ₹{retention_budget:,} budget and ₹{cost_per_save:,} per save, you can target **{len(to_save)} customers**.")

st.dataframe(
    to_save[["CustomerID","ChurnRisk","CLV","ExpectedValueSaved","NextBestAction"]],
    use_container_width=True
)

st.markdown("**Decision Output:** Prioritize these customers for retention this cycle to maximize future value.")

# ----------------------------
# OPTIONAL SECTION: Einstein API plug-in
# ----------------------------
with st.expander("Optional: Connect to real Salesforce Einstein Prediction Service later"):
    st.write(
        "Einstein Prediction Service exposes REST APIs to score records programmatically. "
        "You can replace the scoring formulas above with live predictions once you have org credentials. "
        "Use Streamlit secrets for tokens; do not hardcode keys."
    )
    st.code("""
# pseudo-code:
import requests, streamlit as st

token = st.secrets["SF_TOKEN"]
endpoint = st.secrets["EINSTEIN_ENDPOINT"]

payload = {"records": df.to_dict(orient="records")}
preds = requests.post(endpoint, headers={"Authorization": f"Bearer {token}"}, json=payload).json()
df["ChurnRisk"] = [p["probability"] for p in preds]
""")
