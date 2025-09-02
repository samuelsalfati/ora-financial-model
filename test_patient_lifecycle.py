import model

print("PATIENT LIFECYCLE REVENUE TEST")
print("="*60)

# Test with 100 new patients
new_patients = 100
existing_patients = 1000

rates = model.default_rates()
util = model.default_util()

print("NEW PATIENT REVENUE (First Month Only):")
tcm_moderate = rates["99495"]["rate"] * util["tcm_99495"] * new_patients
tcm_high = rates["99496"]["rate"] * util["tcm_99496"] * new_patients
rpm_setup = rates["99453"]["rate"] * util["rpm_setup"] * new_patients
print(f"TCM 99495 (60% of new): ${tcm_moderate:,.0f}")
print(f"TCM 99496 (30% of new): ${tcm_high:,.0f}")
print(f"RPM Setup 99453 (95% of new): ${rpm_setup:,.0f}")
print(f"TOTAL ONE-TIME: ${tcm_moderate + tcm_high + rpm_setup:,.0f}")
print()

print("MONTHLY RECURRING REVENUE (All Active Patients):")
total_active = existing_patients + new_patients
rpm_device = rates["99454"]["rate"] * util["rpm_16day"] * total_active
rpm_management = rates["99457"]["rate"] * util["rpm_20min"] * total_active
rpm_additional = rates["99458"]["rate"] * rates["99458"]["multiplier"] * util["rpm_40min"] * total_active
rpm_data_review = rates["99091"]["rate"] * util["md_99091"] * total_active
ccm_base = rates["99490"]["rate"] * util["ccm_99490"] * total_active
ccm_add = rates["99439"]["rate"] * rates["99439"]["multiplier"] * util["ccm_99439"] * total_active

print(f"RPM Device 99454 (all patients): ${rpm_device:,.0f}")
print(f"RPM Management 99457 (all patients): ${rpm_management:,.0f}")
print(f"RPM Additional 99458 (some patients): ${rpm_additional:,.0f}")
print(f"RPM Data Review 99091 (physician review): ${rpm_data_review:,.0f}")
print(f"CCM Base 99490 (eligible patients): ${ccm_base:,.0f}")
print(f"CCM Additional 99439 (some patients): ${ccm_add:,.0f}")
print(f"TOTAL MONTHLY: ${rpm_device + rpm_management + rpm_additional + rpm_data_review + ccm_base + ccm_add:,.0f}")
print()

print("REVENUE BREAKDOWN:")
one_time = tcm_moderate + tcm_high + rpm_setup
monthly = rpm_device + rpm_management + rpm_additional + rpm_data_review + ccm_base + ccm_add
print(f"From {new_patients} NEW patients (one-time): ${one_time:,.0f}")
print(f"From {total_active} TOTAL patients (monthly): ${monthly:,.0f}")
print(f"TOTAL REVENUE THIS MONTH: ${one_time + monthly:,.0f}")
print()

print("PER-PATIENT ECONOMICS:")
print(f"New patient value (first month): ${(one_time / new_patients) + (monthly / total_active):.0f}")
print(f"Existing patient value (monthly): ${monthly / total_active:.0f}")
print()

print("HILL VALLEY EXAMPLE (Month 24):")
print("5,000 existing patients + 400 new patients")
hill_valley_new = 400
hill_valley_existing = 5000
hv_one_time = (rates["99495"]["rate"] * util["tcm_99495"] + 
               rates["99496"]["rate"] * util["tcm_99496"] + 
               rates["99453"]["rate"] * util["rpm_setup"]) * hill_valley_new
hv_monthly = ((rpm_device + rpm_management + rpm_additional + rpm_data_review + ccm_base + ccm_add) / total_active) * (hill_valley_existing + hill_valley_new)
print(f"One-time revenue from 400 new: ${hv_one_time:,.0f}")
print(f"Monthly revenue from 5,400 total: ${hv_monthly:,.0f}")
print(f"TOTAL MONTH 24 REVENUE: ${hv_one_time + hv_monthly:,.0f}")