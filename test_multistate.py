import model
import pandas as pd

# Test single state vs multi-state economics
rates = model.default_rates()
util = model.default_util()
settings = model.default_settings()
settings['months'] = 48

print("MULTI-STATE EBITDA MARGIN ANALYSIS")
print("=" * 60)

# Test 1: Virginia only
states_va = {"Virginia": {"start_month": 1, "initial_patients": 100, "active": True}}
gpci_va = {"Virginia": 1.00}
homes_va = {"Virginia": 100}

df_va = model.run_projection(states_va, gpci_va, homes_va, rates, util, settings)
final_month_va = df_va[df_va['Month'] == 48].iloc[0]
revenue_va = final_month_va['Total Revenue']
costs_va = final_month_va['Total Costs']
ebitda_va = final_month_va['EBITDA']
margin_va = (ebitda_va / revenue_va * 100) if revenue_va > 0 else 0
patients_va = final_month_va['Total Patients']

print(f"\nVirginia Only (Month 48):")
print(f"  Patients: {patients_va:,.0f}")
print(f"  Revenue: ${revenue_va:,.0f}")
print(f"  Costs: ${costs_va:,.0f}")
print(f"  EBITDA: ${ebitda_va:,.0f}")
print(f"  EBITDA Margin: {margin_va:.1f}%")
print(f"  Cost per patient: ${costs_va/patients_va:.0f}")

# Test 2: Virginia + Florida
states_both = {
    "Virginia": {"start_month": 1, "initial_patients": 100, "active": True},
    "Florida": {"start_month": 1, "initial_patients": 100, "active": True}
}
gpci_both = {"Virginia": 1.00, "Florida": 1.05}
homes_both = {"Virginia": 100, "Florida": 60}

df_both = model.run_projection(states_both, gpci_both, homes_both, rates, util, settings)
final_month_both = df_both[df_both['Month'] == 48].iloc[0]
revenue_both = final_month_both['Total Revenue']
costs_both = final_month_both['Total Costs']
ebitda_both = final_month_both['EBITDA']
margin_both = (ebitda_both / revenue_both * 100) if revenue_both > 0 else 0
patients_both = final_month_both['Total Patients']

print(f"\nVirginia + Florida (Month 48):")
print(f"  Patients: {patients_both:,.0f}")
print(f"  Revenue: ${revenue_both:,.0f}")
print(f"  Costs: ${costs_both:,.0f}")
print(f"  EBITDA: ${ebitda_both:,.0f}")
print(f"  EBITDA Margin: {margin_both:.1f}%")
print(f"  Cost per patient: ${costs_both/patients_both:.0f}")

print("\n" + "=" * 60)
print("ISSUE ANALYSIS:")
print(f"  Margin with 1 state: {margin_va:.1f}%")
print(f"  Margin with 2 states: {margin_both:.1f}%")
print(f"  Difference: {margin_both - margin_va:.1f}%")

if margin_both < margin_va:
    print("\n❌ ERROR: Margin DECREASED with more states!")
    print("This suggests fixed costs are scaling incorrectly.")
else:
    print("\n✅ OK: Margin improved with scale as expected")

# Detailed cost breakdown
print("\nCOST BREAKDOWN PER PATIENT:")
print(f"  Virginia only: ${costs_va/patients_va:.2f}")
print(f"  With Florida: ${costs_both/patients_both:.2f}")

# Check specific cost categories
if 'Overhead' in df_va.columns:
    overhead_va = final_month_va.get('Overhead', 0)
    overhead_both = final_month_both.get('Overhead', 0)
    print(f"\nOVERHEAD COSTS:")
    print(f"  Virginia only: ${overhead_va:,.0f} total, ${overhead_va/patients_va:.2f}/patient")
    print(f"  With Florida: ${overhead_both:,.0f} total, ${overhead_both/patients_both:.2f}/patient")