import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BENEFICIARY_FILE, PROGRAM_FILE
def load():
    ben  = pd.read_csv(BENEFICIARY_FILE, encoding="utf-8-sig")
    prog = pd.read_csv(PROGRAM_FILE, encoding="utf-8-sig")
    prog["budget_inr"] = pd.to_numeric(prog["budget_inr"], errors="coerce").fillna(0)
    return ben, prog
def get_beneficiary_kpis():
    ben, _ = load()
    total     = len(ben)
    active    = int((ben["enrollment_status"] == "Active").sum())
    completed = int((ben["enrollment_status"] == "Completed").sum())
    dropped   = int((ben["enrollment_status"] == "Dropped").sum())
    female    = int((ben["gender"] == "Female").sum())
    male      = int((ben["gender"] == "Male").sum())
    bpl       = int((ben["bpl_status"] == "Yes").sum())
    avg_age   = round(ben["age"].mean(), 1)
    success   = round(completed / total * 100, 1)
    return {
        "total": total, "active": active, "completed": completed,
        "dropped": dropped, "female": female, "male": male,
        "bpl": bpl, "avg_age": avg_age, "success_rate": success,
        "female_pct": round(female/total*100,1),
        "bpl_pct":    round(bpl/total*100,1),
    }
def get_gender_distribution():
    ben, _ = load()
    df = ben["gender"].value_counts().reset_index()
    df.columns = ["gender", "count"]   # Explicitly rename to avoid duplicate 'count'
    return df
def get_age_group_distribution():
    ben, _ = load()
    bins = [0, 14, 25, 45, 60, 120]
    labels = ["Child (1-14)", "Youth (15-25)", "Adult (26-45)",
              "Middle-Aged (46-60)", "Senior (60+)"]
    ben["age_group"] = pd.cut(ben["age"], bins=bins, labels=labels, right=True)
    df = ben["age_group"].value_counts().reset_index()
    df.columns = ["age_group", "count"]
    df["pct"] = (df["count"] / len(ben) * 100).round(1)
    df["age_group"] = pd.Categorical(df["age_group"], categories=labels, ordered=True)
    return df.sort_values("age_group").reset_index(drop=True)
def get_occupation_distribution():
    ben, _ = load()
    df = ben["occupation"].value_counts().reset_index()
    df.columns = ["occupation","count"]
    df["pct"] = (df["count"]/len(ben)*100).round(1)
    return df.head(10)
def get_category_demographics():
    """Q5 — Which demographics benefit most from NGO programs?"""
    ben, _ = load()
    df = ben.groupby("category").agg(
        total     =("beneficiary_id","count"),
        female    =("is_female","sum"),
        bpl       =("is_bpl","sum"),
        completed =("is_completed","sum"),
        avg_age   =("age","mean"),
    ).reset_index()
    df["success_rate"] = (df["completed"]/df["total"]*100).round(1)
    df["female_pct"]   = (df["female"]/df["total"]*100).round(1)
    df["bpl_pct"]      = (df["bpl"]/df["total"]*100).round(1)
    df["avg_age"]      = df["avg_age"].round(1)
    return df.sort_values("total", ascending=False)
def get_state_bpl_coverage():
    """Q7 — Which states have highest BPL beneficiary coverage?"""
    ben, _ = load()
    df = ben.groupby("state").agg(
        total  =("beneficiary_id","count"),
        bpl    =("is_bpl","sum"),
        female =("is_female","sum"),
        completed=("is_completed","sum"),
    ).reset_index()
    df["bpl_pct"]      = (df["bpl"]/df["total"]*100).round(1)
    df["female_pct"]   = (df["female"]/df["total"]*100).round(1)
    df["success_rate"] = (df["completed"]/df["total"]*100).round(1)
    return df.sort_values("bpl_pct", ascending=False)
def get_outcome_distribution():
    ben, _ = load()
    df = ben["outcome_achieved"].value_counts().reset_index()
    df.columns = ["outcome","count"]
    df["pct"] = (df["count"]/len(ben)*100).round(1)
    return df
def get_dropout_analysis():
    ben, _ = load()
    df = ben.groupby(["program_name","category","state"]).agg(
        total  =("beneficiary_id","count"),
        dropped=("beneficiary_id", lambda x: (ben.loc[x.index,"enrollment_status"]=="Dropped").sum()),
    ).reset_index()
    df["dropout_rate"] = (df["dropped"]/df["total"]*100).round(1)
    return df[df["total"] >= 8].sort_values("dropout_rate", ascending=False).head(10)
def get_enrollment_status_by_category():
    ben, _ = load()
    df = ben.groupby(["category","enrollment_status"]).size().unstack(fill_value=0).reset_index()
    return df
def get_full_table():
    ben, _ = load()
    return ben[["beneficiary_id","beneficiary_name","age","gender",
                "occupation","bpl_status","program_name","category",
                "state","enrollment_status","outcome_achieved","age_group"]]
