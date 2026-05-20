import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import NGO_FILE, DONOR_FILE, PROGRAM_FILE, BENEFICIARY_FILE
def load_all():
    ngo  = pd.read_csv(NGO_FILE,         encoding="utf-8-sig")
    don  = pd.read_csv(DONOR_FILE,       encoding="utf-8-sig")
    prog = pd.read_csv(PROGRAM_FILE,     encoding="utf-8-sig")
    ben  = pd.read_csv(BENEFICIARY_FILE, encoding="utf-8-sig")
    don["amount_cr"]   = pd.to_numeric(don["amount_cr"],   errors="coerce").fillna(0)
    prog["budget_inr"] = pd.to_numeric(prog["budget_inr"], errors="coerce").fillna(0)
    return ngo, don, prog, ben
def q1_sector_csr_funding():
    _, don, _, _ = load_all()
    return don.groupby("sector_focus").agg(
        donors=("donor_id","count"),
        total_cr=("amount_cr","sum"),
        avg_cr=("amount_cr","mean"),
    ).reset_index().rename(columns={"sector_focus":"sector"}).sort_values("total_cr",ascending=False)
def q2_program_success_rates():
    _, _, prog, ben = load_all()
    grp = ben.groupby("program_id").agg(
        enrolled=("beneficiary_id","count"),
        completed=("is_completed","sum"),
        female=("is_female","sum"),
        bpl=("is_bpl","sum"),
    ).reset_index()
    grp["success_rate"] = (grp["completed"]/grp["enrolled"]*100).round(1)
    return prog[["program_id","program_name","category","state","budget_inr"]].merge(
        grp, on="program_id", how="left").sort_values("success_rate", ascending=False)
def q3_budget_vs_funding_by_state():
    _, don, prog, _ = load_all()
    prog_state = prog.groupby("state")["budget_inr"].sum().reset_index(name="program_budget")
    don_state  = don.groupby("state")["amount_cr"].sum().reset_index(name="donor_funds_cr")
    return prog_state.merge(don_state, on="state", how="outer").fillna(0).sort_values(
        "program_budget", ascending=False)
def q4_churn_factors_summary():
    from ml_churn import get_model_summary
    _, fi, best = get_model_summary()
    fi_df = pd.DataFrame(list(fi.items()), columns=["Feature","Importance"])
    return fi_df.sort_values("Importance", ascending=False)
def q5_demographic_impact():
    _, _, prog, ben = load_all()
    return ben.groupby(["category","gender"]).agg(
        count=("beneficiary_id","count"),
        completed=("is_completed","sum"),
        bpl=("is_bpl","sum"),
    ).reset_index().assign(
        success_rate=lambda x: (x["completed"]/x["count"]*100).round(1),
        bpl_pct     =lambda x: (x["bpl"]/x["count"]*100).round(1),
    ).sort_values(["category","count"], ascending=[True,False])
