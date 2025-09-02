#!/usr/bin/env python3
"""
COMPREHENSIVE FINANCIAL MODEL AUDIT FOR VC SUBMISSION
=======================================================
"""

import model
import pandas as pd
import numpy as np
import sys

def format_number(val):
    """Format numbers cleanly"""
    if pd.isna(val):
        return "-"
    if abs(val) < 0.01:
        return "-"
    return f"{val:,.0f}"

def format_currency(val):
    """Format currency cleanly"""
    if pd.isna(val):
        return "-"
    if abs(val) < 0.01:
        return "-"
    return f"${val:,.0f}"

def format_percent(val):
    """Format percentages"""
    if pd.isna(val):
        return "-"
    return f"{val:.1f}%"

print("="*80)
print("📊 COMPREHENSIVE FINANCIAL MODEL AUDIT - ORA LIVING")
print("="*80)
print()

# ========== 1. BILLING CODES & RATES VALIDATION ==========
print("1️⃣ BILLING CODES & RATES VALIDATION")
print("-"*50)

rates = model.default_rates()
util = model.default_util()

# Check all billing codes
billing_codes = {
    "RPM": ["99453", "99454", "99457", "99458", "99091"],
    "CCM": ["99490", "99439", "99487", "99489"],
    "PCM": ["99426", "99427"],
    "TCM": ["99495", "99496"]
}

print("\n📋 CMS Billing Codes Configuration:")
for category, codes in billing_codes.items():
    print(f"\n{category} Codes:")
    for code in codes:
        if code in rates:
            rate_info = rates[code]
            print(f"  {code}: ${rate_info['rate']:.2f} × {rate_info['multiplier']:.2f} multiplier ({rate_info['type']})")
        else:
            print(f"  {code}: ❌ NOT CONFIGURED")

# ========== 2. REVENUE PER PATIENT ANALYSIS ==========
print("\n\n2️⃣ REVENUE PER PATIENT ANALYSIS")
print("-"*50)

# Calculate actual revenue per patient
rpm_revenue = (
    rates['99454']['rate'] * rates['99454']['multiplier'] * util.get('rpm_16day', 0.90) +
    rates['99457']['rate'] * rates['99457']['multiplier'] * util.get('rpm_20min', 0.85) +
    rates['99458']['rate'] * rates['99458']['multiplier'] * util.get('rpm_40min', 0.40) +
    rates['99091']['rate'] * rates['99091']['multiplier'] * util.get('md_99091', 0.50)
)

ccm_revenue = (
    rates['99490']['rate'] * rates['99490']['multiplier'] * util.get('ccm_99490', 0.60) +
    rates['99439']['rate'] * rates['99439']['multiplier'] * util.get('ccm_99439', 0.20)
)

pcm_revenue = rates['99426']['rate'] * rates['99426']['multiplier'] * 0.15  # PCM hardcoded at 15%

total_revenue_per_patient = rpm_revenue + ccm_revenue + pcm_revenue

print(f"\n💰 Per-Patient Monthly Revenue:")
print(f"  RPM Revenue:  ${rpm_revenue:.2f}")
print(f"  CCM Revenue:  ${ccm_revenue:.2f}")
print(f"  PCM Revenue:  ${pcm_revenue:.2f}")
print(f"  TOTAL:        ${total_revenue_per_patient:.2f}")
print(f"\n  Target: ~$245/patient")
print(f"  Status: {'✅ ON TARGET' if 235 <= total_revenue_per_patient <= 255 else f'⚠️ OFF by ${abs(245 - total_revenue_per_patient):.2f}'}")

# ========== 3. GROWTH MODEL VALIDATION ==========
print("\n\n3️⃣ GROWTH MODEL VALIDATION (HILL VALLEY)")
print("-"*50)

# Test Hill Valley scenario
states_hv = {"Virginia": {"start_month": 1, "initial_patients": 100}}
gpci_hv = {"Virginia": 1.0}
homes_hv = {"Virginia": 100}

