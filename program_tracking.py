import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PROGRAM_FILE, BENEFICIARY_FILE
def load():
    prog = pd.read_csv(PROGRAM_FILE, encoding="utf-8-sig")
    bene = pd.read_csv(BENEFICIARY_FILE, encoding="utf-8-sig")
    prog["budget_inr"] = pd.to_numeric(prog["budget_inr"], errors="coerce").fillna(0)
    return prog, bene
def get_program_kpis():
    prog, bene = load()
    total_prog    = len(prog)
    active_prog   = int((prog["status"] == "Active").sum())
    total_budget  = prog["budget_inr"].sum()
    total_target  = int(prog["target_beneficiaries"].sum())
    categories    = prog["category"].nunique()
    states        = prog["state"].nunique()
    total_bene    = len(bene)
    active_bene   = int((bene["enrollment_status"] == "Active").sum())
    completed_bene= int((bene["enrollment_status"] == "Completed").sum())
    female_bene   = int((bene["gender"] == "Female").sum())
    bpl_bene      = int((bene["bpl_status"] == "Yes").sum())
    avg_age       = round(bene["age"].mean(), 1)
    return {
        "total_programs":   total_prog,
        "active_programs":  active_prog,
        "total_budget_cr":  round(total_budget / 1e7, 2),
        "total_target":     total_target,
        "categories":       categories,
        "states_covered":   states,
        "total_beneficiaries": total_bene,
        "active_beneficiaries": active_bene,
        "completed_beneficiaries": completed_bene,
        "female_beneficiaries": female_bene,
        "bpl_beneficiaries": bpl_bene,
        "avg_age": avg_age,
    }
def get_category_summary():
    prog, bene = load()
    cat = prog.groupby("category").agg(
        program_count=("program_id","count"),
        total_budget=("budget_inr","sum"),
        target_beneficiaries=("target_beneficiaries","sum"),
        active=("is_active_program","sum"),
    ).reset_index()
    cat["budget_cr"] = (cat["total_budget"] / 1e7).round(2)
    ben_cat = bene.groupby("category").agg(
        enrolled=("beneficiary_id","count"),
        completed=("is_completed","sum"),
        female=("is_female","sum"),
        bpl=("is_bpl","sum"),
    ).reset_index()
    ben_cat["success_rate"] = (ben_cat["completed"] / ben_cat["enrolled"] * 100).round(1)
    return cat.merge(ben_cat, on="category", how="left")
def get_state_wise_programs():
    prog, bene = load()
    sp = prog.groupby("state").agg(
        programs=("program_id","count"),
        budget=("budget_inr","sum"),
    ).reset_index()
    sb = bene.groupby("state").agg(
        beneficiaries=("beneficiary_id","count"),
        completed=("is_completed","sum"),
        bpl=("is_bpl","sum"),
    ).reset_index()
    df = sp.merge(sb, on="state", how="left").fillna(0)
    df["budget_cr"] = (df["budget"] / 1e7).round(2)
    df["success_rate"] = (df["completed"] / df["beneficiaries"] * 100).round(1)
    return df.sort_values("beneficiaries", ascending=False)
def get_cost_per_beneficiary():
    prog, bene = load()
    bc = bene.groupby("program_id").size().reset_index(name="enrolled")
    df = prog.merge(bc, on="program_id", how="left").fillna(0)
    df["cost_per_ben"] = (df["budget_inr"] / df["enrolled"].replace(0,1)).round(0)
    return df[["program_name","category","state","budget_inr",
               "enrolled","cost_per_ben","status"]].sort_values("cost_per_ben")
def get_program_success_rates():
    prog, bene = load()
    grp = bene.groupby("program_id").agg(
        enrolled  =("beneficiary_id","count"),
        completed =("is_completed","sum"),
        female    =("is_female","sum"),
        bpl       =("is_bpl","sum"),
    ).reset_index()
    grp["success_rate"] = (grp["completed"] / grp["enrolled"] * 100).round(1)
    return prog[["program_id","program_name","category","state",
                 "budget_inr","duration_months","status"]].merge(
        grp, on="program_id", how="left").sort_values("success_rate", ascending=False)
def get_duration_vs_completion():
    prog, bene = load()
    grp = bene.groupby("program_id").agg(
        enrolled  =("beneficiary_id","count"),
        completed =("is_completed","sum"),
    ).reset_index()
    grp["success_rate"] = (grp["completed"]/grp["enrolled"]*100).round(1)
    return prog[["program_id","duration_months","category"]].merge(grp, on="program_id",how="left")
def get_funding_breakdown():
    prog, _ = load()
    return prog.groupby("funding_source").agg(
        programs=("program_id","count"),
        budget  =("budget_inr","sum"),
    ).reset_index().sort_values("budget", ascending=False)
def get_programs_table():
    prog, bene = load()
    bc = bene.groupby("program_id").agg(
        enrolled=("beneficiary_id","count"),
        completed=("is_completed","sum"),
    ).reset_index()
    bc["success_rate"] = (bc["completed"]/bc["enrolled"]*100).round(1)
    df = prog.merge(bc, on="program_id", how="left")
    df["budget_cr"] = (df["budget_inr"]/1e7).round(2)
    return df[["program_id","program_name","category","state",
               "implementing_ngo","budget_cr","enrolled","success_rate",
               "funding_source","status","duration_months"]]
