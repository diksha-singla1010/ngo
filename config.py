"""
NGO Impact Analytics & Donor Management System
config.py — Central Configuration File

Author : Diksha | Roll No: 10 | MCA 2025-2026
"""

import os
import sys

# ==================================================
# BASE DIRECTORY
# ==================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Allow local imports
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ==================================================
# FOLDERS
# ==================================================
DATA_DIR   = os.path.join(BASE_DIR, "data")
MODEL_DIR  = os.path.join(BASE_DIR, "models")
REPORT_DIR = os.path.join(BASE_DIR, "reports")

for folder in [DATA_DIR, MODEL_DIR, REPORT_DIR]:
    os.makedirs(folder, exist_ok=True)

# ==================================================
# DATA FILES
# ==================================================
NGO_FILE         = os.path.join(DATA_DIR, "ngo_data_clean.csv")
DONOR_FILE       = os.path.join(DATA_DIR, "donor_data_clean.csv")
PROGRAM_FILE     = os.path.join(DATA_DIR, "program_data_clean.csv")
BENEFICIARY_FILE = os.path.join(DATA_DIR, "beneficiary_data_clean.csv")

# ==================================================
# MODEL FILE (Required for ml_churn.py)
# ==================================================
MODEL_FILE = os.path.join(MODEL_DIR, "churn_model.pkl")

# ==================================================
# BUSINESS LOGIC FILES
# ==================================================
ML_MODULE_FILE       = os.path.join(BASE_DIR, "ml_churn.py")
CROSS_MODULE_FILE    = os.path.join(BASE_DIR, "cross_analysis.py")
DONOR_MODULE_FILE    = os.path.join(BASE_DIR, "donor_management.py")
PROGRAM_MODULE_FILE  = os.path.join(BASE_DIR, "program_tracking.py")
BENEFICIARY_MODULE_FILE = os.path.join(BASE_DIR, "beneficiary_management.py")

# ==================================================
# APP SETTINGS
# ==================================================
APP_TITLE  = "NGO Impact Analytics & Donor Management System"
APP_ICON   = "🌱"
APP_LAYOUT = "wide"

# ==================================================
# UI COLORS
# ==================================================
PRIMARY_COLOR   = "#00C896"
SECONDARY_COLOR = "#1E293B"
CARD_COLOR      = "rgba(255,255,255,0.08)"
TEXT_COLOR      = "#FFFFFF"

# ==================================================
# REPORT
# ==================================================
REPORT_NAME = "ngo_dashboard_report.pdf"

# ==================================================
# ML SETTINGS
# ==================================================
RANDOM_STATE = 42
TEST_SIZE    = 0.25
CV_FOLDS     = 5

# ==================================================
# CHECK FILES
# ==================================================
REQUIRED_FILES = {
    "ngo_data_clean.csv": NGO_FILE,
    "donor_data_clean.csv": DONOR_FILE,
    "program_data_clean.csv": PROGRAM_FILE,
    "beneficiary_data_clean.csv": BENEFICIARY_FILE,
    "ml_churn.py": ML_MODULE_FILE,
    "cross_analysis.py": CROSS_MODULE_FILE,
    "donor_management.py": DONOR_MODULE_FILE,
    "program_tracking.py": PROGRAM_MODULE_FILE,
    "beneficiary_management.py": BENEFICIARY_MODULE_FILE
}

def check_files():
    missing = []
    for name, path in REQUIRED_FILES.items():
        if not os.path.exists(path):
            missing.append(f"{name} -> {path}")
    return missing

# ==================================================
# TEST RUN
# ==================================================
if __name__ == "__main__":
    print("=== CONFIGURATION LOADED ===")
    print("Base Directory :", BASE_DIR)
    print("Data Folder    :", DATA_DIR)
    print("Model Folder   :", MODEL_DIR)
    print("Report Folder  :", REPORT_DIR)
    print("Model File     :", MODEL_FILE)

    missing = check_files()

    if missing:
        print("\n⚠ Missing Files:")
        for item in missing:
            print(" -", item)
    else:
        print("\n✅ All files found successfully.")