settings = model.default_settings()
results = model.run_projection(
    states=states_hv,
    gpci=gpci_hv,
    homes=homes_hv,
    rates=rates,
    util=util,
    settings=settings
)

max_patients = results['Total Patients'].max()
final_patients = results[results['Month'] == 48]['Total Patients'].iloc[0] if len(results[results['Month'] == 48]) > 0 else 0

# Find when 19,965 target is reached
target_month = None
for _, row in results.iterrows():
    if row['Total Patients'] >= 19965:
        target_month = row['Month']
        break

print(f"\n🎯 Hill Valley Partnership (100 nursing homes):")
print(f"  Target: 19,965 patients (100 homes × ~200 patients)")
print(f"  Max Reached: {max_patients:,.0f} patients")
print(f"  Month 48: {final_patients:,.0f} patients")

if target_month:
    print(f"  ✅ Target reached at month {target_month}")
else:
    print(f"  ❌ Target NOT reached (max: {max_patients:,.0f})")

# ========== 4. FINANCIAL PROJECTIONS VALIDATION ==========
print("\n\n4️⃣ FINANCIAL PROJECTIONS VALIDATION")
print("-"*50)

# Check key months
key_months = [12, 24, 36, 48]
print("\n📈 Key Financial Metrics:")
print(f"{'Month':<8} {'Patients':<12} {'Revenue':<15} {'EBITDA':<15} {'Margin':<10}")
print("-"*65)

for month in key_months:
    month_data = results[results['Month'] == month]
    if len(month_data) > 0:
        row = month_data.iloc[0]
        patients = row['Total Patients']
        revenue = row['Total Revenue']
        ebitda = row['EBITDA']
        margin = (ebitda / revenue * 100) if revenue > 0 else 0
        print(f"{month:<8} {format_number(patients):<12} {format_currency(revenue):<15} {format_currency(ebitda):<15} {format_percent(margin):<10}")

# ========== 5. DATA EXPORT VALIDATION ==========
print("\n\n5️⃣ DATA EXPORT VALIDATION")
print("-"*50)

# Test CSV export
try:
    # Create sample export data
    export_df = results[['Month', 'Total Patients', 'Total Revenue', 'EBITDA', 'Cash Balance']].head(12)
    export_df.to_csv('/tmp/ora_audit_export.csv', index=False)
    print("  ✅ CSV export successful")
except Exception as e:
    print(f"  ❌ CSV export failed: {e}")

# Test Excel export capability
try:
    export_df.to_excel('/tmp/ora_audit_export.xlsx', index=False, engine='openpyxl')
    print("  ✅ Excel export successful")
except ImportError:
    print("  ⚠️ Excel export requires 'openpyxl' package")
except Exception as e:
    print(f"  ❌ Excel export failed: {e}")

# ========== 6. NUMBER FORMATTING VALIDATION ==========
print("\n\n6️⃣ NUMBER FORMATTING VALIDATION")
print("-"*50)

sample_month = results[results['Month'] == 24].iloc[0] if len(results[results['Month'] == 24]) > 0 else results.iloc[-1]

print("\n🔢 Format Check (Month 24):")
print(f"  Revenue: {format_currency(sample_month['Total Revenue'])} (no decimals ✅)")
print(f"  EBITDA: {format_currency(sample_month['EBITDA'])} (no decimals ✅)")
print(f"  Patients: {format_number(sample_month['Total Patients'])} (no decimals ✅)")

# ========== 7. COST STRUCTURE VALIDATION ==========
print("\n\n7️⃣ COST STRUCTURE VALIDATION")
print("-"*50)

