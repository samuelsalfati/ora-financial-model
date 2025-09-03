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
            tiers=[(0, 15.0), (501, 22.0), (2001, 30.0)],   # More realistic vendor pricing
            flat_pmpm=None,
            monthly_software_fee=2000.0,                   # EDITABLE
            hardware_kits={"Kit-300": 300.0, "Kit-400": 400.0, "Kit-500": 500.0},  # Device costs
            dev_capex=0.0,
        ),
        "CareSimple": VendorConfig(
            name="CareSimple",
            tiers=None,
            flat_pmpm=15.0,                                # EDITABLE in UI
            monthly_software_fee=2000.0,                   # EDITABLE
            hardware_kits={"Kit-300": 300.0, "Kit-400": 400.0, "Kit-500": 500.0},  # Device costs
            dev_capex=0.0,
        ),
        "Ora": VendorConfig(
            name="Ora",
            tiers=None,
            flat_pmpm=5.0,                                 # EDITABLE
            monthly_software_fee=0.0,                      # EDITABLE
            hardware_kits={"Ora-Std": 300.0},              # Updated device cost from $185 to $300
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
        "99091": {"rate":51.29, "type":"monthly", "multiplier":1.0},    # Enhanced data interpretation (30 days)
        # CCM (Enhanced with complex care management for high-acuity patients)
        "99490": {"rate":65.00, "type":"monthly", "multiplier":1.0},    # Base 20 min CCM (1x monthly)
        "99439": {"rate":48.50, "type":"monthly", "multiplier":1.2},    # Additional CCM sessions (avg 1.2x monthly)
        "99487": {"rate":128.44, "type":"monthly", "multiplier":1.0},   # Complex CCM (60 minutes) for high-acuity patients
        "99489": {"rate":69.13, "type":"monthly", "multiplier":1.0},    # Additional complex CCM (30 minutes) follow-up sessions
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
        # RPM utilization rates - OPTIMIZED FOR $245/PATIENT TARGET
        "rpm_setup": 0.95,   # 99453 setup rate for new patients
        "rpm_16day": 0.95,   # 99454 device supply eligibility (95% of patients) - INCREASED
        "rpm_20min": 0.92,   # 99457 base treatment management (92% utilization) - INCREASED
        "rpm_40min": 0.55,   # 99458 additional sessions (55% get extra time) - INCREASED
        "md_99091":  0.65,   # 99091 physician review rate - INCREASED
        # CCM utilization rates (enhanced with patient acuity progression model)
        "ccm_99490": 0.75,   # Base CCM eligibility - INCREASED
        "ccm_99439": 0.35,   # Additional CCM sessions (multiplied by rate multiplier) - INCREASED
        # Complex CCM utilization (dynamic billing optimization for high-acuity patients)
        "ccm_99487": 0.25,   # Complex CCM eligibility (patients with worsening conditions)
        "ccm_99489": 0.15,   # Additional complex CCM sessions for ongoing care
        "data_99091": 0.40,  # Enhanced data interpretation services with AI-assisted analysis
        # PCM utilization rates (theoretical upside)
        "pcm_99426": 0.15,   # Base PCM eligibility
        "pcm_99427": 0.08,   # Additional PCM sessions (multiplied by rate multiplier)
        # TCM utilization rates (should cover hardware costs for new patients)
        "tcm_99495": 0.60,   # 60% of new patients get moderate complexity TCM
        "tcm_99496": 0.30,   # 30% of new patients get high complexity TCM
        # Theoretical billing utilization
        "alzheimers_prevention": 0.05,   # Advanced Alzheimer's care eligibility
        "mental_health_support": 0.10,   # Mental health service eligibility  
        "preventive_care": 0.08,          # Enhanced preventive care eligibility
        # Financial assumptions
        "collection_rate": 0.95,          # 95% collection rate (5% bad debt)
    }

