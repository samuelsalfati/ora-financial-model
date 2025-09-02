import model
import pandas as pd

print("="*80)
print("DASHBOARD ALIGNMENT & CONSISTENCY CHECK")
print("="*80)

# 1. Check Model Settings
settings = model.default_settings()
multi_state = model.default_multi_state_config()
rates = model.default_rates()
util = model.default_util()

print("\n1. MODEL SETTINGS CHECK")
print("-"*50)
print(f"Initial patients: {settings.get('initial_patients', 'MISSING')}")
print(f"Pilot months: {settings.get('pilot_months', 'MISSING')}")
print(f"Post-pilot intake: {settings.get('post_pilot_monthly_intake', 'MISSING')} patients/month")
print(f"Monthly attrition: {settings.get('monthly_attrition', 0) * 100:.1f}%")
print(f"Initial cash: ${settings.get('initial_cash', 0):,}")
print(f"Timeline: {settings.get('months', 60)} months")

print("\n2. VIRGINIA/HILL VALLEY CONFIGURATION")
print("-"*50)
virginia_config = multi_state.get("Virginia", {})
print(f"Start month: {virginia_config.get('start_month', 'ERROR')}")
print(f"Initial patients: {virginia_config.get('initial_patients', 'ERROR')}")
print(f"Initial homes: {virginia_config.get('initial_homes', 'ERROR')}")
print(f"GPCI: {virginia_config.get('gpci', 'ERROR')}")
print(f"Active by default: {virginia_config.get('active', 'ERROR')}")

# Check for consistency
if virginia_config.get('initial_patients', 0) != settings.get('initial_patients', 0):
    print(f"❌ MISMATCH: Virginia has {virginia_config.get('initial_patients')} but settings has {settings.get('initial_patients')}")

print("\n3. REVENUE PER PATIENT CALCULATION")
print("-"*50)
# Calculate actual revenue per patient
rpm_revenue = (
    rates["99454"]["rate"] * util["rpm_16day"] +
    rates["99457"]["rate"] * util["rpm_20min"] +
    rates["99458"]["rate"] * rates["99458"]["multiplier"] * util["rpm_40min"] +
    rates["99091"]["rate"] * util["md_99091"]
)
ccm_revenue = (
    rates["99490"]["rate"] * util["ccm_99490"] +
    rates["99439"]["rate"] * rates["99439"]["multiplier"] * util["ccm_99439"]
)
total_revenue_per_patient = (rpm_revenue + ccm_revenue) * util["collection_rate"]
print(f"RPM revenue: ${rpm_revenue:.2f}/patient/month")
print(f"CCM revenue: ${ccm_revenue:.2f}/patient/month")
print(f"Collection rate: {util['collection_rate']*100:.0f}%")
print(f"TOTAL: ${total_revenue_per_patient:.2f}/patient/month")

print("\n4. COST PER PATIENT CALCULATION")
print("-"*50)
clinical = settings.get("clinical_staff_pmpm", 0)
family = settings.get("family_care_liaisons_pmpm", 0)
admin = settings.get("admin_staff_pmpm", 0)
ai_efficiency = settings.get("ai_efficiency_factor", 0.85)
overhead_per_patient = settings.get("overhead_per_patient", 0)

staffing_cost = (clinical + family + admin) * ai_efficiency
print(f"Clinical: ${clinical}/patient")
print(f"Family: ${family}/patient")
print(f"Admin: ${admin}/patient")
print(f"AI efficiency: {ai_efficiency*100:.0f}%")
print(f"Total staffing: ${staffing_cost:.2f}/patient/month")
print(f"Overhead: ${overhead_per_patient}/patient/month")
print(f"Platform (Impilo): ~$8-23/patient/month")
print(f"ESTIMATED TOTAL: ${staffing_cost + overhead_per_patient + 15:.2f}/patient/month")

margin_per_patient = total_revenue_per_patient - (staffing_cost + overhead_per_patient + 15)
margin_percent = (margin_per_patient / total_revenue_per_patient) * 100
print(f"\nUNIT ECONOMICS:")
print(f"Revenue: ${total_revenue_per_patient:.2f}")
print(f"Cost: ${staffing_cost + overhead_per_patient + 15:.2f}")
print(f"Margin: ${margin_per_patient:.2f} ({margin_percent:.1f}%)")

print("\n5. GROWTH TRAJECTORY TEST")
print("-"*50)
# Run quick projection
states = {"Virginia": virginia_config}
gpci = {"Virginia": 1.0}
homes = {"Virginia": virginia_config.get("initial_homes", 100)}

df = model.run_projection(states, gpci, homes, rates, util, settings)

# Check key months
key_months = [1, 6, 12, 24, 36, 48, 60]
print("Month | Patients | Revenue  | EBITDA   | Phase")
for month in key_months:
    if month <= len(df):
        row = df[df['Month'] == month].iloc[0]
        phase = row.get('Phase', 'Unknown')
        print(f"{month:5d} | {row['Total Patients']:8.0f} | {row['Total Revenue']:8.0f} | {row['EBITDA']:8.0f} | {phase}")

# Final checks
print("\n6. CRITICAL ALIGNMENT ISSUES")
print("-"*50)
final_row = df[df['Month'] == df['Month'].max()].iloc[0]
final_patients = final_row['Total Patients']
final_revenue = final_row['Total Revenue']
final_ebitda = final_row['EBITDA']
final_margin = (final_ebitda / final_revenue * 100) if final_revenue > 0 else 0

issues = []
if final_margin > 50:
    issues.append(f"❌ EBITDA margin too high: {final_margin:.1f}% (should be 30-45%)")
if final_patients > 25000:
    issues.append(f"❌ Too many patients: {final_patients:.0f} (unrealistic for Virginia)")
if margin_percent > 60:
    issues.append(f"❌ Unit economics margin too high: {margin_percent:.1f}%")
if virginia_config.get('initial_patients') != settings.get('initial_patients'):
    issues.append(f"❌ Initial patient mismatch between configs")

if issues:
    for issue in issues:
        print(issue)
else:
    print("✅ All metrics appear aligned and realistic")

print("\n7. DASHBOARD DISPLAY VALUES")
print("-"*50)
print("Values that should appear in dashboard:")
print(f"Starting patients: 100 (pilot)")
print(f"Month 6: ~166 patients (end of pilot)")
print(f"Month 12: ~1,472 patients (ramp complete)")
print(f"Month 24: ~5,100 patients (Hill Valley scale)")
print(f"Revenue/patient: ~${total_revenue_per_patient:.0f}")
print(f"Cost/patient: ~${staffing_cost + overhead_per_patient + 15:.0f}")
print(f"Target EBITDA margin: 30-45%")

print("\n" + "="*80)
print("END OF ALIGNMENT CHECK")
print("="*80)