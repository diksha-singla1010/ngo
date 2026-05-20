import pandas as pd
import numpy as np
import pickle, os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DONOR_FILE, MODEL_FILE
from sklearn.ensemble      import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model  import LogisticRegression
from sklearn.tree          import DecisionTreeClassifier
from sklearn.neighbors     import KNeighborsClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics       import (accuracy_score, precision_score, recall_score,
                                    f1_score, roc_auc_score, confusion_matrix,
                                    classification_report)
from sklearn.utils         import resample
FEATURES = [
    "amount_cr","amount_log","beneficiaries",
    "donor_type_enc","state_enc","sector_enc",
    "fcra_flag","year_numeric","is_recent",
    "amount_per_yr",
]
FEATURE_LABELS = [
    "Donation Amount (Cr)","Log Amount","Beneficiaries Impacted",
    "Donor Type","State","Sector Focus",
    "FCRA Compliant","Financial Year","Is Recent Donor",
    "Amount Per Year",
]
def _build_features():
    df = pd.read_csv(DONOR_FILE, encoding="utf-8-sig")
    df["amount_cr"]   = pd.to_numeric(df["amount_cr"],   errors="coerce").fillna(0)
    df["beneficiaries"]= pd.to_numeric(df["beneficiaries"],errors="coerce").fillna(0)
    df["amount_log"]  = np.log1p(df["amount_cr"])
    df["fcra_flag"]   = (df["fcra_compliant"] == "Yes").astype(int)
    year_map = {"2019-20":2020,"2020-21":2021,"2021-22":2022,"2022-23":2023,"2023-24":2024}
    df["year_numeric"]= df["financial_year"].map(year_map).fillna(2022)
    df["is_recent"]   = (df["year_numeric"] >= 2023).astype(int)
    df["amount_per_yr"]= df["amount_cr"] / (2025 - df["year_numeric"] + 1)
    le = LabelEncoder()
    df["donor_type_enc"] = le.fit_transform(df["donor_type"].fillna("Unknown"))
    df["state_enc"]      = le.fit_transform(df["state"].fillna("Unknown"))
    df["sector_enc"]     = le.fit_transform(df["sector_focus"].fillna("Unknown"))
    df["churned"]        = (df["is_active_donor"] == "No").astype(int)
    return df
def train_models():
    df = _build_features()
    X  = df[FEATURES].values
    y  = df["churned"].values
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y)
    sc = StandardScaler()
    X_tr_s = sc.fit_transform(X_tr)
    X_te_s  = sc.transform(X_te)
    idx_maj = np.where(y_tr == 0)[0]
    idx_min = np.where(y_tr == 1)[0]
    if len(idx_min) > 0 and len(idx_min) < len(idx_maj):
        idx_up  = resample(idx_min, replace=True, n_samples=len(idx_maj), random_state=42)
        idx_bal = np.concatenate([idx_maj, idx_up])
        np.random.seed(42); np.random.shuffle(idx_bal)
        X_tr_s  = X_tr_s[idx_bal]
        y_tr    = y_tr[idx_bal]
    classifiers = {
        "Random Forest":      RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced"),
        "Gradient Boosting":  GradientBoostingClassifier(n_estimators=100, random_state=42),
        "Logistic Regression":LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced"),
        "Decision Tree":      DecisionTreeClassifier(max_depth=6, random_state=42, class_weight="balanced"),
        "KNN":                KNeighborsClassifier(n_neighbors=5),
    }
    cv      = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results = {}
    best_name, best_auc = None, 0
    for name, clf in classifiers.items():
        clf.fit(X_tr_s, y_tr)
        preds = clf.predict(X_te_s)
        probs = clf.predict_proba(X_te_s)[:,1]
        acc   = accuracy_score (y_te, preds)
        prec  = precision_score(y_te, preds, zero_division=0)
        rec   = recall_score   (y_te, preds, zero_division=0)
        f1    = f1_score       (y_te, preds, zero_division=0)
        auc   = roc_auc_score  (y_te, probs)
        cv_sc = cross_val_score(clf, X_tr_s, y_tr, cv=cv, scoring="accuracy").mean()
        cm    = confusion_matrix(y_te, preds)
        results[name] = {
            "model": clf, "accuracy": round(acc,4), "precision": round(prec,4),
            "recall": round(rec,4), "f1": round(f1,4),
            "auc": round(auc,4), "cv": round(cv_sc,4),
            "confusion": cm.tolist(), "probs": probs, "preds": preds,
        }
        if auc > best_auc:
            best_auc  = auc
            best_name = name
    best_clf = results[best_name]["model"]
    if hasattr(best_clf, "feature_importances_"):
        fi = dict(zip(FEATURE_LABELS, best_clf.feature_importances_.tolist()))
    else:
        from sklearn.inspection import permutation_importance
        perm = permutation_importance(best_clf, X_te_s, y_te, n_repeats=5, random_state=42)
        fi = dict(zip(FEATURE_LABELS, perm.importances_mean.tolist()))
    artifact = {
        "best_name": best_name, "results": results,
        "scaler": sc, "features": FEATURES, "feature_labels": FEATURE_LABELS,
        "feature_importances": fi,
    }
    os.makedirs(os.path.dirname(MODEL_FILE), exist_ok=True)
    with open(MODEL_FILE, "wb") as f:
        pickle.dump(artifact, f)
    print(f"[ML] Best model: {best_name} | AUC={best_auc:.4f}")
    print(f"[ML] Model saved: {MODEL_FILE}")
    return artifact
def load_model():
    if not os.path.exists(MODEL_FILE):
        print("[ML] Model not found — training now...")
        return train_models()
    with open(MODEL_FILE, "rb") as f:
        return pickle.load(f)
def predict_all():
    artifact = load_model()
    model  = artifact["results"][artifact["best_name"]]["model"]
    scaler = artifact["scaler"]
    feats  = artifact["features"]
    df     = _build_features()
    X_s    = scaler.transform(df[feats].values)
    probs  = model.predict_proba(X_s)[:,1]
    df["churn_probability"] = probs
    df["churn_risk"] = pd.cut(probs, bins=[0,0.30,0.60,1.01],
                               labels=["Low","Medium","High"])
    return df[["donor_id","donor_name","donor_type","state","sector_focus",
               "amount_cr","is_active_donor","churn_probability","churn_risk"]]
def get_model_summary():
    art = load_model()
    rows = []
    for name, res in art["results"].items():
        rows.append({
            "Model": name, "Accuracy": res["accuracy"],
            "Precision": res["precision"], "Recall": res["recall"],
            "F1": res["f1"], "AUC-ROC": res["auc"], "CV(5-fold)": res["cv"],
            "Best": "★" if name == art["best_name"] else "",
        })
    return pd.DataFrame(rows), art["feature_importances"], art["best_name"]
