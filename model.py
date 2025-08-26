import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

# Vendor config structure
@dataclass
class VendorConfig:
    name: str
    # per-patient PMPM:
    #  - For Impilo, we support tiers: list of (min_patients_incl, pmpm)
    #  - For CareSimple/Ora, use flat pmpm
    tiers: Optional[List[Tuple[int, float]]] = None    # e.g., [(0, 8), (501, 14), (2001, 23)]
    flat_pmpm: Optional[float] = None                  # e.g., 15 for CareSimple, 5 for Ora
    # monthly fixed software fee (applied once per month, company-wide)
    monthly_software_fee: float = 0.0
    # hardware kits: name -> unit cost per new patient; you can pick which one to use in UI
    hardware_kits: Dict[str, float] = None
    # one-time CAPEX when Ora becomes active
    dev_capex: float = 0.0

def default_vendor_presets():
    return {
        "Impilo": VendorConfig(
            name="Impilo",
            tiers=[(0, 8.0), (501, 14.0), (2001, 23.0)],   # EDITABLE in UI
            flat_pmpm=None,
            monthly_software_fee=2000.0,                   # EDITABLE
            hardware_kits={"Kit-300": 300.0, "Kit-400": 400.0, "Kit-500": 500.0},  # EDITABLE
            dev_capex=0.0,
        ),
        "CareSimple": VendorConfig(
            name="CareSimple",
            tiers=None,
            flat_pmpm=15.0,                                # EDITABLE in UI
            monthly_software_fee=2000.0,                   # EDITABLE
            hardware_kits={"Kit-300": 300.0, "Kit-400": 400.0, "Kit-500": 500.0},  # EDITABLE
            dev_capex=0.0,
        ),
        "Ora": VendorConfig(
            name="Ora",
            tiers=None,
            flat_pmpm=5.0,                                 # EDITABLE
            monthly_software_fee=0.0,                      # EDITABLE
            hardware_kits={"Ora-Std": 185.0},              # EDITABLE
            dev_capex=250_000.0,                           # EDITABLE
        ),
    }

def _pmpm_for_vendor(vcfg: VendorConfig, active_patients: int) -> float:
    """
    Resolve PMPM given a vendor config and current active patient count.
    - If tiers provided (Impilo), pick the highest min threshold <= patients.
    - Else use flat pmpm (CareSimple/Ora).
    """
    if vcfg.tiers:
        # sort tiers by min threshold
        tiers = sorted(vcfg.tiers, key=lambda x: x[0])
        pmpm = tiers[0][1]
        for min_n, tier_pmpm in tiers:
            if active_patients >= min_n:
                pmpm = tier_pmpm
            else:
                break
        return pmpm
    return float(vcfg.flat_pmpm or 0.0)

def default_rates():
    """
    Billing code rates with population average multipliers.
    
    Multiplier Logic:
    - 1.0 = Standard codes billed once per eligible timeframe
    - >1.0 = "Additional" codes that can be billed multiple times
    
    Population Average Multipliers:
    Example: 99458 multiplier of 1.35 means across 10,000 patients:
    - 75% get base only (1x)  
    - 20% get 2x additional sessions
    - 5% get 3x additional sessions
    - Average = (0.75×1) + (0.20×2) + (0.05×3) = 1.35x
    """
    return {
        # RPM
        "99453": {"rate":19.00, "type":"setup", "multiplier":1.0},      # Patient education + device setup (once per patient)
        "99454": {"rate":52.50, "type":"monthly", "multiplier":1.0},    # Device supply + 16-day data (1x monthly)
        "99457": {"rate":50.00, "type":"monthly", "multiplier":1.0},    # Base 20 min treatment management (1x monthly)
        "99458": {"rate":42.50, "type":"monthly", "multiplier":1.35},   # Additional 20 min sessions (avg 1.35x monthly)
        "99091": {"rate":60.00, "type":"monthly", "multiplier":1.0},    # MD/QHP 30 min data review (1x monthly)
        # CCM
        "99490": {"rate":65.00, "type":"monthly", "multiplier":1.0},    # Base 20 min CCM (1x monthly)
        "99439": {"rate":48.50, "type":"monthly", "multiplier":1.2},    # Additional CCM sessions (avg 1.2x monthly)
        # PCM (Principal Care Management)
        "99426": {"rate":71.50, "type":"monthly", "multiplier":1.0},    # Base 30 min PCM (1x monthly)
        "99427": {"rate":52.50, "type":"monthly", "multiplier":1.15},   # Additional PCM sessions (avg 1.15x monthly)
        # TCM (per transition event)
        "99495": {"rate":192.50, "type":"once", "multiplier":1.0},      # TCM moderate complexity
        "99496": {"rate":260.00, "type":"once", "multiplier":1.0},      # TCM high complexity
        # Theoretical billing codes (advanced care management)
        "alzheimers_prevention": {"rate":180.00, "type":"monthly", "multiplier":1.0, "theoretical":True},
        "mental_health_support": {"rate":120.00, "type":"monthly", "multiplier":1.0, "theoretical":True},
        "preventive_care": {"rate":200.00, "type":"monthly", "multiplier":1.0, "theoretical":True},
    }

