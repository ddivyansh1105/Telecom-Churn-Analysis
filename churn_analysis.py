"""
Telecom Customer Churn Analysis
--------------------------------
Input : data/Telco_customer_churn.xlsx   (IBM Telco Customer Churn, Kaggle, 7,043 customers)
Output: data/telco_clean.csv     -> load this into MySQL (sql/churn_queries.sql)
        outputs/*.png            -> charts + one-page dashboard image
        outputs/key_numbers.txt  -> every number printed

Run:  python churn_analysis.py
"""
import json, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score

RAW = "data/Telco_customer_churn.xlsx"
CLEAN = "data/telco_clean.csv"
OUT = "outputs"
os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------ 1. LOAD + RENAME
df = pd.read_excel(RAW)
n_raw = len(df)
df = df.rename(columns={
    "CustomerID": "customerID", "Zip Code": "ZipCode", "Gender": "gender",
    "Senior Citizen": "SeniorCitizen", "Tenure Months": "tenure",
    "Phone Service": "PhoneService", "Multiple Lines": "MultipleLines",
    "Internet Service": "InternetService", "Online Security": "OnlineSecurity",
    "Online Backup": "OnlineBackup", "Device Protection": "DeviceProtection",
    "Tech Support": "TechSupport", "Streaming TV": "StreamingTV",
    "Streaming Movies": "StreamingMovies", "Paperless Billing": "PaperlessBilling",
    "Payment Method": "PaymentMethod", "Monthly Charges": "MonthlyCharges",
    "Total Charges": "TotalCharges", "Churn Label": "Churn",
    "Churn Score": "ChurnScore", "Churn Reason": "ChurnReason",
})
print(f"Loaded {n_raw:,} rows")

# ------------------------------------------------------------ 2. CLEAN
# TotalCharges is text in the source; brand-new customers (tenure 0) have a blank.
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
n_blank_total = int(df["TotalCharges"].isna().sum())
df["TotalCharges"] = df["TotalCharges"].fillna(0)

df["ChurnFlag"] = (df["Churn"] == "Yes").astype(int)

# "No internet service" / "No phone service" are really just "No"
for c in ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport",
          "StreamingTV", "StreamingMovies", "MultipleLines"]:
    df[c] = df[c].replace({"No internet service": "No", "No phone service": "No"})

df["TenureBand"] = pd.cut(df["tenure"], bins=[-1, 6, 12, 24, 48, 72],
                          labels=["0-6 mo", "7-12 mo", "13-24 mo", "25-48 mo", "49-72 mo"]).astype(str)
protect = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport"]
df["ProtectionServices"] = (df[protect] == "Yes").sum(axis=1)

cols = ["customerID", "City", "State", "ZipCode", "gender", "SeniorCitizen", "Partner",
        "Dependents", "tenure", "PhoneService", "MultipleLines", "InternetService",
        "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV",
        "StreamingMovies", "Contract", "PaperlessBilling", "PaymentMethod", "MonthlyCharges",
        "TotalCharges", "Churn", "ChurnFlag", "ChurnScore", "CLTV", "ChurnReason",
        "TenureBand", "ProtectionServices"]
df[cols].to_csv(CLEAN, index=False)
print(f"Saved cleaned data -> {CLEAN}")

# ------------------------------------------------------------ 3. NUMBERS
M = {}                                   # metrics for README
L = []                                   # lines for key_numbers.txt
overall = df["ChurnFlag"].mean() * 100
M["customers"] = n_raw
M["churned"] = int(df["ChurnFlag"].sum())
M["overall"] = round(overall, 1)
M["blank_total"] = n_blank_total
L += [f"Records analysed: {n_raw:,}", f"Churned customers: {M['churned']:,}",
      f"Blank TotalCharges fixed: {n_blank_total}", f"Overall churn rate: {overall:.1f}%"]


def rate_by(col):
    return (df.groupby(col, observed=True)["ChurnFlag"].mean() * 100).round(1)


for col in ["Contract", "TenureBand", "InternetService", "PaymentMethod", "TechSupport",
            "OnlineSecurity", "SeniorCitizen", "PaperlessBilling", "ProtectionServices"]:
    r = rate_by(col)
    M[col] = r.to_dict()
    L.append(f"\nChurn rate (%) by {col}:\n{r.to_string()}")

lost = df.loc[df.ChurnFlag == 1, "MonthlyCharges"].sum()
tot = df["MonthlyCharges"].sum()
M["lost_mrr"] = round(float(lost)); M["lost_pct"] = round(lost / tot * 100, 1)
L.append(f"\nMonthly revenue of churned customers: {lost:,.0f} ({lost / tot * 100:.1f}% of total)")