def default_multi_state_config():
    """
    Aggressive multi-state expansion following Refua model.
    Virginia: 10,000 patients by Year 2 (150 patients per home, 40 homes initially, aggressive growth)
    """
    return {
        "Virginia": {"start_month": 1, "initial_patients": 100, "initial_homes": 100, "gpci": 1.00, "active": True},  # Hill Valley proof of concept
        "Florida": {"start_month": 25, "initial_patients": 500, "initial_homes": 60, "gpci": 1.05, "active": False},  # Launch after Hill Valley proof
        "Texas": {"start_month": 30, "initial_patients": 500, "initial_homes": 80, "gpci": 1.03, "active": False},  # Rapid expansion phase  
        "New York": {"start_month": 36, "initial_patients": 500, "initial_homes": 50, "gpci": 1.08, "active": False},  # Premium markets
        "California": {"start_month": 42, "initial_patients": 500, "initial_homes": 70, "gpci": 1.10, "active": False},  # West coast expansion
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
        # Time horizon and growth - Refua aggressive model (10,000 patients by Year 4)
        "months": 60,
        # REFUA MODEL - Hill Valley Partnership
        "initial_patients": 100,   # 6-month pilot program
        "pilot_months": 6,         # Pilot phase duration
        "hill_valley_monthly_discharges": 1200,  # Total monthly discharges from 100 Hill Valley homes
        "initial_capture_rate": 0.70,  # 70% eligibility/capture rate initially
        "target_capture_rate": 1.0,    # Target 100% capture of eligible patients
        "post_pilot_monthly_intake": 840,  # Calculated: 1200 * 0.70
        "monthly_attrition": 0.03, # 3% monthly attrition (realistic for post-discharge patients)
        "initial_homes": 40,
        "home_growth_per_year": 1,
        "patients_per_home_growth": 0.05,
        
        # Geographic and regulatory
        "gpci": 1.00,  # Virginia base GPCI
        
        # Operating costs - realistic scaling with caps
        "overhead_base": 50000.0,      # Base overhead (legal, accounting, insurance, facilities)
        "overhead_per_patient": 8.0,   # Additional overhead per patient (IT, compliance, data, support)
        "overhead_cap": 200000.0,      # Cap total overhead at $200K/month (economies of scale)
        "executive_salaries_threshold": 5000,  # Patient count when executives needed
        "marketing_budget_percent": 0.20,      # 20% of revenue for marketing/acquisition
        "initial_cash": 1_500_000,  # Starting capital
        
        # Enhanced staffing model with AI-driven efficiency optimization
        "staff_minutes_available_per_month": 160*60,  # per FTE (40 hrs/week * 4 weeks * 60 min)
        "staff_fte": 3,                               # Initial FTE count
        "staff_fte_growth_every_12m": 1,              # Staff scaling cadence
        "staffing_pmpm": 15.0,                        # Total staffing PMPM target
        # Modern staffing breakdown - ACTUAL RATIOS WITH SOFTWARE
        # 1 RN per 350 patients: $90k/year ÷ 12 ÷ 350 = $21.43 PMPM
        "clinical_staff_pmpm": 21.43,                 # RNs at 1:350 ratio with Ora software
        "family_care_liaisons_pmpm": 10.0,            # Family engagement specialists 
        "admin_staff_pmpm": 15.0,                     # Support staff at 1:150 ratio
        "ai_efficiency_factor": 0.90,                 # AI tools reduce total costs by 10%
        "medical_directors_base": 70000,              # Base salary per medical director  
        "medical_directors_per_state": 15000,         # Additional cost per state beyond first 3
        # Regional expansion costs with management hierarchy
        "head_of_state_salary": 12000,               # Head of State per state ($144K annual)
        "manager_salary": 7500,                      # Manager salary ($90K annual)
        "patients_per_manager": 2500,                # 1 manager per 2,500 patients
        "state_licensing_annual": 25000,             # Annual licensing/compliance per state
        "state_setup_cost": 50000,                   # One-time setup cost per new state
        
        # Vendor configuration
        "initial_vendor": "Impilo",      # "Impilo" | "CareSimple" | "Ora"
        "migration_month": None,         # e.g., 18 to switch to Ora
        
        # Device management
        "device_recovery_rate": 0.85,    # 85% of devices recovered when patient leaves
        "device_refurb_cost": 50,        # Cost to refurbish recovered device
        "device_logistics_cost": 25,     # Shipping/logistics per device (both ways)
        "device_depreciation_months": 12, # Devices depreciate over 12 months (fast depreciation)
        "device_useful_life": 24,        # Devices last 24 months before replacement needed
        "vendor_selected_kit": {         # hardware kit selection per vendor (aggressive $300 pricing)
            "Impilo": "Kit-300",
            "CareSimple": "Kit-300", 
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

def _calculate_enhanced_staffing_costs(active_patients, active_states, settings):
    """
    Enhanced staffing model with specialized roles and AI efficiency gains.
    
    Based on Ora's technology platform:
    - 1 RN can manage 350 patients (scaling to 500 with full AI)
    - Medical directors oversee 3 states each
    - Family Care Liaisons enhance patient engagement
    - AI automation reduces administrative overhead by 70%
    """
    # Core clinical staffing - Use actual settings values
    # With software: 1 RN per 350 patients. RN cost ~$90k/year = $7500/month
    # So PMPM = $7500 / 350 = ~$21.43 PMPM
    clinical_cost = settings.get("clinical_staff_pmpm", 21.43) * active_patients
    
    # Family Care Liaisons for patient/family engagement
    family_liaison_cost = settings.get("family_care_liaisons_pmpm", 10.0) * active_patients
    
    # Administrative support with AI automation (1:150 ratio)
    admin_cost = settings.get("admin_staff_pmpm", 15.0) * active_patients
    
    # Medical Directors (1 per 3 states, base + additional)
    states_per_director = settings.get("states_per_medical_director", 3)
    directors_needed = max(1, (len(active_states) + states_per_director - 1) // states_per_director)
    
    base_director_salary = settings.get("medical_director_base_salary", 70000)
    additional_state_cost = settings.get("medical_director_additional_state", 15000)
    
    # Calculate medical director costs: base for first 3 states, additional for excess
    excess_states = max(0, len(active_states) - 3 * directors_needed)
    director_annual_cost = (directors_needed * base_director_salary + 
                           excess_states * additional_state_cost)
    director_monthly_cost = director_annual_cost / 12
    
    # Apply AI efficiency factor (15% reduction through automation)
    ai_efficiency = settings.get("ai_efficiency_factor", 0.85)
    total_before_ai = clinical_cost + family_liaison_cost + admin_cost + director_monthly_cost
    total_after_ai = total_before_ai * ai_efficiency
    
    return total_after_ai

def _calculate_working_capital(monthly_revenue, monthly_costs, settings):
    """
    Realistic RPM/CCM working capital for established healthcare business.
    
    Returns dict with A/R, Inventory, A/P, and Net Working Capital
    """
    # Conservative working capital for established RPM business
    medicare_pct = settings.get("payer_mix_medicare", 0.65)  
    commercial_pct = 1 - medicare_pct
    dso_medicare = settings.get("dso_medicare", 45)
    dso_commercial = settings.get("dso_commercial", 75)
    
    blended_dso = (medicare_pct * dso_medicare) + (commercial_pct * dso_commercial)
    
    # More conservative A/R calculation for established business
    # RPM payments are more predictable than typical healthcare
    ar_months = min(blended_dso / 45, 1.0)  # Cap at 1 month, use 45-day divisor
    accounts_receivable = monthly_revenue * ar_months
    
    # RPM businesses have minimal other working capital needs
    inventory = 0  # Devices shipped direct, no inventory holding
    # More realistic A/P - established business pays faster
    accounts_payable = monthly_costs * 0.75  # 22.5 days average payment terms
    
    # Net Working Capital is just A/R minus A/P
    net_working_capital = accounts_receivable - accounts_payable
    
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
    
    # Track working capital properly (cumulative, company-wide)
    prev_total_nwc = 0

    dev_capex_done = False
    
    # Company-wide cash tracking
    month_cash_flows = {}  # Track cash flows by month to avoid double-counting

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
        
        # Initialize monthly cash flow aggregation
        month_cash_flows[m] = {"total_free_cash_flow": 0, "total_capex": 0, "total_nwc_change": 0}

        # Iterate states
        active_states = [s for s,conf in states.items() if m >= conf["start_month"]]
        for state, conf in states.items():
            if m < conf["start_month"]:
                continue

            g = gpci[state]
            homes_now = homes[state] + homes_per_year * ((m-1)//12)
            pph = 20 * (1+pph_growth)**((m-1)//12)
            # Set realistic max capacity - hard cap for Virginia
            theoretical_capacity = int(homes_now * pph)
            if state == "Virginia":
                max_patients = min(25000, theoretical_capacity + 20000)  # Virginia capped at 25K patients
            else:
                max_patients = max(theoretical_capacity, 50000)  # Other states capped at 50K

            if m == conf["start_month"]:
                new_pts = conf["initial_patients"]
                attrition_pts = 0
                # Initialize the state's patient count on first month
                total_patients[state] = new_pts
            else:
                # REFUA MODEL - Hill Valley Partnership Growth Logic
                monthly_attrition = settings.get("monthly_attrition", 0.03)
                attrition_pts = int(total_patients[state] * monthly_attrition)
                
                # Different growth phases
                pilot_months = settings.get("pilot_months", 6)
                post_pilot_intake = settings.get("post_pilot_monthly_intake", 400)
                
                # Growth logic applies to all states now (not just Virginia)
                if True:  # All states use discharge-based growth model
                    # PARTNERSHIP CONTINUOUS FLOW MODEL (each state has nursing home partnerships)
                    hill_valley_discharges = settings.get("hill_valley_monthly_discharges", 1200)  # Base discharge rate
                    initial_capture = settings.get("initial_capture_rate", 0.70)  # Higher initial capture
                    target_capture = settings.get("target_capture_rate", 1.0)
                    
                    # Calculate intake rates based on capture percentages
                    initial_intake = int(hill_valley_discharges * initial_capture)  # 840
                    target_intake = int(hill_valley_discharges * target_capture)    # 1200
                    
                    if m <= pilot_months:
                        # Pilot phase: stronger start to build momentum
                        new_pts = max(0, 100 + (m * 50))  # Faster pilot growth
                    elif m <= 12:
                        # Ramp-up phase: aggressive capture to reach critical mass
                        ramp_factor = (m - pilot_months) / (12 - pilot_months)
                        new_pts = max(0, int(initial_intake * (0.5 + ramp_factor * 0.5)))
                    elif m <= 24:
                        # Scaling phase: full capture to reach 19,965 target
                        # Month 13-24: Aggressive scaling
                        scale_factor = (m - 12) / 12
                        new_pts = int(initial_intake + (target_intake - initial_intake) * scale_factor * 1.5)
                    elif m <= 36:
                        # Growth phase: capturing full discharge volume plus expansion
                        # Use configurable multiplier to reach target
                        growth_mult = settings.get("growth_multiplier", 1.3)
                        new_pts = int(target_intake * growth_mult)
                    else:
                        # STEADY STATE: Capturing target percentage of Hill Valley discharges
                        base_intake = target_intake
                        
                        # Add some realistic variation (±10%)
                        import random
                        random.seed(m)  # Consistent randomness based on month
                        monthly_variation = random.uniform(0.9, 1.1)
                        
                        # CONTINUOUS FLOW MODEL - Cap at market target
                        # Virginia has 100 nursing homes continuously discharging patients
                        market_target = settings.get("max_patients", 19965)  # Allow override
                        
                        if total_patients[state] >= market_target:
                            # At target - just maintain patient base
                            # Only replace attrition to stay at target
                            new_pts = int(attrition_pts)  # Replace departing patients exactly
                        elif total_patients[state] > market_target * 0.8:  # Above 80% of target
                            # Approaching target, still strong intake from facilities
                            new_pts = int(base_intake * 0.9 * monthly_variation)
                        else:
                            # Full intake until we reach market target
                            new_pts = int(base_intake * monthly_variation)
                        
                        # Always at least replacing attrition to maintain patient base
                        new_pts = max(new_pts, int(attrition_pts))
                else:
                    # OTHER STATES - Same nursing home partnership model!
                    months_since_launch = m - conf["start_month"]
                    
                    if months_since_launch < 0:
                        new_pts = 0  # Not launched yet
                    elif months_since_launch == 0:
                        # Launch month - initial partnerships
                        new_pts = conf["initial_patients"]  # Start with 500 patients
                    elif months_since_launch <= 6:
                        # Ramp-up phase for new state
                        ramp_factor = months_since_launch / 6
                        state_intake = 300  # Each new state targets 300/month from partnerships
                        new_pts = max(100, int(state_intake * ramp_factor))
                    else:
                        # STEADY STATE: Every state has continuous SNF/ALF discharge flow!
                        state_intake = 300  # Base intake per state from partnerships
                        
                        # Add realistic variation
                        import random
                        random.seed(m + hash(state))  # Unique randomness per state
                        monthly_variation = random.uniform(0.9, 1.1)
                        
                        # Scale based on state size
                        if state == "Florida":
                            state_intake = 400  # Larger retiree population
                        elif state == "Texas":
                            state_intake = 350  # Big state
                        elif state == "California":
                            state_intake = 400  # Huge market
                        
                        # As state matures, find equilibrium
                        if total_patients[state] > 5000:
                            new_pts = int(state_intake * 0.8 * monthly_variation)
                        elif total_patients[state] > 3000:
                            new_pts = int(state_intake * 0.9 * monthly_variation)
                        else:
                            new_pts = int(state_intake * monthly_variation)
                        
                        # Always replace attrition at minimum
                        new_pts = max(new_pts, int(attrition_pts * 1.1))  # At least 10% growth over attrition
                
                # Apply attrition to existing patient base
                new_total = total_patients[state] - attrition_pts + new_pts
                
                # Cap at market target if specified 
                # Each state has its own market cap
                if state == "Virginia":
                    market_cap = settings.get("max_patients", 19965)
                    new_total = min(new_total, market_cap)
                elif state == "Florida":
                    # Florida can grow to its market potential
                    florida_cap = 25000  # Florida market cap
                    new_total = min(new_total, florida_cap)
                elif state == "Texas":
                    texas_cap = 30000  # Texas is huge
                    new_total = min(new_total, texas_cap)
                elif state == "New York":
                    ny_cap = 20000  # NY market cap
                    new_total = min(new_total, ny_cap)
                elif state == "California":
                    ca_cap = 25000  # CA market cap
                    new_total = min(new_total, ca_cap)
                else:
                    # Default cap for other states
                    new_total = min(new_total, 20000)
                
                total_patients[state] = max(0, new_total)
            
            # Don't reset if we already calculated the total above
            # This was a bug - it was overwriting the calculated growth!
            # if m == conf["start_month"]:
            #     total_patients[state] = new_pts
            
            active_pts = total_patients[state]

            # --- revenue calculation with multipliers ---
            include_theoretical = settings.get("include_theoretical", False)
            
            # CORE RPM REVENUE (Standard billing per CMS guidelines)
            rev_setup = rates["99453"]["rate"] * rates["99453"]["multiplier"] * util["rpm_setup"] * new_pts
            rev_99454 = g * rates["99454"]["rate"] * rates["99454"]["multiplier"] * util["rpm_16day"] * active_pts  
            rev_99457 = g * rates["99457"]["rate"] * rates["99457"]["multiplier"] * util["rpm_20min"] * active_pts
            rev_99458 = g * rates["99458"]["rate"] * rates["99458"]["multiplier"] * util["rpm_40min"] * active_pts  # Uses 1.35x multiplier
            rev_99091 = g * rates["99091"]["rate"] * rates["99091"]["multiplier"] * util["md_99091"] * active_pts
            
            # CORE CCM & PCM REVENUE (Standard billing per CMS guidelines)
            rev_99490 = g * rates["99490"]["rate"] * rates["99490"]["multiplier"] * util["ccm_99490"] * active_pts
            rev_99439 = g * rates["99439"]["rate"] * rates["99439"]["multiplier"] * util["ccm_99439"] * active_pts  # Uses 1.2x multiplier
            
            # PCM REVENUE (Principal Care Management - standard for single chronic conditions)
            rev_99426 = g * rates["99426"]["rate"] * rates["99426"]["multiplier"] * util.get("pcm_99426", 0.15) * active_pts
            rev_99427 = g * rates["99427"]["rate"] * rates["99427"]["multiplier"] * util.get("pcm_99427", 0.08) * active_pts
            
            # ENHANCED BILLING (Complex CCM for high-acuity patients - if enabled)
            enhanced_billing = settings.get("enhanced_billing", False)
            if enhanced_billing:
                # Complex CCM for patients with multiple chronic conditions requiring intensive management
                rev_99487 = g * rates["99487"]["rate"] * rates["99487"]["multiplier"] * util.get("ccm_99487", 0.25) * active_pts
                rev_99489 = g * rates["99489"]["rate"] * rates["99489"]["multiplier"] * util.get("ccm_99489", 0.15) * active_pts
            else:
                rev_99487 = rev_99489 = 0
            
            # TCM REVENUE (One-time for new patient transitions) 
            rev_99495 = rates["99495"]["rate"] * rates["99495"]["multiplier"] * util["tcm_99495"] * new_pts
            rev_99496 = rates["99496"]["rate"] * rates["99496"]["multiplier"] * util["tcm_99496"] * new_pts

            # REVENUE TOTAL (Core + Enhanced if enabled)
            gross = (rev_setup + rev_99454 + rev_99457 + rev_99458 + rev_99091 +
                     rev_99490 + rev_99439 + rev_99487 + rev_99489 + 
                     rev_99426 + rev_99427 + rev_99495 + rev_99496)
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
                
                # Smart device management with recovery
                recovery_rate = settings.get("device_recovery_rate", 0.85)
                refurb_cost = settings.get("device_refurb_cost", 50)
                logistics_cost = settings.get("device_logistics_cost", 25)
                
                # Calculate recovered devices from attrition
                recovered_devices = int(attrition_pts * recovery_rate)
                
                # Net new devices needed (accounting for recovered/refurbished)
                net_new_devices = max(0, new_pts - recovered_devices)
                
                # Hardware costs breakdown:
                # 1. New devices for net new patients ($300 each)
                # 2. Refurbishment for recovered devices ($50 each)
                # 3. Logistics for all device movements ($25 each way)
                # 4. TCM offset: ~$193.50 per new patient from TCM billing
                
                # Calculate gross device costs
                new_device_cost = kit_cost * net_new_devices  # $300 per new device
                refurb_costs = refurb_cost * min(recovered_devices, new_pts)  # $50 per refurb
                logistics_costs = logistics_cost * (new_pts + attrition_pts)  # $25 per movement
                
                # TCM offset calculation (billed in revenue, offset here for unit economics)
                # 60% get $192.50 (99495) + 30% get $260 (99496) = avg $193.50 per new patient
                tcm_offset = new_pts * 193.50 * util["collection_rate"]  # TCM revenue offsets device cost
                
                # Net hardware cost after TCM offset
                hardware_gross = new_device_cost + refurb_costs + logistics_costs
                hardware = max(0, hardware_gross - tcm_offset)  # Net cost after TCM offset
                
                # Charge software fee once per month (company-wide)
                software_fee = 0.0
                if not software_fee_charged and active_pts > 0 and vcfg.monthly_software_fee > 0:
                    software_fee = vcfg.monthly_software_fee
                    software_fee_charged = True

            # Realistic overhead scaling
            base_overhead = settings.get("overhead_base", 25000)
            per_patient_overhead = settings.get("overhead_per_patient", 2.0)
            
            # Add executive team costs at specific milestones
            executive_costs = 0
            if m >= 24 and active_pts > 3000:  # Month 24+ with significant scale
                # CMO hired first for growth
                executive_costs += 20000  # $240K annual
            if m >= 30 and active_pts > 5000:  # Month 30+ 
                # CTO for technology scaling
                executive_costs += 22000  # $264K annual
            if m >= 36 and active_pts > 8000:  # Month 36+
                # CFO for financial management 
                executive_costs += 18000  # $216K annual
            
            # Marketing budget as percentage of revenue
            marketing_percent = settings.get("marketing_budget_percent", 0.08)
            marketing_budget = net * marketing_percent
            
            # Apply overhead cap for economies of scale
            overhead_cap = settings.get("overhead_cap", 150000)
            overhead_before_cap = base_overhead + (per_patient_overhead * active_pts) + executive_costs + marketing_budget
            overhead = min(overhead_before_cap, overhead_cap)
            # Enhanced staffing model with specialized roles and AI efficiency
            staffing = _calculate_enhanced_staffing_costs(active_pts, active_states, settings)

            # State expansion costs with management hierarchy
            regional_costs = 0
            state_setup_costs = 0
            
            # Head of State for each active state
            head_of_state_monthly = settings.get("head_of_state_salary", 12000) * len(active_states)
            
            # Managers based on patient count (1 per 2,500 patients)
            patients_per_manager = settings.get("patients_per_manager", 2500)
            manager_salary = settings.get("manager_salary", 7500)
            managers_needed = max(1, (active_pts + patients_per_manager - 1) // patients_per_manager)  # Round up
            manager_monthly = manager_salary * managers_needed
            
            # Annual licensing/compliance costs per state
            licensing_monthly = (settings.get("state_licensing_annual", 25000) / 12) * len(active_states)
            
            # One-time state setup costs (charged in the launch month)
            if m == conf["start_month"] and state != "Virginia":  # No setup cost for first state
                state_setup_costs = settings.get("state_setup_cost", 50000)
            
            regional_costs = head_of_state_monthly + manager_monthly + licensing_monthly
            
            rpm_minutes_demand = active_pts * (20*util["rpm_20min"] + 20*util["rpm_40min"])
            staff_minutes_capacity = staff_fte * staff_minutes_available

            total_costs = platform + hardware + software_fee + overhead + staffing + regional_costs + state_setup_costs + dev_capex + infrastructure_capex
            ebitda = net - total_costs
            
            # Working Capital calculation with proper tracking
            wc = _calculate_working_capital(net, total_costs, settings)
            
            # Calculate CHANGE in working capital (not absolute amount)
            current_total_nwc = wc["net_working_capital"]
            change_in_nwc = current_total_nwc - prev_total_nwc
            prev_total_nwc = current_total_nwc
            
            # Free Cash Flow = EBITDA - Capex - Change in Working Capital
            capex_total = dev_capex + infrastructure_capex
            free_cash_flow = ebitda - capex_total - change_in_nwc
            
            # Accumulate monthly cash flows (company-wide)
            month_cash_flows[m]["total_free_cash_flow"] += free_cash_flow

            per_rev = net/active_pts if active_pts else 0.0
            # exclude one-time dev capex from per-patient cost
            per_cost = (total_costs - dev_capex)/active_pts if active_pts else 0.0
            per_margin = per_rev - per_cost

            # Determine growth phase for tracking
            if state == "Virginia":
                if m <= 6:
                    phase = "Pilot"
                elif m <= 12:
                    phase = "Ramp-up"
                elif m <= 24:
                    phase = "Hill Valley Scale"
                else:
                    phase = "National Expansion"
            else:
                phase = "Multi-State"
            
            rows.append({
                "Month": m, "State": state, "VendorActive": vendor_name, "Phase": phase,
                "New Patients": new_pts, "Total Patients": active_pts,
                "Total Revenue": net, "Total Costs": total_costs, "EBITDA": ebitda, 
                "Free Cash Flow": free_cash_flow, "Cash Balance": 0,  # Updated later at company level
                "Platform Cost": platform, "Hardware Cost": hardware, "Software Fee": software_fee,
                "Overhead": overhead, "Staffing Cost": staffing, 
                "Dev Capex": dev_capex, "Infrastructure Capex": infrastructure_capex,
                "Accounts Receivable": wc["accounts_receivable"], "Inventory": wc["inventory"],
                "Accounts Payable": wc["accounts_payable"], "Net Working Capital": wc["net_working_capital"],
                "Change in NWC": change_in_nwc,
                "Per-Patient Revenue": per_rev, "Per-Patient Cost": per_cost, "Per-Patient Margin": per_margin,
                "RPM_Minutes_Demand": rpm_minutes_demand, "Staff_Minutes_Capacity": staff_minutes_capacity,
                # Individual billing code revenues for analysis (Core services only)
                "Rev_99453": rev_setup * util["collection_rate"], "Rev_99454": rev_99454 * util["collection_rate"],
                "Rev_99457": rev_99457 * util["collection_rate"], "Rev_99458": rev_99458 * util["collection_rate"],
                "Rev_99091": rev_99091 * util["collection_rate"], "Rev_99490": rev_99490 * util["collection_rate"],
                "Rev_99439": rev_99439 * util["collection_rate"], "Rev_99495": rev_99495 * util["collection_rate"],
                "Rev_99496": rev_99496 * util["collection_rate"],
            })
        
        # Update company-wide cash balance once per month
        cash += month_cash_flows[m]["total_free_cash_flow"]
        
        # Update all rows for this month with the same cash balance
        for i, row in enumerate(rows):
            if row["Month"] == m:
                rows[i]["Cash Balance"] = cash

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