def default_util():
    """
    Utilization rates and working capital assumptions.
    
    Utilization = % of eligible patients who receive each service
    Collection Rate = % of billed revenue actually collected (bad debt adjustment)
    """
    return {
        # RPM utilization rates
        "rpm_setup": 0.95,   # 99453 setup rate for new patients
        "rpm_16day": 0.80,   # 99454 device supply eligibility  
        "rpm_20min": 0.80,   # 99457 base treatment management
        "rpm_40min": 0.25,   # 99458 additional sessions (multiplied by rate multiplier)
        "md_99091":  0.50,   # 99091 physician review rate
        # CCM utilization rates  
        "ccm_99490": 0.60,   # Base CCM eligibility
        "ccm_99439": 0.20,   # Additional CCM sessions (multiplied by rate multiplier)
        # PCM utilization rates (theoretical upside)
        "pcm_99426": 0.15,   # Base PCM eligibility
        "pcm_99427": 0.08,   # Additional PCM sessions (multiplied by rate multiplier)
        # TCM utilization rates (transition events)
        "tcm_99495": 0.02,   # Moderate complexity transitions per patient per month
        "tcm_99496": 0.01,   # High complexity transitions per patient per month
        # Theoretical billing utilization
        "alzheimers_prevention": 0.05,   # Advanced Alzheimer's care eligibility
        "mental_health_support": 0.10,   # Mental health service eligibility  
        "preventive_care": 0.08,          # Enhanced preventive care eligibility
        # Financial assumptions
        "collection_rate": 0.95,          # 95% collection rate (5% bad debt)
    }

def default_multi_state_config():
    """
    Default multi-state expansion configuration with GPCI adjustments.
    Realistic expansion timeline and patient counts based on market analysis.
    """
    return {
        "Virginia": {"start_month": 1, "initial_patients": 50, "initial_homes": 40, "gpci": 1.00, "active": True},
        "Florida": {"start_month": 12, "initial_patients": 80, "initial_homes": 60, "gpci": 1.05, "active": False},  # Large retiree population
        "Texas": {"start_month": 18, "initial_patients": 120, "initial_homes": 80, "gpci": 1.03, "active": False},  # Large population centers
        "New York": {"start_month": 30, "initial_patients": 90, "initial_homes": 50, "gpci": 1.08, "active": False},  # High reimbursement
        "California": {"start_month": 42, "initial_patients": 100, "initial_homes": 70, "gpci": 1.10, "active": False},  # Premium market
    }