# customer value
cl = df.groupby("Churn")[["CLTV", "MonthlyCharges", "tenure"]].mean().round(1)
M["cltv_churn"] = round(float(cl.loc["Yes", "CLTV"])); M["cltv_stay"] = round(float(cl.loc["No", "CLTV"]))
M["mc_churn"] = float(cl.loc["Yes", "MonthlyCharges"]); M["mc_stay"] = float(cl.loc["No", "MonthlyCharges"])
M["ten_churn"] = float(cl.loc["Yes", "tenure"]); M["ten_stay"] = float(cl.loc["No", "tenure"])
L.append(f"\nAverages by churn:\n{cl.to_string()}")

# why customers say they left
reasons = df.loc[df.ChurnFlag == 1, "ChurnReason"].value_counts()
rpct = (reasons / reasons.sum() * 100).round(1)
M["reasons_top"] = rpct.head(8).to_dict()
M["reasons_n"] = reasons.head(8).to_dict()
comp = rpct[[i for i in rpct.index if i.startswith("Competitor")]].sum()
att = rpct[[i for i in rpct.index if i.startswith("Attitude")]].sum()
M["reason_competitor"] = round(float(comp), 1); M["reason_attitude"] = round(float(att), 1)
L.append(f"\nTop churn reasons (% of churners):\n{rpct.head(10).to_string()}")
L.append(f"Competitor-related total: {comp:.1f}% | Staff-attitude total: {att:.1f}%")

# cities
city = df.groupby("City").agg(n=("ChurnFlag", "size"), rate=("ChurnFlag", "mean"))
city = city[city.n >= 50].sort_values("rate", ascending=False)
city["rate"] = (city["rate"] * 100).round(1)
M["cities_top"] = {k: [int(v.n), float(v.rate)] for k, v in city.head(5).iterrows()}
L.append(f"\nCities with >=50 customers, highest churn:\n{city.head(8).to_string()}")

# high-risk segment
hr = df[(df.Contract == "Month-to-month") & (df.InternetService == "Fiber optic")
        & (df.TechSupport == "No") & (df.tenure <= 12)]
M["hr_n"] = len(hr); M["hr_rate"] = round(hr.ChurnFlag.mean() * 100, 1)
M["hr_lost"] = round(float(hr.loc[hr.ChurnFlag == 1, "MonthlyCharges"].sum()))
M["hr_share_churn"] = round(hr.ChurnFlag.sum() / df.ChurnFlag.sum() * 100, 1)
M["hr_share_lost"] = round(M["hr_lost"] / lost * 100, 1)
L.append(f"\nHigh-risk segment: {len(hr)} customers, churn {M['hr_rate']}%, "
         f"{M['hr_share_churn']}% of all churners, {M['hr_share_lost']}% of lost monthly revenue")

# ------------------------------------------------------------ 4. CHARTS
plt.rcParams.update({"figure.figsize": (7, 4), "axes.spines.top": False, "axes.spines.right": False})


def bar_chart(col, title, fname, rot=0):
    s = rate_by(col)
    fig, ax = plt.subplots()
    ax.bar(s.index.astype(str), s.values, color="#2b6cb0")
    ax.axhline(overall, color="grey", ls="--", lw=1)
    ax.text(len(s) - 0.5, overall + 0.8, f"overall {overall:.1f}%", ha="right", color="grey", fontsize=9)
    for i, v in enumerate(s.values):
        ax.text(i, v + 0.8, f"{v:.1f}%", ha="center", fontsize=9)
    ax.set_ylabel("Churn rate (%)"); ax.set_title(title)
    plt.xticks(rotation=rot); plt.tight_layout()
    fig.savefig(f"{OUT}/{fname}", dpi=150); plt.close(fig)


bar_chart("Contract", "Churn rate by contract type", "churn_by_contract.png")
df["TenureBand"] = pd.Categorical(df["TenureBand"], ["0-6 mo", "7-12 mo", "13-24 mo", "25-48 mo", "49-72 mo"], ordered=True)
bar_chart("TenureBand", "Churn rate by customer tenure", "churn_by_tenure.png")
bar_chart("InternetService", "Churn rate by internet service", "churn_by_internet.png")
bar_chart("PaymentMethod", "Churn rate by payment method", "churn_by_payment.png", rot=15)
bar_chart("TechSupport", "Churn rate by tech support", "churn_by_techsupport.png")

fig, ax = plt.subplots(figsize=(8, 4.5))
rp = rpct.head(8)[::-1]
ax.barh(rp.index, rp.values, color="#2b6cb0")
for i, v in enumerate(rp.values): ax.text(v + .3, i, f"{v:.1f}%", va="center", fontsize=9)
ax.set_title("Top reasons churned customers gave (% of churners)")
plt.tight_layout(); fig.savefig(f"{OUT}/churn_reasons.png", dpi=150); plt.close(fig)