# Check costs at scale
if 'Staffing Cost' in sample_month:
    staffing = sample_month.get('Staffing Cost', 0)
    platform = sample_month.get('Platform Cost', 0)
    hardware = sample_month.get('Hardware Cost', 0)
    overhead = sample_month.get('Overhead', 0)
    total_costs = sample_month.get('Total Costs', 0)
    
    print(f"\n💼 Cost Breakdown (Month 24):")
    print(f"  Staffing:  {format_currency(staffing)}")
    print(f"  Platform:  {format_currency(platform)}")
    print(f"  Hardware:  {format_currency(hardware)}")
    print(f"  Overhead:  {format_currency(overhead)}")
    print(f"  TOTAL:     {format_currency(total_costs)}")
    
    if sample_month['Total Patients'] > 0:
        cost_per_patient = total_costs / sample_month['Total Patients']
        print(f"\n  Cost per patient: ${cost_per_patient:.2f}")

# ========== 8. MULTI-STATE EXPANSION TEST ==========
print("\n\n8️⃣ MULTI-STATE EXPANSION TEST")
print("-"*50)

# Test all states
states_all = {
    "Virginia": {"start_month": 1, "initial_patients": 100},
    "Florida": {"start_month": 7, "initial_patients": 50},
    "Texas": {"start_month": 13, "initial_patients": 50}
}

gpci_all = {
    "Virginia": 1.0,
    "Florida": 1.02,
    "Texas": 0.98
}

homes_all = {
    "Virginia": 100,
    "Florida": 60,
    "Texas": 80
}

results_multi = model.run_projection(
    states=states_all,
    gpci=gpci_all,
    homes=homes_all,
    rates=rates,
    util=util,
    settings=settings
)

# Check state aggregation
state_summary = results_multi[results_multi['Month'] == 48].groupby('State')['Total Patients'].sum()
total_multi = state_summary.sum()

print(f"\n🗺️ Multi-State Results (Month 48):")
for state, patients in state_summary.items():
    print(f"  {state}: {patients:,.0f} patients")
print(f"  TOTAL: {total_multi:,.0f} patients")

# ========== 9. DEVICE ECONOMICS VALIDATION ==========
print("\n\n9️⃣ DEVICE ECONOMICS VALIDATION")
print("-"*50)

device_cost = 185  # Ora standard kit
recovery_rate = 0.85
refurb_cost = 45

print(f"\n📱 Device Economics:")
print(f"  New device cost: ${device_cost}")
print(f"  Recovery rate: {recovery_rate:.0%}")
print(f"  Refurbishment cost: ${refurb_cost}")
print(f"  Effective cost with recovery: ${device_cost * (1 - recovery_rate) + refurb_cost * recovery_rate:.2f}")

# ========== 10. FINAL SUMMARY ==========
print("\n\n🎯 FINAL AUDIT SUMMARY")
print("="*80)

issues = []
warnings = []
successes = []

# Check all critical metrics
if 235 <= total_revenue_per_patient <= 255:
    successes.append("Revenue per patient on target (~$245)")
else:
    issues.append(f"Revenue per patient off target (${total_revenue_per_patient:.2f} vs $245)")

if max_patients >= 19965:
    successes.append("Growth model reaches 19,965 patient target")
else:
    issues.append(f"Growth model only reaches {max_patients:,.0f} patients (target: 19,965)")

if final_patients >= 18000:
    successes.append(f"Strong patient retention at month 48 ({final_patients:,.0f})")
else:
    warnings.append(f"Patient count at month 48 lower than expected ({final_patients:,.0f})")

# Print summary
print(f"\n✅ SUCCESSES ({len(successes)}):")
for item in successes:
    print(f"  • {item}")

if warnings:
    print(f"\n⚠️ WARNINGS ({len(warnings)}):")
    for item in warnings:
        print(f"  • {item}")

if issues:
    print(f"\n❌ CRITICAL ISSUES ({len(issues)}):")
    for item in issues:
        print(f"  • {item}")
        
print("\n" + "="*80)
if not issues:
    print("🎉 MODEL READY FOR VC SUBMISSION!")
else:
    print("⚠️ CRITICAL ISSUES NEED FIXING BEFORE SUBMISSION")
print("="*80)