def default_settings():
    """
    Model settings including growth, costs, and working capital assumptions.
    
    Working Capital Components:
    - DSO: Days Sales Outstanding (how long to collect A/R)
    - Inventory Days: Hardware devices kept on hand  
    - DPO: Days Payable Outstanding (payment terms to vendors)
    """
    return {
        # Time horizon and growth
        "months": 60,
        "initial_patients": 50,
        "monthly_growth": 0.10,
        "initial_homes": 40,
        "home_growth_per_year": 1,
        "patients_per_home_growth": 0.05,
        
        # Geographic and regulatory
        "gpci": 1.00,  # Virginia base GPCI
        
        # Operating costs
        "overhead_base": 10000.0,
        "overhead_cap": 50000.0,
        "initial_cash": 1_500_000 - (500_000+400_000+300_000+300_000),  # $300k after initial investments
        
        # Staffing (legacy - will add detailed ratios)
        "staff_minutes_available_per_month": 160*60,  # per FTE
        "staff_fte": 3,
        "staff_fte_growth_every_12m": 1,
        "staffing_pmpm": 66.0,  # blended staffing cost per patient per month
        
        # Vendor configuration
        "initial_vendor": "Impilo",      # "Impilo" | "CareSimple" | "Ora"
        "migration_month": None,         # e.g., 18 to switch to Ora
        "vendor_selected_kit": {         # hardware kit selection per vendor
            "Impilo": "Kit-400",
            "CareSimple": "Kit-400", 
            "Ora": "Ora-Std"
        },
        "vendor_overrides": {},          # runtime overrides for vendor configs
        
        # Advanced features
        "include_pcm": False,            # Principal Care Management codes
        "include_theoretical": False,    # Theoretical billing codes (Alzheimers, etc.)
        
        # Working Capital Assumptions
        "dso_medicare": 45,              # Medicare/Medicaid collection days
        "dso_commercial": 75,            # Commercial payer collection days  
        "payer_mix_medicare": 0.65,      # 65% Medicare/Medicaid, 35% Commercial
        "inventory_days": 30,            # Hardware inventory on hand (days)
        "dpo_vendors": 30,               # Payment terms to vendors (days)
        "dpo_staffing": 15,              # Staff payroll cycle (bi-weekly)
        
        # Post-60-Month Infrastructure Transition
        "own_infrastructure_month": 61,  # Month to transition to owned IT/hardware
        "own_it_annual_cost": 500_000,   # Annual IT infrastructure cost (vs vendor fees)
        "own_hardware_unit_cost": 120,   # Cost per device when manufacturing own hardware
        "infrastructure_capex": 2_000_000,  # One-time capex for IT infrastructure buildout
    }

def _merge_vendor_overrides(base: VendorConfig, ov: dict | None) -> VendorConfig:
    if not ov: return base
    tiers = ov.get("tiers", base.tiers)
    flat = ov.get("flat_pmpm", base.flat_pmpm)
    fee = ov.get("monthly_software_fee", base.monthly_software_fee)
    kits = ov.get("hardware_kits", base.hardware_kits)
    capex = ov.get("dev_capex", base.dev_capex)
    return VendorConfig(base.name, tiers, flat, fee, kits, capex)

