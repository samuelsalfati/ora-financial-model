# Ora Living – WOW Model (Step 1: Virginia)

Virginia-only baseline to prove the UI & outputs before multi-state and vendor logic.

## Run
```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Features
- Excel-like editors for **rates**, **utilization**, and **growth/overhead**
- RPM/CCM/TCM codes modeled; collection rate and 16-day RPM proxy via utilization
- Charts: Revenue vs Costs vs EBITDA vs Cash; Patients & Capacity; Unit Econ waterfall
- One-click **Excel export** of monthly, KPI, and assumptions

## Next steps
- Add multi-state (GPCI by state), vendor switching (Impilo/CareSimple/Ora), PCM toggle, and migration.