# ------------------------------------------------------------ 5. MODEL
# Churn Score, CLTV and Churn Reason are NOT used as features: Churn Score is an
# IBM-calculated prediction and Churn Reason only exists for churners (data leakage).
feats = ["tenure", "MonthlyCharges", "SeniorCitizen", "Partner", "Dependents", "InternetService",
         "Contract", "PaperlessBilling", "PaymentMethod", "TechSupport", "OnlineSecurity",
         "StreamingTV", "StreamingMovies"]
X = pd.get_dummies(df[feats], drop_first=True).astype(float)
y = df["ChurnFlag"]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
sc = StandardScaler(); nc = ["tenure", "MonthlyCharges"]
Xtr[nc] = sc.fit_transform(Xtr[nc]); Xte[nc] = sc.transform(Xte[nc])
model = LogisticRegression(max_iter=1000, class_weight="balanced").fit(Xtr, ytr)
pred = model.predict(Xte); proba = model.predict_proba(Xte)[:, 1]
auc = roc_auc_score(yte, proba)
rep = classification_report(yte, pred, digits=3, output_dict=True)
M["auc"] = round(auc, 2); M["recall"] = round(rep["1"]["recall"] * 100); M["precision"] = round(rep["1"]["precision"] * 100)
L.append(f"\n--- Logistic regression (balanced) ---\nROC-AUC: {auc:.3f}\n" + classification_report(yte, pred, digits=3))

coef = pd.Series(model.coef_[0], index=X.columns).sort_values()
top = pd.concat([coef.head(7), coef.tail(7)])
fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(top.index, top.values, color=["#2f855a" if v < 0 else "#c53030" for v in top.values])
ax.set_title("What drives churn? (logistic regression coefficients)\nred = raises churn risk, green = lowers it")
plt.tight_layout(); fig.savefig(f"{OUT}/churn_drivers.png", dpi=150); plt.close(fig)
M["up"] = coef.tail(5).iloc[::-1].round(2).to_dict(); M["down"] = coef.head(5).round(2).to_dict()
L.append("Raise risk:\n" + coef.tail(5).iloc[::-1].round(3).to_string())
L.append("Lower risk:\n" + coef.head(5).round(3).to_string())

# ------------------------------------------------------------ 6. DASHBOARD IMAGE
fig, axes = plt.subplots(2, 3, figsize=(15, 8.5))
fig.suptitle("Telecom Customer Churn Dashboard  |  IBM Telco Customer Churn dataset (7,043 customers)", fontsize=12)
k = axes[0, 0]; k.axis("off")
for y0, big, small, col in [(.84, f"{n_raw:,}", "customers", "black"),
                            (.56, f"{overall:.1f}%", f"overall churn rate ({M['churned']:,} customers)", "#c53030"),
                            (.28, f"{M['lost_pct']:.1f}%", "of monthly revenue lost to churn", "#c53030")]:
    k.text(0, y0, big, fontsize=28, weight="bold", color=col); k.text(0, y0 - .09, small, color="grey")
for ax, col, ttl in [(axes[0, 1], "Contract", "By contract"), (axes[0, 2], "TenureBand", "By tenure"),
                     (axes[1, 0], "InternetService", "By internet service"),
                     (axes[1, 1], "PaymentMethod", "By payment method")]:
    s = rate_by(col)
    ax.bar(range(len(s)), s.values, color="#2b6cb0"); ax.set_xticks(range(len(s)))
    ax.set_xticklabels([str(i).replace(" (automatic)", " (auto)").replace("Electronic check", "E-check") for i in s.index], fontsize=7, rotation=12)
    ax.axhline(overall, color="grey", ls="--", lw=1)
    for i, v in enumerate(s.values): ax.text(i, v + .6, f"{v:.0f}%", ha="center", fontsize=8)
    ax.set_title(ttl + " (churn %)", fontsize=10)
rp = rpct.head(6)[::-1]
axes[1, 2].barh([i for i in rp.index], rp.values, color="#2b6cb0")
for i, v in enumerate(rp.values): axes[1, 2].text(v + .2, i, f"{v:.0f}%", va="center", fontsize=8)
axes[1, 2].set_title("Top churn reasons (% of churners)", fontsize=10); axes[1, 2].tick_params(labelsize=7)
for a in axes.flat: a.spines[["top", "right"]].set_visible(False)
plt.tight_layout(rect=[0, 0, 1, .95]); fig.savefig(f"{OUT}/dashboard_overview.png", dpi=140); plt.close(fig)

# ------------------------------------------------------------ 7. SAVE
open(f"{OUT}/key_numbers.txt", "w").write("\n".join(L))
print("\n".join(L))
