import model

print("=== CRITICAL BUG TEST ===")

# Test with 10K patients, Virginia only
patients = 10000

# 1. TEST STAFFING COSTS
clinical_pmpm = 40  # Default
admin_pmpm = 8     # Default  
family_pmpm = 6    # Default
director_annual = 70000  # Default

clinical_monthly = clinical_pmpm * patients
admin_monthly = admin_pmpm * patients
family_monthly = family_pmpm * patients
director_monthly = director_annual / 12

total_staffing = (clinical_monthly + admin_monthly + family_monthly + director_monthly) * 0.85  # AI efficiency

print(f"STAFFING COSTS for {patients:,} patients:")
print(f"Clinical: ${clinical_monthly:,}/month (${clinical_pmpm}/patient)")  
print(f"Admin: ${admin_monthly:,}/month (${admin_pmpm}/patient)")
print(f"Family: ${family_monthly:,}/month (${family_pmpm}/patient)")
print(f"Director: ${director_monthly:,}/month")
print(f"TOTAL: ${total_staffing:,.0f}/month = ${total_staffing*12:,.0f}/year")
print()

# 2. TEST REVENUE PER PATIENT
rates = model.default_rates()
util = model.default_util()

# Calculate typical revenue per patient per month
rev_per_patient = 0
rev_per_patient += rates["99454"]["rate"] * util["rpm_16day"]  # Device supply
rev_per_patient += rates["99457"]["rate"] * util["rpm_20min"]  # Basic RPM
rev_per_patient += rates["99458"]["rate"] * rates["99458"]["multiplier"] * util["rpm_40min"]  # Additional RPM
rev_per_patient += rates["99091"]["rate"] * util["md_99091"]  # Physician review
rev_per_patient += rates["99490"]["rate"] * util["ccm_99490"]  # Basic CCM
rev_per_patient += rates["99439"]["rate"] * rates["99439"]["multiplier"] * util["ccm_99439"]  # Additional CCM

total_revenue = rev_per_patient * patients * 0.95  # Collection rate

print(f"REVENUE for {patients:,} patients:")
print(f"Revenue per patient: ${rev_per_patient:.0f}/month")
print(f"Total revenue: ${total_revenue:,.0f}/month")
print()

# 3. CALCULATE EBITDA
ebitda = total_revenue - total_staffing
ebitda_margin = (ebitda / total_revenue) * 100 if total_revenue > 0 else 0

print(f"EBITDA CALCULATION:")
print(f"Revenue: ${total_revenue:,.0f}")
print(f"Staffing: ${total_staffing:,.0f}")
print(f"EBITDA: ${ebitda:,.0f}")
print(f"EBITDA Margin: {ebitda_margin:.1f}%")

if ebitda < 0:
    print("❌ NEGATIVE EBITDA - Model is broken!")
if total_staffing > total_revenue * 0.5:
    print("❌ Staffing costs too high - over 50% of revenue!")