def q6_fcra_impact():
    ngo, _, prog, ben = load_all()
    fcra_col = next((c for c in ["fcra_registered", "fcra_status"] if c in ngo.columns), None)
    if not fcra_col:
        fcra_col = next((c for c in ngo.columns if "fcra" in c.lower()), None)
    if not fcra_col:
        raise ValueError("No FCRA column found in NGO data")
    ngo = ngo[["ngo_name", fcra_col]].copy()
    ngo["fcra_status"] = ngo[fcra_col].astype(str).str.strip().str.upper().isin(
        ["1", "YES", "TRUE", "REGISTERED", "FCRA REGISTERED"]
    ).map({True: "FCRA Registered", False: "Not Registered"})
    stop = {"foundation", "trust", "samiti", "society", "sangh", "india", "seva", "kalyan"}
    ngo_lookup = dict(zip(ngo["ngo_name"].str.lower(), ngo["fcra_status"]))
    def status_for(name):
        key = str(name).strip().lower()
        if key in ngo_lookup:
            return ngo_lookup[key]
        tokens = [t for t in key.replace("/", " ").split() if t not in stop]
        matched = ngo[ngo["ngo_name"].str.lower().apply(lambda n: all(t in n for t in tokens))] if tokens else ngo.iloc[0:0]
        if matched.empty:
            matched = ngo[ngo["ngo_name"].str.lower().str.contains(tokens[0], na=False)] if tokens else ngo.iloc[0:0]
        if matched.empty:
            return "Not Registered"
        return matched["fcra_status"].mode().iat[0]
    program_status = prog[["program_id", "program_name", "implementing_ngo"]].copy()
    program_status["fcra_status"] = program_status["implementing_ngo"].map(status_for)
    ben_prog = ben.groupby("program_id").agg(
        enrolled=("beneficiary_id", "count"), completed=("is_completed", "sum")
    ).reset_index()
    ben_prog["success_rate"] = (ben_prog["completed"] / ben_prog["enrolled"] * 100).round(1)
    return program_status.merge(ben_prog, on="program_id", how="left").groupby("fcra_status").agg(
        programs=("program_id", "count"),
        avg_success=("success_rate", "mean"),
        total_enrolled=("enrolled", "sum"),
    ).reset_index().assign(avg_success=lambda x: x["avg_success"].round(1))
def q7_state_bpl_coverage():
    _, _, _, ben = load_all()
    df = ben.groupby("state").agg(
        total=("beneficiary_id","count"),
        bpl=("is_bpl","sum"),
        female=("is_female","sum"),
        completed=("is_completed","sum"),
    ).reset_index()
    df["bpl_pct"]      = (df["bpl"]/df["total"]*100).round(1)
    df["success_rate"] = (df["completed"]/df["total"]*100).round(1)
    return df.sort_values("bpl_pct", ascending=False)
def q8_duration_vs_completion():
    _, _, prog, ben = load_all()
    grp = ben.groupby("program_id").agg(
        enrolled=("beneficiary_id","count"),
        completed=("is_completed","sum"),
    ).reset_index()
    grp["success_rate"] = (grp["completed"]/grp["enrolled"]*100).round(1)
    df = prog[["program_id","program_name","duration_months","category"]].merge(
        grp, on="program_id", how="left")
    bins   = [0,12,24,36,60]
    labels = ["<12 mo","12-24 mo","24-36 mo",">36 mo"]
    df["duration_band"] = pd.cut(df["duration_months"], bins=bins, labels=labels)
    return df.groupby("duration_band").agg(
        programs=("program_id","count"),
        avg_success=("success_rate","mean"),
        avg_enrolled=("enrolled","mean"),
    ).reset_index()
def q9_cost_per_beneficiary():
    _, _, prog, ben = load_all()
    bc = ben.groupby("program_id").size().reset_index(name="enrolled")
    df = prog[["program_id","program_name","category","budget_inr"]].merge(bc, on="program_id", how="left")
    df["enrolled"]     = df["enrolled"].fillna(0)
    df["cost_per_ben"] = (df["budget_inr"] / df["enrolled"].replace(0,1)).round(0)
    return df.groupby("category").agg(
        programs=("program_id","count"),
        total_budget=("budget_inr","sum"),
        total_enrolled=("enrolled","sum"),
        avg_cost_per_ben=("cost_per_ben","mean"),
    ).reset_index().assign(
        overall_cpb=lambda x: (x["total_budget"]/x["total_enrolled"].replace(0,1)).round(0)
    ).sort_values("overall_cpb")
def q10_payment_mode_retention():
    _, don, _, _ = load_all()
    don["is_active_flag"] = (don["is_active_donor"] == "Yes").astype(int)
    pm = don.groupby("payment_mode").agg(
        count=("donor_id","count"),
        total_cr=("amount_cr","sum"),
        active=("is_active_flag","sum"),
    ).reset_index()
    pm["retention_rate"] = (pm["active"]/pm["count"]*100).round(1)
    return pm.sort_values("retention_rate", ascending=False)