def _patients_per_home(month, annual_growth):
    return 20 * (1+annual_growth) ** ((month-1)//12)

def _calculate_working_capital(monthly_revenue, monthly_costs, settings):
    """
    Calculate working capital components based on DSO, inventory, and payment terms.
    
    Returns dict with A/R, Inventory, A/P, and Net Working Capital
    """
    # Accounts Receivable (based on blended DSO)
    medicare_pct = settings.get("payer_mix_medicare", 0.65)  
    commercial_pct = 1 - medicare_pct
    dso_medicare = settings.get("dso_medicare", 45)
    dso_commercial = settings.get("dso_commercial", 75)
    
    blended_dso = (medicare_pct * dso_medicare) + (commercial_pct * dso_commercial)
    accounts_receivable = monthly_revenue * (blended_dso / 30)  # Convert days to months
    
    # Inventory (hardware devices on hand)
    inventory_days = settings.get("inventory_days", 30)
    # Assume inventory value is proportional to monthly hardware costs
    monthly_hardware_cost = monthly_costs * 0.15  # Rough estimate, will be refined
    inventory = monthly_hardware_cost * (inventory_days / 30)
    
    # Accounts Payable (vendor payments and payroll)  
    dpo_vendors = settings.get("dpo_vendors", 30)
    dpo_staffing = settings.get("dpo_staffing", 15)
    
    vendor_costs = monthly_costs * 0.4  # Platform + hardware costs
    staffing_costs = monthly_costs * 0.5  # Staffing costs
    other_costs = monthly_costs * 0.1   # Overhead and other
    
    accounts_payable = (vendor_costs * (dpo_vendors / 30) + 
                       staffing_costs * (dpo_staffing / 30) + 
                       other_costs * (dpo_vendors / 30))
    
    # Net Working Capital = (A/R + Inventory) - A/P
    net_working_capital = accounts_receivable + inventory - accounts_payable
    
    return {
        "accounts_receivable": accounts_receivable,
        "inventory": inventory, 
        "accounts_payable": accounts_payable,
        "net_working_capital": net_working_capital
    }

def run_projection(
    states, gpci, homes, rates, util, settings,
):
    """
    Uses vendor pricing with:
      - Impilo: tiered PMPM + monthly software fee + chosen kit per new patient, NO CAPEX
      - CareSimple: flat PMPM + monthly software fee + chosen kit per new, NO CAPEX
      - Ora: flat PMPM + chosen kit per new + ONE-TIME dev CAPEX when Ora becomes active
    """
    months = settings["months"]
    monthly_growth = settings["monthly_growth"]
    pph_growth = settings["patients_per_home_growth"]
    homes_per_year = settings["home_growth_per_year"]
    cash = settings["initial_cash"]
    overhead_base = settings["overhead_base"]
    overhead_cap = settings["overhead_cap"]

    include_pcm = bool(settings.get("include_pcm", False))

    # Vendor presets + overrides
    _presets = default_vendor_presets()
    if settings.get("vendor_overrides"):
        for k,v in settings["vendor_overrides"].items():
            if k in _presets:
                _presets[k] = _merge_vendor_overrides(_presets[k], v)

    initial_vendor = settings.get("initial_vendor", "Impilo")
    migration_month = settings.get("migration_month", None)

    total_patients = {s: 0 for s in states}
    rows = []

    staff_fte = settings["staff_fte"]
    staff_minutes_available = settings["staff_minutes_available_per_month"]
    staffing_pmpm = settings.get("staffing_pmpm", 66.0)

    dev_capex_done = False

    for m in range(1, months+1):
        # staff ramp yearly
        if m > 1 and (m-1) % 12 == 0:
            staff_fte += settings["staff_fte_growth_every_12m"]

        # Which vendor is active this month?
        if migration_month is not None and m >= int(migration_month):
            vcfg = _presets["Ora"]
            vendor_name = "Ora"
            dev_capex = (0 if dev_capex_done else vcfg.dev_capex)
            if dev_capex > 0:
                dev_capex_done = True
        else:
            vcfg = _presets[initial_vendor]
            vendor_name = initial_vendor
            dev_capex = 0.0
            if initial_vendor == "Ora" and not dev_capex_done and m == 1:
                dev_capex = vcfg.dev_capex
                dev_capex_done = True

        # software fee should be charged once per month (company-wide)
        software_fee_charged = False

        # Iterate states
        active_states = [s for s,conf in states.items() if m >= conf["start_month"]]
        for state, conf in states.items():
            if m < conf["start_month"]:
                continue

            g = gpci[state]
            homes_now = homes[state] + homes_per_year * ((m-1)//12)
            pph = 20 * (1+pph_growth)**((m-1)//12)
            max_patients = int(homes_now * pph)

            if m == conf["start_month"]:
                new_pts = conf["initial_patients"]
            else:
                new_pts = max(0, min(max_patients - total_patients[state], int(total_patients[state] * monthly_growth)))
            total_patients[state] += new_pts
            active_pts = total_patients[state]

            # --- revenue calculation with multipliers ---
            include_theoretical = settings.get("include_theoretical", False)
            
            # RPM Revenue (setup is one-time, others are monthly)
            rev_setup = rates["99453"]["rate"] * rates["99453"]["multiplier"] * util["rpm_setup"] * new_pts
            rev_99454 = g * rates["99454"]["rate"] * rates["99454"]["multiplier"] * util["rpm_16day"] * active_pts  
            rev_99457 = g * rates["99457"]["rate"] * rates["99457"]["multiplier"] * util["rpm_20min"] * active_pts
            rev_99458 = g * rates["99458"]["rate"] * rates["99458"]["multiplier"] * util["rpm_40min"] * active_pts  # Uses 1.35x multiplier
            rev_99091 = g * rates["99091"]["rate"] * rates["99091"]["multiplier"] * util["md_99091"] * active_pts
            
            # CCM Revenue  
            rev_99490 = g * rates["99490"]["rate"] * rates["99490"]["multiplier"] * util["ccm_99490"] * active_pts
            rev_99439 = g * rates["99439"]["rate"] * rates["99439"]["multiplier"] * util["ccm_99439"] * active_pts  # Uses 1.2x multiplier
            
            # PCM Revenue (if enabled)
            rev_99426 = g * rates["99426"]["rate"] * rates["99426"]["multiplier"] * util.get("pcm_99426",0.0) * active_pts if include_pcm else 0.0
            rev_99427 = g * rates["99427"]["rate"] * rates["99427"]["multiplier"] * util.get("pcm_99427",0.0) * active_pts if include_pcm else 0.0  # Uses 1.15x multiplier
            
            # TCM Revenue (per transition event) 
            rev_99495 = rates["99495"]["rate"] * rates["99495"]["multiplier"] * util["tcm_99495"] * active_pts
            rev_99496 = rates["99496"]["rate"] * rates["99496"]["multiplier"] * util["tcm_99496"] * active_pts
            
            # Theoretical Advanced Care Revenue (if enabled)
            rev_alzheimers = g * rates["alzheimers_prevention"]["rate"] * rates["alzheimers_prevention"]["multiplier"] * util.get("alzheimers_prevention",0.0) * active_pts if include_theoretical else 0.0
            rev_mental_health = g * rates["mental_health_support"]["rate"] * rates["mental_health_support"]["multiplier"] * util.get("mental_health_support",0.0) * active_pts if include_theoretical else 0.0  
            rev_preventive = g * rates["preventive_care"]["rate"] * rates["preventive_care"]["multiplier"] * util.get("preventive_care",0.0) * active_pts if include_theoretical else 0.0

            gross = (rev_setup + rev_99454 + rev_99457 + rev_99458 + rev_99091 +
                     rev_99490 + rev_99439 + rev_99426 + rev_99427 + rev_99495 + rev_99496 +
                     rev_alzheimers + rev_mental_health + rev_preventive)
            net = gross * util["collection_rate"]

            # --- costs: Handle 60+ month infrastructure transition ---
            own_infra_month = settings.get("own_infrastructure_month", 61)
            infrastructure_capex = 0.0
            
            if m >= own_infra_month:
                # Post-60 month: Own IT infrastructure  
                platform = settings.get("own_it_annual_cost", 500_000) / 12  # Monthly IT cost
                kit_cost = settings.get("own_hardware_unit_cost", 120)  # Own manufacturing cost
                hardware = kit_cost * new_pts
                software_fee = 0.0  # No vendor software fees
                
                # One-time infrastructure capex in transition month
                if m == own_infra_month:
                    infrastructure_capex = settings.get("infrastructure_capex", 2_000_000)
                    
            else:
                # Pre-60 month: Vendor-based costs
                pmpm = _pmpm_for_vendor(vcfg, active_pts)
                platform = pmpm * active_pts
                
                chosen = settings["vendor_selected_kit"].get(vendor_name)
                kit_cost = (vcfg.hardware_kits or {}).get(chosen, 0.0)
                hardware = kit_cost * new_pts
                
                # Charge software fee once per month (company-wide)
                software_fee = 0.0
                if not software_fee_charged and active_pts > 0 and vcfg.monthly_software_fee > 0:
                    software_fee = vcfg.monthly_software_fee
                    software_fee_charged = True

            overhead = min(overhead_base + 1000*len(active_states), overhead_cap)
            staffing = settings.get("staffing_pmpm", 66.0) * active_pts

            rpm_minutes_demand = active_pts * (20*util["rpm_20min"] + 20*util["rpm_40min"])
            staff_minutes_capacity = staff_fte * staff_minutes_available

            total_costs = platform + hardware + software_fee + overhead + staffing + dev_capex + infrastructure_capex
            ebitda = net - total_costs
            
            # Working Capital calculation
            wc = _calculate_working_capital(net, total_costs, settings)
            
            # Free Cash Flow = EBITDA - Capex - Change in Working Capital  
            prev_nwc = 0  # Will track this properly in full implementation
            change_in_nwc = wc["net_working_capital"] - prev_nwc if m > 1 else wc["net_working_capital"]
            capex_total = dev_capex + infrastructure_capex
            free_cash_flow = ebitda - capex_total - change_in_nwc
            
            cash += free_cash_flow

            per_rev = net/active_pts if active_pts else 0.0
            # exclude one-time dev capex from per-patient cost
            per_cost = (total_costs - dev_capex)/active_pts if active_pts else 0.0
            per_margin = per_rev - per_cost

            rows.append({
                "Month": m, "State": state, "VendorActive": vendor_name,
                "New Patients": new_pts, "Total Patients": active_pts,
                "Total Revenue": net, "Total Costs": total_costs, "EBITDA": ebitda, 
                "Free Cash Flow": free_cash_flow, "Cash Balance": cash,
                "Platform Cost": platform, "Hardware Cost": hardware, "Software Fee": software_fee,
                "Overhead": overhead, "Staffing Cost": staffing, 
                "Dev Capex": dev_capex, "Infrastructure Capex": infrastructure_capex,
                "Accounts Receivable": wc["accounts_receivable"], "Inventory": wc["inventory"],
                "Accounts Payable": wc["accounts_payable"], "Net Working Capital": wc["net_working_capital"],
                "Change in NWC": change_in_nwc,
                "Per-Patient Revenue": per_rev, "Per-Patient Cost": per_cost, "Per-Patient Margin": per_margin,
                "RPM_Minutes_Demand": rpm_minutes_demand, "Staff_Minutes_Capacity": staff_minutes_capacity,
                # Individual billing code revenues for analysis
                "Rev_99453": rev_setup * util["collection_rate"], "Rev_99454": rev_99454 * util["collection_rate"],
                "Rev_99457": rev_99457 * util["collection_rate"], "Rev_99458": rev_99458 * util["collection_rate"],
                "Rev_99091": rev_99091 * util["collection_rate"], "Rev_99490": rev_99490 * util["collection_rate"],
                "Rev_99439": rev_99439 * util["collection_rate"], "Rev_99426": rev_99426 * util["collection_rate"],
                "Rev_99427": rev_99427 * util["collection_rate"], "Rev_99495": rev_99495 * util["collection_rate"],
                "Rev_99496": rev_99496 * util["collection_rate"], "Rev_Theoretical": (rev_alzheimers + rev_mental_health + rev_preventive) * util["collection_rate"],
            })

    df = pd.DataFrame(rows)
    df["Year"] = (df["Month"] - 1)//12 + 1
    return df

# Legacy single-state model for backward compatibility
def run_model(rates, util, settings):
    # Convert to multi-state format for compatibility
    states = {"Virginia": {"start_month": 1, "initial_patients": settings["initial_patients"]}}
    gpci = {"Virginia": settings.get("gpci", 1.0)}
    homes = {"Virginia": settings["initial_homes"]}
    
    return run_projection(states, gpci, homes, rates, util, settings)

def summarize(df):
    kpi = pd.DataFrame([{
        "Months": int(df["Month"].max()),
        "Ending Patients": int(df["Total Patients"].max()),
        "Cumulative Revenue": float(df["Total Revenue"].sum()),
        "Cumulative EBITDA": float(df["EBITDA"].sum()),
        "Ending Cash": float(df["Cash Balance"].iloc[-1])
    }])
    return {"kpi": kpi}