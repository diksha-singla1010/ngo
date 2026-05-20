import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DONOR_FILE
def load():
    df = pd.read_csv(DONOR_FILE, encoding="utf-8-sig")
    df["amount_cr"]  = pd.to_numeric(df["amount_cr"],  errors="coerce").fillna(0)
    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce").fillna(0)
    df["beneficiaries"] = pd.to_numeric(df["beneficiaries"], errors="coerce").fillna(0)
    return df
def get_donor_kpis():
    df = load()
    total   = len(df)
    active  = int((df["is_active_donor"] == "Yes").sum())
    total_cr = df["amount_cr"].sum()
    avg_cr   = df["amount_cr"].mean()
    states   = df["state"].nunique()
    sectors  = df["sector_focus"].nunique()
    corporate= int((df["donor_type"] == "Corporate").sum())
    trust    = int((df["donor_type"] == "Trust/Foundation").sum())
    retention= round(active / total * 100, 1)
    churn    = round((total - active) / total * 100, 1)
    return {
        "total_donors":     total,
        "active_donors":    active,
        "inactive_donors":  total - active,
        "total_funds_cr":   round(total_cr, 2),
        "avg_donation_cr":  round(avg_cr, 2),
        "retention_rate":   retention,
        "churn_rate":       churn,
        "states_covered":   states,
        "sectors_covered":  sectors,
        "corporate_donors": corporate,
        "trust_donors":     trust,
    }
def get_top_donors(n=10):
    df = load()
    return df.nlargest(n, "amount_cr")[
        ["donor_name","donor_type","state","sector_focus",
         "amount_cr","financial_year","payment_mode","is_active_donor"]
    ].reset_index(drop=True)
def get_sector_funding():
    """Q1 — Which NGO sector receives the most CSR funding?"""
    df = load()
    return df.groupby("sector_focus").agg(
        donors=("donor_id","count"),
        total_cr=("amount_cr","sum"),
        avg_cr  =("amount_cr","mean"),
        active  =("is_active_flag","sum"),
    ).reset_index().sort_values("total_cr", ascending=False)
def get_state_funding():
    df = load()
    return df.groupby("state").agg(
        donors=("donor_id","count"),
        total_cr=("amount_cr","sum"),
        active  =("is_active_flag","sum"),
    ).reset_index().sort_values("total_cr", ascending=False)
def get_year_wise_trend():
    df = load()
    return df.groupby("financial_year").agg(
        donors=("donor_id","count"),
        total_cr=("amount_cr","sum"),
        active  =("is_active_flag","sum"),
    ).reset_index().sort_values("financial_year")
def get_payment_mode_analysis():
    """Q10 — Which payment modes correlate with retention?"""
    df = load()
    pm = df.groupby("payment_mode").agg(
        count=("donor_id","count"),
        total_cr=("amount_cr","sum"),
        active=("is_active_flag","sum"),
    ).reset_index()
    pm["retention_rate"] = (pm["active"] / pm["count"] * 100).round(1)
    return pm.sort_values("retention_rate", ascending=False)
def get_donor_type_analysis():
    df = load()
    dt = df.groupby("donor_type").agg(
        count=("donor_id","count"),
        total_cr=("amount_cr","sum"),
        avg_cr  =("amount_cr","mean"),
        active  =("is_active_flag","sum"),
    ).reset_index()
    dt["retention_rate"] = (dt["active"] / dt["count"] * 100).round(1)
    return dt.sort_values("total_cr", ascending=False)
def get_engagement_scores():
    """Engagement = amount(50%) + active(30%) + fcra(20%)"""
    df = load()
    max_amt = df["amount_cr"].max() if df["amount_cr"].max() > 0 else 1
    df["score"] = (
        (df["amount_cr"] / max_amt * 50) +
        ((df["is_active_donor"] == "Yes").astype(int) * 30) +
        ((df["fcra_compliant"] == "Yes").astype(int) * 20)
    ).round(2)
    return df[["donor_name","donor_type","state","sector_focus",
               "amount_cr","is_active_donor","score"]].sort_values(
                   "score", ascending=False)
def get_full_table():
    df = load()
    return df[["donor_id","donor_name","donor_type","state","sector_focus",
               "amount_cr","financial_year","payment_mode",
               "fcra_compliant","is_active_donor","amount_category"]]
def get_churn_risk_table():
    df = load()
    return df[df["is_active_donor"] == "No"].sort_values("amount_cr", ascending=False)[
        ["donor_name","donor_type","state","sector_focus","amount_cr","financial_year"]
    ]
