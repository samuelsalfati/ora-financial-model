import model
import pandas as pd

# Test that each state actually grows
settings = model.default_settings()
settings['months'] = 12

print("TESTING INDIVIDUAL STATE GROWTH")
print("=" * 60)

# Test Florida alone
states_fl = {
    "Florida": {"start_month": 1, "initial_patients": 100, "active": True}
}
gpci_fl = {"Florida": 1.05}
homes_fl = {"Florida": 60}

df_fl = model.run_projection(states_fl, gpci_fl, homes_fl, model.default_rates(), model.default_util(), settings)

print("\nFlorida Growth (first 12 months):")
for m in range(1, 13):
    month_data = df_fl[df_fl['Month'] == m]
    if not month_data.empty:
        patients = month_data.iloc[0]['Total Patients']
        revenue = month_data.iloc[0]['Total Revenue']
        print(f"  Month {m:2}: {patients:6.0f} patients, ${revenue:10.0f} revenue")

# Test Virginia alone
states_va = {
    "Virginia": {"start_month": 1, "initial_patients": 100, "active": True}
}
gpci_va = {"Virginia": 1.00}
homes_va = {"Virginia": 100}

df_va = model.run_projection(states_va, gpci_va, homes_va, model.default_rates(), model.default_util(), settings)

print("\nVirginia Growth (first 12 months):")
for m in range(1, 13):
    month_data = df_va[df_va['Month'] == m]
    if not month_data.empty:
        patients = month_data.iloc[0]['Total Patients']
        revenue = month_data.iloc[0]['Total Revenue']
        print(f"  Month {m:2}: {patients:6.0f} patients, ${revenue:10.0f} revenue")

print("\n" + "=" * 60)
print("ISSUE: If both states have same growth logic, they should grow similarly!")