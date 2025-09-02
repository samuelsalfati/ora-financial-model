import model
import pandas as pd

print("🗺️ MULTI-STATE CONFIGURATION AUDIT")
print("="*60)

# Test with Virginia state (Hill Valley partnership)
states = {
    "Virginia": {
        "start_month": 1,
        "initial_patients": 20
    }
}

gpci = {"Virginia": 1.0}
homes = {"Virginia": 100}  # 100 nursing homes

results = model.run_projection(
    states=states,
    gpci=gpci,
    homes=homes,
    rates=model.default_rates(),
    util=model.default_util(),
    settings=model.default_settings()
)

print("\n📊 VIRGINIA (HILL VALLEY) RESULTS:")
print(f"Nursing homes: {homes['Virginia']}")
print(f"Target: 100 homes × 200 patients = 20,000 patients")

max_patients = results['Total Patients'].max()
final_patients = results[results['Month'] == 48]['Total Patients'].iloc[0] if len(results[results['Month'] == 48]) > 0 else 0

print(f"\n🏁 OUTCOMES:")
print(f"Max patients reached: {max_patients:,.0f}")
print(f"Patients at month 48: {final_patients:,.0f}")

# Check monthly growth
print("\n📈 MONTHLY PATIENT GROWTH (sample):")
for month in [1, 6, 12, 18, 24, 30, 36, 42, 48]:
    month_data = results[results['Month'] == month]
    if len(month_data) > 0:
        patients = month_data['Total Patients'].iloc[0]
        revenue = month_data['Total Revenue'].iloc[0]
        print(f"  Month {month:2d}: {patients:6,.0f} patients, ${revenue:10,.0f} revenue")

# Test with all states active
print("\n" + "="*60)
print("🌎 ALL STATES ACTIVE TEST:")

states_all = {
    "Virginia": {"start_month": 1, "initial_patients": 20},
    "Florida": {"start_month": 7, "initial_patients": 10},
    "Texas": {"start_month": 13, "initial_patients": 10},
    "New York": {"start_month": 19, "initial_patients": 10},
    "California": {"start_month": 25, "initial_patients": 10}
}

gpci_all = {
    "Virginia": 1.0,
    "Florida": 1.02,
    "Texas": 0.98,
    "New York": 1.15,
    "California": 1.10
}

homes_all = {
    "Virginia": 100,
    "Florida": 60,
    "Texas": 80,
    "New York": 50,
    "California": 70
}

results_all = model.run_projection(
    states=states_all,
    gpci=gpci_all,
    homes=homes_all,
    rates=model.default_rates(),
    util=model.default_util(),
    settings=model.default_settings()
)

max_patients_all = results_all['Total Patients'].max()
final_patients_all = results_all[results_all['Month'] == 48]['Total Patients'].iloc[0] if len(results_all[results_all['Month'] == 48]) > 0 else 0

total_homes = sum(homes_all.values())
target_all = total_homes * 200  # 200 patients per home target

print(f"Total nursing homes: {total_homes}")
print(f"Target: {total_homes} homes × 200 patients = {target_all:,} patients")
print(f"\n🏁 OUTCOMES:")
print(f"Max patients reached: {max_patients_all:,.0f}")
print(f"Patients at month 48: {final_patients_all:,.0f}")

if max_patients_all >= target_all * 0.9:
    print(f"✅ Successfully reached ~90% of target!")
else:
    print(f"❌ Only reached {max_patients_all/target_all:.1%} of target")