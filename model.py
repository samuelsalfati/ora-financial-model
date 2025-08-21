import pandas as pd
import numpy as np

def default_rates():
    return {
        # RPM
        "99453": {"rate":18.95, "type":"setup"},     # once per new patient
        "99454": {"rate":45.12, "type":"monthly"},   # device 16+ days
        "99457": {"rate":46.85, "type":"monthly"},   # 20 min
        "99458": {"rate":37.62, "type":"monthly"},   # +20 min
        "99091": {"rate":51.29, "type":"monthly"},   # MD/QHP review
        # CCM
        "99490": {"rate":59.90, "type":"monthly"},
        "99439": {"rate":48.72, "type":"monthly"},
        # TCM
        "99495": {"rate":195.00, "type":"once"},
        "99496": {"rate":260.00, "type":"once"},
    }

def default_util():
    return {
        "rpm_setup": 0.95,   # 99453 on new
        "rpm_16day": 0.80,   # 99454 eligible
        "rpm_20min": 0.80,   # 99457
        "rpm_40min": 0.25,   # 99458
        "md_99091":  0.50,   # 99091
        "ccm_99490": 0.60,
        "ccm_99439": 0.20,
        # TCM proxy
        "tcm_99495": 0.02,
        "tcm_99496": 0.01,
        # collections
        "collection_rate": 0.95,
    }

def default_settings():
    return {
        "months": 60,
        "initial_patients": 50,
        "monthly_growth": 0.10,
        "initial_homes": 40,
        "home_growth_per_year": 1,
        "patients_per_home_growth": 0.05,
        "gpci": 1.00,  # Virginia
        "overhead_base": 10000.0,
        "overhead_cap": 50000.0,
        "initial_cash": 1_500_000 - (500_000+400_000+300_000+300_000),
        # staffing proxy
        "staff_minutes_available_per_month": 160*60,  # per FTE
        "staff_fte": 3,
        "staff_fte_growth_every_12m": 1,
        # blended staffing $ pmpm (can expose later)
        "staffing_pmpm": 66.0,
        # platform/hardware placeholders for Step 1 (single-vendor neutral)
        "platform_pmpm": 12.0,
        "hardware_per_new": 120.0,
    }

def _patients_per_home(month, annual_growth):
    return 20 * (1+annual_growth) ** ((month-1)//12)

def run_model(rates, util, settings):
    months = settings["months"]
    gpci = settings["gpci"]
    tot_patients = 0
    cash = settings["initial_cash"]

    rows = []
    staff_fte = settings["staff_fte"]
    staff_minutes_available_per_month = settings["staff_minutes_available_per_month"]

    for m in range(1, months+1):
        # annual staff ramp
        if m>1 and (m-1)%12==0:
            staff_fte += settings["staff_fte_growth_every_12m"]

        # homes capacity
        homes_now = settings["initial_homes"] + settings["home_growth_per_year"] * ((m-1)//12)
        pph = _patients_per_home(m, settings["patients_per_home_growth"])
        max_patients = int(homes_now * pph)

        # new patients
        if m == 1:
            new_pts = settings["initial_patients"]
        else:
            growth = int(tot_patients * settings["monthly_growth"])
            new_pts = max(0, min(max_patients - tot_patients, growth))
        tot_patients += new_pts
        active_pts = tot_patients

        # revenue
        rev_setup = rates["99453"]["rate"] * util["rpm_setup"] * new_pts
        rev_99454 = gpci * rates["99454"]["rate"] * util["rpm_16day"] * active_pts
        rev_99457 = gpci * rates["99457"]["rate"] * util["rpm_20min"] * active_pts
        rev_99458 = gpci * rates["99458"]["rate"] * util["rpm_40min"] * active_pts
        rev_99091 = gpci * rates["99091"]["rate"] * util["md_99091"]  * active_pts
        rev_99490 = gpci * rates["99490"]["rate"] * util["ccm_99490"] * active_pts
        rev_99439 = gpci * rates["99439"]["rate"] * util["ccm_99439"] * active_pts
        rev_99495 = rates["99495"]["rate"] * util["tcm_99495"] * active_pts
        rev_99496 = rates["99496"]["rate"] * util["tcm_99496"] * active_pts

        gross = rev_setup + rev_99454 + rev_99457 + rev_99458 + rev_99091 + rev_99490 + rev_99439 + rev_99495 + rev_99496
        net = gross * util["collection_rate"]

        # costs
        platform = settings["platform_pmpm"] * active_pts
        hardware = settings["hardware_per_new"] * new_pts
        overhead = min(settings["overhead_base"], settings["overhead_cap"])
        staffing = settings["staffing_pmpm"] * active_pts

        # staffing capacity proxy
        rpm_minutes_demand = active_pts * (20*util["rpm_20min"] + 20*util["rpm_40min"])
        staff_minutes_capacity = staff_fte * staff_minutes_available_per_month

        total_costs = platform + hardware + overhead + staffing
        ebitda = net - total_costs
        cash += ebitda

        per_rev = net/active_pts if active_pts>0 else 0
        per_cost = total_costs/active_pts if active_pts>0 else 0
        per_margin = per_rev - per_cost

        rows.append({
            "Month": m,
            "Total Patients": active_pts,
            "New Patients": new_pts,
            "Total Revenue": net,
            "Total Costs": total_costs,
            "EBITDA": ebitda,
            "Cash Balance": cash,
            "Per-Patient Revenue": per_rev,
            "Per-Patient Cost": per_cost,
            "Per-Patient Margin": per_margin,
            "RPM_Minutes_Demand": rpm_minutes_demand,
            "Staff_Minutes_Capacity": staff_minutes_capacity
        })

    return pd.DataFrame(rows)

def summarize(df):
    kpi = pd.DataFrame([{
        "Months": int(df["Month"].max()),
        "Ending Patients": int(df["Total Patients"].max()),
        "Cumulative Revenue": float(df["Total Revenue"].sum()),
        "Cumulative EBITDA": float(df["EBITDA"].sum()),
        "Ending Cash": float(df["Cash Balance"].iloc[-1])
    }])
    return {"kpi": kpi}